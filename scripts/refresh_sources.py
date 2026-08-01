#!/usr/bin/env python3
"""Refresh published IPTV URLs and review withheld rows from public catalogs.

This is intentionally conservative: it only replaces a published URL when the
same public catalog that supplied the existing mapping still advertises the
same channel alias and the URL passes a bounded VLC playback profile.  It
never promotes a new channel or a different catalog mapping automatically;
those changes still require the documented identity review.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import re
import shutil
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
FRAME_WIDTH = 160
FRAME_HEIGHT = 90
FRAME_BYTES = FRAME_WIDTH * FRAME_HEIGHT * 3
BLACK_LUMA_MAX = 12
BLACK_PIXEL_MAX = 16
BLACK_PIXEL_FRACTION = 0.985
BLACK_FRAME_FRACTION = 0.90
BLANK_LUMA_STDDEV_MAX = 2.5
BLANK_FRAME_FRACTION = 0.90
STALE_FRAME_DIFF_MAX = 1.5
STALE_PAIR_FRACTION = 0.90
MIN_CONTENT_FRAMES = 3


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
    """Read the channel register by column name, not by stale column offsets."""
    rows: list[dict[str, str]] = []
    header: dict[str, int] | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.startswith("|"):
            continue
        fields = [field.strip() for field in raw.strip().strip("|").split("|")]
        if fields and fields[0] == "#":
            header = {name: index for index, name in enumerate(fields)}
            continue
        if header is None or not fields or not fields[0].isdigit():
            continue
        required = {"Requested", "Display", "Status"}
        if not required.issubset(header) or len(fields) <= max(header.values()):
            continue
        requested = fields[header["Requested"]].strip("`")
        display = fields[header["Display"]].strip("`")
        status = fields[header["Status"]].upper()
        if requested and status in {"PUBLISHED", "WITHHELD", "REQUESTED", "IMPORTED"}:
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


def load_playlist_streams(path: Path) -> dict[str, dict[str, str]]:
    """Read the generated playlist so the daily check tests published URLs."""
    lines = path.read_text(encoding="utf-8").splitlines()
    streams: dict[str, dict[str, str]] = {}
    for index, line in enumerate(lines):
        if not line.startswith("#EXTINF:"):
            continue
        if index + 1 >= len(lines):
            raise ValueError(f"{path.name}: missing URL after line {index + 1}")
        attrs = parse_attrs(line)
        requested = attrs.get("tvg-id", "").strip()
        url = lines[index + 1].strip()
        if not requested or not safe_stream_url(url):
            raise ValueError(f"{path.name}: invalid stream entry after line {index + 1}")
        if requested in streams:
            raise ValueError(f"{path.name}: duplicate tvg-id {requested}")
        streams[requested] = {"url": url, "label": attrs.get("tvg-name", requested)}
    if not streams:
        raise ValueError(f"{path.name}: no published stream entries")
    return streams


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


def vlc_binary() -> str | None:
    return shutil.which("cvlc") or shutil.which("vlc")


def parse_vlc_profile(output: str) -> dict[str, str | None]:
    result: dict[str, str | None] = {"codec": None, "resolution": None}
    codec = re.search(r"creating video transcoding from fcc=`([^']+)'", output)
    if codec:
        result["codec"] = codec.group(1)
    else:
        codec = re.search(r"codec \(([^)]+)\) started", output)
        if codec:
            result["codec"] = codec.group(1)
    resolution = re.search(r"source (\d+)x(\d+), destination", output)
    if resolution:
        result["resolution"] = f"{resolution.group(1)}x{resolution.group(2)}"
    return result


def analyze_rgb_frames(path: Path) -> dict:
    """Reject decoded video that is persistently black, blank, or unchanged."""
    raw = path.read_bytes()
    frame_count = len(raw) // FRAME_BYTES
    result = {
        "content_sample_resolution": f"{FRAME_WIDTH}x{FRAME_HEIGHT}",
        "content_sampled_frames": frame_count,
        "black_frame_fraction": 0.0,
        "blank_frame_fraction": 0.0,
        "stale_pair_fraction": 0.0,
        "video_content_ok": False,
    }
    if frame_count < MIN_CONTENT_FRAMES:
        result["content_failure"] = "insufficient decoded video frames"
        return result

    black_frames = 0
    blank_frames = 0
    stale_pairs = 0
    previous: bytes | None = None
    comparisons = 0
    # A 160x90 sample keeps the analysis bounded even for 1080p/4K sources.
    for frame_index in range(frame_count):
        start = frame_index * FRAME_BYTES
        frame = raw[start : start + FRAME_BYTES]
        sampled_pixels = 0
        luma_sum = 0
        luma_squared_sum = 0
        black_pixels = 0
        for pixel in range(0, FRAME_BYTES, 9):
            red, green, blue = frame[pixel : pixel + 3]
            luma = (54 * red + 183 * green + 19 * blue) >> 8
            sampled_pixels += 1
            luma_sum += luma
            luma_squared_sum += luma * luma
            if luma <= BLACK_LUMA_MAX and red <= BLACK_PIXEL_MAX and green <= BLACK_PIXEL_MAX and blue <= BLACK_PIXEL_MAX:
                black_pixels += 1
        mean_luma = luma_sum / sampled_pixels
        variance = max(0.0, (luma_squared_sum / sampled_pixels) - (mean_luma * mean_luma))
        luma_stddev = variance ** 0.5
        if black_pixels / sampled_pixels >= BLACK_PIXEL_FRACTION and mean_luma <= BLACK_LUMA_MAX:
            black_frames += 1
        if luma_stddev <= BLANK_LUMA_STDDEV_MAX:
            blank_frames += 1
        if previous is not None:
            comparisons += 1
            difference = sum(abs(frame[index] - previous[index]) for index in range(0, FRAME_BYTES, 9)) / (FRAME_BYTES / 9)
            if difference <= STALE_FRAME_DIFF_MAX:
                stale_pairs += 1
        previous = frame

    result["black_frame_fraction"] = round(black_frames / frame_count, 3)
    result["blank_frame_fraction"] = round(blank_frames / frame_count, 3)
    result["stale_pair_fraction"] = round(stale_pairs / comparisons, 3) if comparisons else 0.0
    if result["black_frame_fraction"] >= BLACK_FRAME_FRACTION:
        result["content_failure"] = "black video detected"
    elif result["blank_frame_fraction"] >= BLANK_FRAME_FRACTION:
        result["content_failure"] = "blank/uniform video detected"
    elif comparisons >= MIN_CONTENT_FRAMES - 1 and result["stale_pair_fraction"] >= STALE_PAIR_FRACTION:
        result["content_failure"] = "stale/unchanging video detected"
    else:
        result["video_content_ok"] = True
    return result


def probe_candidate(candidate: dict, probe_timeout: int, decode_seconds: int) -> dict:
    url = candidate["url"]
    started = time.monotonic()
    result: dict = {
        "vlc_playback_ok": False,
        "elapsed_ms": None,
    }
    binary = vlc_binary()
    if not binary:
        result["probe_error"] = "VLC executable not found (tried cvlc and vlc)"
        result["elapsed_ms"] = round((time.monotonic() - started) * 1000)
        return result
    try:
        with tempfile.TemporaryDirectory(prefix="iptv-refresh-") as temp_name:
            temp_dir = Path(temp_name)
            local_input = None
            if urlsplit(url).path.lower().endswith((".m3u8", ".m3u")):
                local_input = bounded_hls_input(url, probe_timeout, temp_dir)
            input_url = local_input or url
            output = temp_dir / "vlc-frames.rgb"
            sout = (
                f"#transcode{{vcodec=RV24,acodec=none,width={FRAME_WIDTH}}}:"
                f"std{{access=file,mux=raw,dst={output}}}"
            )
            vlc = [
                binary, "-vv", "--intf", "dummy", "--play-and-exit",
                f"--run-time={max(1, decode_seconds)}",
                f"--network-caching={max(250, probe_timeout * 1000 // 2)}",
                "--no-audio", "--no-video-title-show", "--sout", sout, input_url,
            ]
            return_code, stdout, stderr, timed_out = command_output(
                vlc, probe_timeout + decode_seconds + 8
            )
            combined = f"{stdout}\n{stderr}"
            profile = parse_vlc_profile(combined)
            content = analyze_rgb_frames(output) if output.is_file() and output.stat().st_size > 0 else {
                "content_sample_resolution": f"{FRAME_WIDTH}x{FRAME_HEIGHT}",
                "content_sampled_frames": 0,
                "black_frame_fraction": 0.0,
                "blank_frame_fraction": 0.0,
                "stale_pair_fraction": 0.0,
                "video_content_ok": False,
                "content_failure": "no decoded video frames",
            }
            result.update({
                "vlc_binary": Path(binary).name,
                "vlc_output_bytes": output.stat().st_size if output.is_file() else 0,
                "codec": profile["codec"],
                "resolution": profile["resolution"],
                **content,
                "vlc_playback_ok": return_code == 0 and bool(content.get("video_content_ok")),
            })
            if not result["vlc_playback_ok"]:
                if timed_out:
                    result["probe_error"] = "VLC playback timeout"
                elif return_code != 0:
                    result["probe_error"] = redacted_text(stderr.strip()[-500:]) or f"VLC exit {return_code}"
                elif content.get("content_failure"):
                    result["probe_error"] = str(content["content_failure"])
                else:
                    result["probe_error"] = "VLC produced no playable output"
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


def report_channel(
    status: str,
    entry: dict,
    source_index: int | None,
    candidates: list[dict],
    probe: dict | None = None,
    replacement_probe: dict | None = None,
) -> dict:
    result = {
        "status": status,
        "source_index": source_index,
        "candidate_count": len(candidates),
    }
    if candidates:
        result["candidate_labels"] = [candidate["label"] for candidate in candidates[:10]]
    if probe is not None:
        result["probe"] = probe
    if replacement_probe is not None:
        result["replacement_probe"] = replacement_probe
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
        "refresh_method": "active source catalogs searched only after a published playlist URL failed",
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


WITHHELD_REFRESH_STATUSES = {
    "withheld_no_match",
    "withheld_probe_failed",
    "withheld_identity_review",
}
REGISTER_ROW_RE = re.compile(
    r"^(?P<prefix>\|\s*\d+\s*\|\s*`(?P<requested>[^`]+)`\s*\|\s*`[^`]*`\s*\|\s*)"
    r"(?P<status>PUBLISHED|WITHHELD|REQUESTED|IMPORTED)"
    r"(?P<suffix>\s*\|.*)$",
    re.MULTILINE,
)


def update_channel_register(report: dict, manifest: dict) -> None:
    """Refresh generated evidence and reconcile table statuses with publication state."""
    path = ROOT / "channel.md"
    text = path.read_text(encoding="utf-8")
    snapshot_date = report["checked_at"][:10]
    text = re.sub(r"(?m)^- Snapshot date: \*\*.*?\*\*$", f"- Snapshot date: **{snapshot_date}**", text, count=1)

    published = {entry["requested"] for entry in manifest.get("entries", [])}
    status_updates: dict[str, str] = {}
    for requested, result in report.get("channels", {}).items():
        if requested in published:
            status_updates[requested] = "PUBLISHED"
        elif result.get("status") in WITHHELD_REFRESH_STATUSES:
            status_updates[requested] = "WITHHELD"

    updated_rows = 0

    def replace_register_status(match: re.Match[str]) -> str:
        nonlocal updated_rows
        requested = match.group("requested")
        status = status_updates.get(requested)
        if status is None or status == match.group("status"):
            return match.group(0)
        updated_rows += 1
        return f"{match.group('prefix')}{status}{match.group('suffix')}"

    text = REGISTER_ROW_RE.sub(replace_register_status, text)
    if set(status_updates) - {match.group("requested") for match in REGISTER_ROW_RE.finditer(text)}:
        missing = sorted(set(status_updates) - {match.group("requested") for match in REGISTER_ROW_RE.finditer(text)})
        raise RuntimeError(f"channel.md register rows missing: {', '.join(missing)}")

    summary = report["summary"]
    block = "\n".join([
        "<!-- DAILY_REFRESH_STATUS:START -->",
        f"- Last automated source refresh: **{report['checked_at']}**",
        f"- Playlist URLs checked: **{summary['playlist_checked']}**; accessible: **{summary['playlist_accessible']}**; inaccessible: **{summary['playlist_inaccessible']}**",
        f"- Content failures: black **{summary['black_video']}**, blank/uniform **{summary['blank_video']}**, stale/unchanging **{summary['stale_video']}**, no decoded video **{summary['no_decoded_video']}**",
        f"- Replacement search: **{summary['replacement_searched']}** failed URLs; candidates found **{summary['replacement_candidates']}**; URLs refreshed **{summary['url_refreshed']}**",
        f"- Register rows checked: **{summary['register_checked']}**; withheld rows reviewed: **{summary['withheld_checked']}**; identity-review candidates: **{summary['withheld_identity_review']}**; withheld probe failures: **{summary['withheld_probe_failed']}**",
        f"- Safe failures retained without replacement: no replacement **{summary['replacement_no_match']}**, replacement probe failures **{summary['replacement_probe_failed']}**, unavailable catalogs **{summary['catalog_unavailable']}**, source not active **{summary['source_not_active']}**",
        f"- Table statuses updated: **{updated_rows}**; `PUBLISHED` means present in the generated playlist, while reviewed non-published requests are `WITHHELD`.",
        "- Publication policy: every published playlist URL is VLC-checked first; only exact normalized active-catalog matches that also pass VLC may replace an inaccessible URL.",
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

    playlist_streams = load_playlist_streams(ROOT / "playlist.m3u")
    channel_results: dict[str, dict] = {}
    playlist_check_entries: list[tuple[dict, dict]] = []
    failed_entries: list[tuple[dict, dict]] = []
    for entry in entries:
        requested = entry["requested"]
        stream = playlist_streams.get(requested)
        if stream is None:
            failed_entries.append((entry, {"vlc_playback_ok": False, "probe_error": "playlist URL missing"}))
            continue
        playlist_check_entries.append((entry, {
            "label": stream["label"],
            "url": stream["url"],
            "source_index": entry.get("source_index"),
        }))

    preflight_probes: dict[str, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.max_workers)) as pool:
        futures = {
            pool.submit(probe_candidate, candidate, args.probe_timeout, args.decode_seconds): candidate["url"]
            for _entry, candidate in playlist_check_entries
        }
        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            try:
                preflight_probes[url] = future.result()
            except Exception as exc:  # keep one bad URL from aborting all channels
                preflight_probes[url] = {
                    "vlc_playback_ok": False,
                    "probe_error": redacted_text(f"{type(exc).__name__}: {exc}"),
                }

    playlist_accessible = 0
    for entry, candidate in playlist_check_entries:
        requested = entry["requested"]
        probe = preflight_probes.get(candidate["url"], {"vlc_playback_ok": False, "probe_error": "probe result missing"})
        if probe.get("vlc_playback_ok"):
            playlist_accessible += 1
            channel_results[requested] = report_channel(
                "verified_unchanged", entry, entry.get("source_index"), [candidate], probe
            )
        else:
            failed_entries.append((entry, probe))

    fetch_items: dict[int, tuple[int, str]] = {}
    if failed_entries or review_rows:
        fetch_items = {index: (index, url) for index, url in enumerate(current_sources)}
    catalogs: dict[int, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.max_workers)) as pool:
        futures = {
            pool.submit(fetch_catalog, item, args.catalog_timeout, 12_000_000): item[0]
            for item in fetch_items.values()
        }
        for future in concurrent.futures.as_completed(futures):
            catalog = future.result()
            catalogs[catalog["source_index"]] = catalog

    replacement_work: list[tuple[dict, dict, list[dict]]] = []
    for entry, initial_probe in failed_entries:
        requested = entry["requested"]
        display = metadata.get(requested, {}).get("display_name", requested)
        wanted = aliases_for(requested, display, alias_rows)
        available_catalogs = {index: catalog for index, catalog in catalogs.items() if catalog.get("status") == 200}
        if not available_catalogs:
            channel_results[requested] = report_channel(
                "catalog_unavailable", entry, entry.get("source_index"), [], initial_probe
            )
            continue
        matches = review_candidates(entry, available_catalogs, wanted)
        current_url = entry.get("url")
        matches = [candidate for candidate in matches if candidate["url"] != current_url]
        if not matches:
            channel_results[requested] = report_channel(
                "replacement_no_match", entry, entry.get("source_index"), [], initial_probe
            )
            continue
        replacement_work.append((entry, initial_probe, matches[:5]))

    review_work: list[tuple[dict[str, str], list[dict]]] = []
    for row in review_rows:
        wanted = aliases_for(row["requested"], row["display"], alias_rows)
        matches = review_candidates(row, catalogs, wanted)
        if not matches:
            channel_results[row["requested"]] = report_channel("withheld_no_match", row, None, [])
            continue
        review_work.append((row, matches[:5]))

    probe_jobs: dict[str, dict] = {}
    for _entry, _initial_probe, matches in replacement_work:
        for candidate in matches:
            probe_jobs.setdefault(candidate["url"], candidate)
    for _row, matches in review_work:
        for candidate in matches:
            probe_jobs.setdefault(candidate["url"], candidate)
    replacement_probes: dict[str, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.max_workers)) as pool:
        futures = {
            pool.submit(probe_candidate, candidate, args.probe_timeout, args.decode_seconds): url
            for url, candidate in probe_jobs.items()
        }
        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            try:
                replacement_probes[url] = future.result()
            except Exception as exc:  # keep one bad URL from aborting all channels
                replacement_probes[url] = {
                    "vlc_playback_ok": False,
                    "probe_error": redacted_text(f"{type(exc).__name__}: {exc}"),
                }

    changed_entries = 0
    for entry, initial_probe, matches in replacement_work:
        requested = entry["requested"]
        accepted: tuple[dict, dict] | None = None
        for candidate in matches:
            probe = replacement_probes.get(candidate["url"], {})
            if probe.get("vlc_playback_ok"):
                accepted = (candidate, probe)
                break
        if accepted is None:
            first_probe = replacement_probes.get(matches[0]["url"], {})
            channel_results[requested] = report_channel(
                "replacement_probe_failed", entry, entry.get("source_index"), matches, initial_probe, first_probe
            )
            continue
        candidate, replacement_probe = accepted
        source_url = current_sources[candidate["source_index"]]
        replacement_source_index = manifest_index[source_url]
        if not args.dry_run:
            entry["url"] = candidate["url"]
            entry["source_index"] = replacement_source_index
            entry["delay"] = None
            entry["speed"] = None
            entry["resolution"] = replacement_probe.get("resolution")
            entry["accepted"] = False
            entry["verification_status"] = "daily_active_catalog_vlc_playback_verified_not_identity_verified"
            entry["playback_profile"] = {
                "method": "bounded VLC playback profile",
                **replacement_probe,
                "source_inventory": "assets/sources.txt",
            }
        changed_entries += 1
        channel_results[requested] = report_channel(
            "url_refreshed", entry, replacement_source_index, matches, initial_probe, replacement_probe
        )

    for row, matches in review_work:
        accepted: tuple[dict, dict] | None = None
        for candidate in matches:
            probe = replacement_probes.get(candidate["url"], {})
            if probe.get("vlc_playback_ok"):
                accepted = (candidate, probe)
                break
        if accepted is None:
            channel_results[row["requested"]] = report_channel(
                "withheld_probe_failed", row, None, matches, replacement_probes.get(matches[0]["url"])
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
    replacement_candidate_count = sum(
        channel_results[entry["requested"]].get("candidate_count", 0)
        for entry, _probe in failed_entries
        if entry["requested"] in channel_results
    )
    summary = {
        "checked": len(entries),
        "playlist_checked": len(entries),
        "playlist_accessible": playlist_accessible,
        "playlist_inaccessible": len(failed_entries),
        "replacement_searched": len(failed_entries),
        "replacement_candidates": replacement_candidate_count,
        "black_video": sum(item.get("probe", {}).get("content_failure") == "black video detected" for item in published_results),
        "blank_video": sum(item.get("probe", {}).get("content_failure") == "blank/uniform video detected" for item in published_results),
        "stale_video": sum(item.get("probe", {}).get("content_failure") == "stale/unchanging video detected" for item in published_results),
        "no_decoded_video": sum(item.get("probe", {}).get("content_failure") == "no decoded video frames" for item in published_results),
        "register_checked": len(register_rows),
        "withheld_checked": len(review_rows),
        "verified_unchanged": sum(item["status"] == "verified_unchanged" for item in published_results),
        "url_refreshed": sum(item["status"] == "url_refreshed" for item in published_results),
        "probe_failed": sum(item["status"] == "replacement_probe_failed" for item in published_results),
        "replacement_probe_failed": sum(item["status"] == "replacement_probe_failed" for item in published_results),
        "replacement_no_match": sum(item["status"] == "replacement_no_match" for item in published_results),
        "no_same_catalog_match": 0,
        "catalog_unavailable": sum(item["status"] == "catalog_unavailable" for item in published_results),
        "source_not_active": 0,
        "withheld_no_match": sum(item["status"] == "withheld_no_match" for item in withheld_results),
        "withheld_probe_failed": sum(item["status"] == "withheld_probe_failed" for item in withheld_results),
        "withheld_identity_review": sum(item["status"] == "withheld_identity_review" for item in withheld_results),
    }
    report = {
        "checked_at": now_utc().isoformat(),
        "method": "full published playlist VLC preflight with raw-RGB black/blank/stale content gate; failed URLs searched against active assets/sources.txt catalogs; exact normalized matches only",
        "content_gate": {
            "method": "VLC-decoded raw RGB temporal sample",
            "sample_resolution": f"{FRAME_WIDTH}x{FRAME_HEIGHT}",
            "decode_seconds": args.decode_seconds,
            "minimum_frames": MIN_CONTENT_FRAMES,
            "black": {
                "pixel_luma_max": BLACK_LUMA_MAX,
                "pixel_fraction": BLACK_PIXEL_FRACTION,
                "frame_fraction": BLACK_FRAME_FRACTION,
            },
            "blank_uniform": {
                "luma_stddev_max": BLANK_LUMA_STDDEV_MAX,
                "frame_fraction": BLANK_FRAME_FRACTION,
            },
            "stale": {
                "mean_rgb_difference_max": STALE_FRAME_DIFF_MAX,
                "pair_fraction": STALE_PAIR_FRACTION,
            },
        },
        "summary": summary,
        "playlist_check": {
            "checked": len(entries),
            "accessible": playlist_accessible,
            "inaccessible": len(failed_entries),
            "replacement_searched": len(failed_entries),
            "urls_refreshed": summary["url_refreshed"],
        },
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
        update_channel_register(report, manifest)
        for entry in manifest["entries"]:
            result = channel_results.get(entry["requested"], {})
            if result.get("status") == "url_refreshed":
                continue
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
