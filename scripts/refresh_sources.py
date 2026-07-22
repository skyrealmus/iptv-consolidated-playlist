#!/usr/bin/env python3
"""Refresh published IPTV URLs and review withheld rows from public catalogs.

This is intentionally conservative: it only replaces a published URL when the
same public catalog that supplied the existing mapping still advertises the
same channel alias and the URL passes ffprobe plus a short FFmpeg decode.  It
never promotes a new channel or a different catalog mapping automatically;
those changes still require the documented identity review.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
ALIASES = ROOT / "assets" / "channel_aliases.txt"
SOURCES = ROOT / "assets" / "sources.txt"
DEFAULT_REPORT = ROOT / "reports" / "daily-refresh.json"
USER_AGENT = "iptv-consolidated-playlist/daily-refresh"
URL_RE = re.compile(r"https?://[^\s,|]+", re.IGNORECASE)
ATTR_RE = re.compile(r"([\w-]+)=(?:\"([^\"]*)\"|'([^']*)')")
QUALITY_RE = re.compile(r"(?:\b(?:hd|sd|fhd|uhd|4k|8k|\d{3,4}p)\b|\[[^\]]*\]|\([^)]*\)|@[^\s,|]+|\*[^\s,|]+)", re.IGNORECASE)


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def load_source_urls(path: Path) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        url = raw.strip()
        if not url or url.startswith("#") or url in seen:
            continue
        seen.add(url)
        result.append(url)
    return result


def normalize_label(value: str, *, strip_quality: bool = False) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    if strip_quality:
        value = QUALITY_RE.sub(" ", value)
    value = re.sub(r"[\u200b\ufeff]", "", value)
    value = re.sub(r"[^\w\u4e00-\u9fff]+", "", value, flags=re.UNICODE)
    return value


def label_variants(value: str) -> set[str]:
    variants = {normalize_label(value), normalize_label(value, strip_quality=True)}
    return {variant for variant in variants if variant}


def load_alias_rows(path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "|" in line:
            fields = [field.strip() for field in line.split("|")]
            terms = [fields[0], fields[1] if len(fields) > 1 else ""]
            if len(fields) > 2:
                terms.extend(part.strip() for part in fields[2].split(","))
        elif "=" in line:
            fields = [field.strip() for field in line.split("=", 1)]
            terms = fields
        else:
            terms = [line]
        rows.append([term for term in terms if term])
    return rows


def load_register(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.startswith("|"):
            continue
        fields = [field.strip() for field in raw.strip().strip("|").split("|")]
        if len(fields) < 10 or not fields[0].isdigit():
            continue
        requested = fields[2].strip("`")
        display = fields[3].strip("`")
        status = fields[7].strip().upper()
        if requested and status in {"PUBLISHED", "WITHHELD", "REQUESTED"}:
            rows.append({"requested": requested, "display": display, "status": status})
    return rows


def aliases_for(requested: str, display: str, rows: list[list[str]]) -> set[str]:
    wanted = label_variants(requested) | label_variants(display)
    terms: set[str] = {requested, display}
    for row in rows:
        row_variants = {variant for term in row for variant in label_variants(term)}
        if wanted & row_variants:
            terms.update(row)
    return {variant for term in terms for variant in label_variants(term)}


def safe_stream_url(url: str) -> bool:
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    return parts.scheme in {"http", "https"} and not parts.username and not parts.password


def redacted_url(url: str) -> str:
    """Keep report provenance useful without copying query tokens into reports."""
    try:
        parts = urlsplit(url)
        path = parts.path or "/"
        return urlunsplit((parts.scheme, parts.netloc, path, "[REDACTED]" if parts.query else "", ""))
    except ValueError:
        return "[invalid-url]"


def redacted_text(value: str) -> str:
    return re.sub(r"https?://[^\s]+", lambda match: redacted_url(match.group(0).rstrip(".,);'\"")), value)


def fingerprint(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def parse_attrs(line: str) -> dict[str, str]:
    return {key: (quoted or bare) for key, quoted, bare in ATTR_RE.findall(line)}


def append_candidate(candidates: list[dict], label: str, url: str, source_index: int) -> None:
    url = url.strip().strip("<>\"'")
    url = url.rstrip("),;\"")
    if not label or not safe_stream_url(url):
        return
    candidates.append({
        "label": label.strip(),
        "url": url,
        "source_index": source_index,
    })


def parse_catalog(text: str, source_index: int) -> list[dict]:
    candidates: list[dict] = []
    pending: tuple[str, dict[str, str]] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#EXTINF"):
            label = line.split(",", 1)[1].strip() if "," in line else ""
            pending = (label, parse_attrs(line))
            continue
        if line.startswith("#"):
            continue
        if pending and safe_stream_url(line):
            label, attrs = pending
            append_candidate(candidates, label or attrs.get("tvg-name", ""), line, source_index)
            pending = None
            continue
        pending = None
        match = URL_RE.search(line)
        if not match:
            continue
        url = match.group(0)
        prefix = line[: match.start()].strip(" \t,|\"")
        suffix = line[match.end() :].strip(" \t,|\"")
        label = prefix or suffix
        append_candidate(candidates, label, url, source_index)
    return candidates


def fetch_catalog(item: tuple[int, str], timeout: int, max_bytes: int) -> dict:
    source_index, url = item
    started = time.monotonic()
    result = {
        "source_index": source_index,
        "source": redacted_url(url),
        "status": None,
        "bytes": 0,
        "candidates": [],
    }
    try:
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=timeout) as response:
            data = response.read(max_bytes)
            result["status"] = getattr(response, "status", 200)
        text = data.decode("utf-8-sig", "replace")
        result["bytes"] = len(data)
        result["candidates"] = parse_catalog(text, source_index)
    except Exception as exc:  # network sources are untrusted and best effort
        result["error"] = f"{type(exc).__name__}: {exc}"
    result["elapsed_ms"] = round((time.monotonic() - started) * 1000)
    return result


def command_output(command: list[str], timeout: int) -> tuple[int, str, str, bool]:
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            check=False,
        )
        return completed.returncode, completed.stdout, completed.stderr, False
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return 124, stdout, stderr, True
    except OSError as exc:
        return 127, "", str(exc), False


def bounded_hls_input(url: str, timeout: int, temp_dir: Path) -> str | None:
    """Materialize a small current HLS window for deterministic local probing."""
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        playlist = response.read(2_000_000).decode("utf-8", "replace")
    if "#EXTM3U" not in playlist:
        return None
    lines = [line.strip() for line in playlist.splitlines() if line.strip()]
    if "#EXT-X-STREAM-INF" in playlist:
        variants: list[str] = []
        for index, line in enumerate(lines[:-1]):
            if line.startswith("#EXT-X-STREAM-INF") and not lines[index + 1].startswith("#"):
                variants.append(urljoin(url, lines[index + 1]))
        if not variants:
            return None
        variant_request = Request(variants[0], headers={"User-Agent": USER_AGENT})
        with urlopen(variant_request, timeout=timeout) as response:
            playlist = response.read(2_000_000).decode("utf-8", "replace")
        url = variants[0]
        lines = [line.strip() for line in playlist.splitlines() if line.strip()]
    segments = [urljoin(url, line) for line in lines if not line.startswith("#")]
    if not segments:
        return None
    output = temp_dir / "window.ts"
    with output.open("wb") as destination:
        for segment in segments[-2:]:
            segment_request = Request(segment, headers={"User-Agent": USER_AGENT})
            with urlopen(segment_request, timeout=timeout) as response:
                remaining = 8_000_000
                while remaining > 0:
                    block = response.read(min(256_000, remaining))
                    if not block:
                        break
                    destination.write(block)
                    remaining -= len(block)
    return str(output)


def probe_candidate(candidate: dict, probe_timeout: int, decode_seconds: int) -> dict:
    url = candidate["url"]
    timeout_us = str(max(1, probe_timeout) * 1_000_000)
    started = time.monotonic()
    result: dict = {
        "url_fingerprint": fingerprint(url),
        "ffprobe_ok": False,
        "ffmpeg_decode_ok": False,
        "elapsed_ms": None,
    }
    try:
        with tempfile.TemporaryDirectory(prefix="iptv-refresh-") as temp_name:
            temp_dir = Path(temp_name)
            local_input = None
            if urlsplit(url).path.lower().endswith((".m3u8", ".m3u")):
                local_input = bounded_hls_input(url, probe_timeout, temp_dir)
            input_url = local_input or url
            ffprobe = [
                "ffprobe", "-v", "error", "-rw_timeout", timeout_us,
                "-analyzeduration", "1000000", "-probesize", "1000000",
                "-select_streams", "v:0", "-show_entries",
                "stream=codec_name,width,height,bit_rate", "-of", "json", input_url,
            ]
            probe_rc, probe_out, probe_err, probe_timed_out = command_output(ffprobe, probe_timeout + 5)
            if probe_rc == 0:
                try:
                    streams = json.loads(probe_out).get("streams", [])
                    if streams:
                        stream = streams[0]
                        result["ffprobe_ok"] = True
                        result["codec"] = stream.get("codec_name")
                        result["resolution"] = (
                            f"{stream['width']}x{stream['height']}"
                            if stream.get("width") and stream.get("height") else None
                        )
                        if stream.get("bit_rate"):
                            result["bit_rate"] = stream["bit_rate"]
                except (ValueError, TypeError, KeyError) as exc:
                    result["probe_error"] = f"invalid ffprobe JSON: {exc}"
            else:
                result["probe_error"] = "ffprobe timeout" if probe_timed_out else (redacted_text(probe_err.strip()[-500:]) or f"exit {probe_rc}")
            if result["ffprobe_ok"]:
                ffmpeg = [
                    "ffmpeg", "-hide_banner", "-loglevel", "error",
                    "-rw_timeout", timeout_us, "-i", input_url, "-map", "0:v:0",
                    "-t", str(max(1, decode_seconds)), "-f", "null", "-",
                ]
                decode_rc, _decode_out, decode_err, decode_timed_out = command_output(ffmpeg, probe_timeout + decode_seconds + 5)
                result["ffmpeg_decode_ok"] = decode_rc == 0
                if not result["ffmpeg_decode_ok"]:
                    result["decode_error"] = "FFmpeg timeout" if decode_timed_out else (redacted_text(decode_err.strip()[-500:]) or f"exit {decode_rc}")
    except Exception as exc:
        result["probe_error"] = redacted_text(f"{type(exc).__name__}: {exc}")
    result["elapsed_ms"] = round((time.monotonic() - started) * 1000)
    return result


def source_index_map(old_sources: list[str], current_sources: list[str]) -> dict[int, int | None]:
    current = {url: index for index, url in enumerate(current_sources)}
    return {index: current.get(url) for index, url in enumerate(old_sources)}


def merged_manifest_sources(old_sources: list[str], current_sources: list[str]) -> list[str]:
    """Use the active list first, retaining removed provenance after it."""
    result = list(current_sources)
    present = set(result)
    for url in old_sources:
        if url not in present:
            result.append(url)
            present.add(url)
    return result


def selected_candidates(entry: dict, catalog: dict, wanted: set[str]) -> list[dict]:
    matches = [candidate for candidate in catalog.get("candidates", []) if label_variants(candidate["label"]) & wanted]
    old_url = entry.get("url")
    matches.sort(key=lambda candidate: (candidate["url"] != old_url, len(candidate["label"]), candidate["url"]))
    return matches


def review_candidates(row: dict[str, str], catalogs: dict[int, dict], wanted: set[str]) -> list[dict]:
    unique: dict[str, dict] = {}
    for catalog in catalogs.values():
        if catalog.get("status") != 200:
            continue
        for candidate in catalog.get("candidates", []):
            if label_variants(candidate["label"]) & wanted:
                unique.setdefault(candidate["url"], candidate)
    return sorted(unique.values(), key=lambda candidate: (len(candidate["label"]), candidate["source_index"], candidate["url"]))


def report_channel(status: str, entry: dict, source_index: int | None, candidates: list[dict], probe: dict | None = None) -> dict:
    result = {
        "status": status,
        "source_index": source_index,
        "candidate_count": len(candidates),
    }
    if candidates:
        result["candidate_labels"] = [candidate["label"] for candidate in candidates[:10]]
    if probe is not None:
        result["probe"] = probe
    return result


def update_stream_speed_report(report: dict) -> None:
    """Add the current bounded probe snapshot without deleting audit evidence."""
    path = ROOT / "reports" / "stream-speed.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {}
    data["tested_at"] = report["checked_at"]
    data["catalog_health"] = {
        "tested": len(report["catalogs"]),
        "http_200": sum(item.get("status") == 200 for item in report["catalogs"]),
        "failed": [
            {"source": redacted_url(item["source"]), "error": item.get("error", "unknown error")}
            for item in report["catalogs"]
            if item.get("status") != 200
        ],
        "refresh_method": "selected manifest source catalogs",
    }
    channels = data.setdefault("channels", {})
    for requested, result in report["channels"].items():
        channels.setdefault(requested, {})["daily_refresh"] = result
    data.setdefault("summary", {})["daily_refresh"] = report["summary"]
    data["daily_refresh"] = {
        "at": report["checked_at"],
        "method": report["method"],
        "summary": report["summary"],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_channel_register(report: dict) -> None:
    """Refresh only the generated summary in the human-maintained register."""
    path = ROOT / "channel.md"
    text = path.read_text(encoding="utf-8")
    snapshot_date = report["checked_at"][:10]
    text = re.sub(r"(?m)^- Snapshot date: \*\*.*?\*\*$", f"- Snapshot date: **{snapshot_date}**", text, count=1)
    summary = report["summary"]
    block = "\n".join([
        "<!-- DAILY_REFRESH_STATUS:START -->",
        f"- Last automated source refresh: **{report['checked_at']}**",
        f"- Mapped channels checked: **{summary['checked']}**; verified unchanged: **{summary['verified_unchanged']}**; URLs refreshed: **{summary['url_refreshed']}**",
        f"- Register rows checked: **{summary['register_checked']}**; withheld rows reviewed: **{summary['withheld_checked']}**; identity-review candidates: **{summary['withheld_identity_review']}**; withheld probe failures: **{summary['withheld_probe_failed']}**",
        f"- Safe failures retained without replacement: probe failures **{summary['probe_failed']}**, unavailable catalogs **{summary['catalog_unavailable']}**, no same-catalog alias match **{summary['no_same_catalog_match']}**, withheld no-match **{summary['withheld_no_match']}**",
        "- Publication policy: same-source alias match plus FFprobe and short FFmpeg decode; cross-catalog replacements remain manual identity review.",
        "<!-- DAILY_REFRESH_STATUS:END -->",
    ])
    marker = re.compile(r"<!-- DAILY_REFRESH_STATUS:START -->.*?<!-- DAILY_REFRESH_STATUS:END -->", re.DOTALL)
    if marker.search(text):
        text = marker.sub(block, text, count=1)
    else:
        anchor = f"- Snapshot date: **{snapshot_date}**"
        if anchor not in text:
            raise RuntimeError("channel.md snapshot-date anchor not found")
        text = text.replace(anchor, anchor + "\n" + block, 1)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="probe and report without changing manifest.json")
    parser.add_argument("--only", action="append", default=[], help="refresh only this requested channel; repeatable")
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--catalog-timeout", type=int, default=30)
    parser.add_argument("--probe-timeout", type=int, default=20)
    parser.add_argument("--decode-seconds", type=int, default=3)
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    old_sources = list(manifest.get("sources", []))
    current_sources = load_source_urls(SOURCES)
    manifest_sources = merged_manifest_sources(old_sources, current_sources)
    active_index = {url: index for index, url in enumerate(current_sources)}
    manifest_index = {url: index for index, url in enumerate(manifest_sources)}
    active_map = {index: active_index.get(url) for index, url in enumerate(old_sources)}
    manifest_map = {index: manifest_index.get(url) for index, url in enumerate(old_sources)}
    alias_rows = load_alias_rows(ALIASES)
    register_rows = load_register(ROOT / "channel.md")
    metadata = json.loads((ROOT / "assets" / "channel_metadata.json").read_text(encoding="utf-8"))["channels"]
    only = set(args.only)
    register_by_requested = {row["requested"]: row for row in register_rows}
    if only and not only.issubset(register_by_requested):
        missing = sorted(only - set(register_by_requested))
        raise SystemExit(f"unknown --only channel(s): {', '.join(missing)}")
    entries = [entry for entry in manifest["entries"] if not only or entry["requested"] in only]
    review_rows = [
        row for row in register_rows
        if row["status"] in {"WITHHELD", "REQUESTED"} and (not only or row["requested"] in only)
    ]
    original_entry_indices = {entry["requested"]: entry["source_index"] for entry in manifest["entries"]}

    needed_old_indices = sorted({entry["source_index"] for entry in entries})
    fetch_items: dict[int, tuple[int, str]] = {}
    if review_rows:
        fetch_items = {index: (index, url) for index, url in enumerate(current_sources)}
    else:
        for index in needed_old_indices:
            current_index = active_map.get(index)
            if current_index is not None:
                fetch_items[current_index] = (current_index, current_sources[current_index])
    catalogs: dict[int, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.max_workers)) as pool:
        futures = {
            pool.submit(fetch_catalog, item, args.catalog_timeout, 12_000_000): item[0]
            for item in fetch_items.values()
        }
        for future in concurrent.futures.as_completed(futures):
            catalog = future.result()
            catalogs[catalog["source_index"]] = catalog

    work: list[tuple[dict, list[dict]]] = []
    channel_results: dict[str, dict] = {}
    for entry in entries:
        requested = entry["requested"]
        old_index = entry["source_index"]
        current_index = active_map.get(old_index)
        if current_index is None:
            channel_results[requested] = report_channel("source_not_active", entry, None, [])
            continue
        catalog = catalogs.get(current_index)
        if not catalog or catalog.get("status") != 200:
            channel_results[requested] = report_channel("catalog_unavailable", entry, current_index, [])
            continue
        display = metadata.get(requested, {}).get("display_name", requested)
        wanted = aliases_for(requested, display, alias_rows)
        matches = selected_candidates(entry, catalog, wanted)
        if not matches:
            channel_results[requested] = report_channel("no_same_catalog_match", entry, current_index, [])
            continue
        work.append((entry, matches[:3]))

    review_work: list[tuple[dict[str, str], list[dict]]] = []
    for row in review_rows:
        wanted = aliases_for(row["requested"], row["display"], alias_rows)
        matches = review_candidates(row, catalogs, wanted)
        if not matches:
            channel_results[row["requested"]] = report_channel("withheld_no_match", row, None, [])
            continue
        review_work.append((row, matches[:3]))

    probe_jobs: list[tuple[str, dict]] = []
    for entry, matches in work:
        for candidate in matches:
            probe_jobs.append((entry["requested"], candidate))
    for row, matches in review_work:
        for candidate in matches:
            probe_jobs.append((row["requested"], candidate))
    probes: dict[tuple[str, str], dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.max_workers)) as pool:
        futures = {
            pool.submit(probe_candidate, candidate, args.probe_timeout, args.decode_seconds): (requested, candidate["url"])
            for requested, candidate in probe_jobs
        }
        for future in concurrent.futures.as_completed(futures):
            key = futures[future]
            try:
                probes[key] = future.result()
            except Exception as exc:  # keep one bad URL from aborting all channels
                probes[key] = {"ffprobe_ok": False, "ffmpeg_decode_ok": False, "probe_error": redacted_text(f"{type(exc).__name__}: {exc}")}

    changed_entries = 0
    for entry in entries:
        requested = entry["requested"]
        if requested in channel_results:
            continue
        matches = next(matches for item, matches in work if item is entry)
        accepted: tuple[dict, dict] | None = None
        for candidate in matches:
            probe = probes.get((requested, candidate["url"]), {})
            if probe.get("ffprobe_ok") and probe.get("ffmpeg_decode_ok"):
                accepted = (candidate, probe)
                break
        current_index = active_map[entry["source_index"]]
        if accepted is None:
            channel_results[requested] = report_channel("probe_failed", entry, current_index, matches, probes.get((requested, matches[0]["url"])))
            continue
        candidate, probe = accepted
        url_changed = entry.get("url") != candidate["url"]
        index_changed = entry.get("source_index") != current_index
        if url_changed and not args.dry_run:
            entry["url"] = candidate["url"]
            entry["delay"] = None
            entry["speed"] = None
            entry["resolution"] = probe.get("resolution")
        if index_changed and not args.dry_run:
            entry["source_index"] = manifest_map[entry["source_index"]]
        if url_changed or index_changed:
            changed_entries += 1
        status = "url_refreshed" if url_changed else "verified_unchanged"
        channel_results[requested] = report_channel(status, entry, current_index, matches, probe)

    for row, matches in review_work:
        accepted: tuple[dict, dict] | None = None
        for candidate in matches:
            probe = probes.get((row["requested"], candidate["url"]), {})
            if probe.get("ffprobe_ok") and probe.get("ffmpeg_decode_ok"):
                accepted = (candidate, probe)
                break
        if accepted is None:
            channel_results[row["requested"]] = report_channel(
                "withheld_probe_failed", row, None, matches, probes.get((row["requested"], matches[0]["url"]))
            )
        else:
            candidate, probe = accepted
            channel_results[row["requested"]] = report_channel(
                "withheld_identity_review", row, candidate.get("source_index"), matches, probe
            )

    catalog_report = []
    for index in sorted(catalogs):
        catalog = catalogs[index]
        catalog_report.append({
            "source_index": index,
            "source": redacted_url(catalog["source"]),
            "status": catalog.get("status"),
            "bytes": catalog.get("bytes", 0),
            "candidate_count": len(catalog.get("candidates", [])),
            "elapsed_ms": catalog.get("elapsed_ms"),
            **({"error": catalog["error"]} if catalog.get("error") else {}),
        })
    published_results = [channel_results[entry["requested"]] for entry in entries if entry["requested"] in channel_results]
    withheld_results = [channel_results[row["requested"]] for row in review_rows if row["requested"] in channel_results]
    summary = {
        "checked": len(entries),
        "register_checked": len(entries) + len(review_rows),
        "withheld_checked": len(review_rows),
        "verified_unchanged": sum(item["status"] == "verified_unchanged" for item in published_results),
        "url_refreshed": sum(item["status"] == "url_refreshed" for item in published_results),
        "probe_failed": sum(item["status"] == "probe_failed" for item in published_results),
        "no_same_catalog_match": sum(item["status"] == "no_same_catalog_match" for item in published_results),
        "catalog_unavailable": sum(item["status"] == "catalog_unavailable" for item in published_results),
        "source_not_active": sum(item["status"] == "source_not_active" for item in published_results),
        "withheld_no_match": sum(item["status"] == "withheld_no_match" for item in withheld_results),
        "withheld_probe_failed": sum(item["status"] == "withheld_probe_failed" for item in withheld_results),
        "withheld_identity_review": sum(item["status"] == "withheld_identity_review" for item in withheld_results),
    }
    report = {
        "checked_at": now_utc().isoformat(),
        "method": "published same-source refresh + full-register withheld discovery + bounded ffprobe/FFmpeg; no automatic cross-catalog publication",
        "summary": summary,
        "catalogs": catalog_report,
        "channels": channel_results,
    }
    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = ROOT / report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not args.dry_run:
        update_stream_speed_report(report)
        update_channel_register(report)
        for entry in manifest["entries"]:
            target_index = manifest_map.get(original_entry_indices[entry["requested"]])
            if target_index is not None:
                entry["source_index"] = target_index
        manifest["sources"] = manifest_sources
        if changed_entries:
            manifest["generated_at"] = now_utc().date().isoformat()
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"dry_run": args.dry_run, "summary": summary, "report": str(report_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
