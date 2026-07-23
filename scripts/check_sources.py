#!/usr/bin/env python3
"""Record lightweight HTTP health and quality classes for public source inputs."""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 2_000_000
MAX_HIGH_LATENCY_MS = 5_000
PLAYLIST_CONTENT_TYPES = {
    "audio/x-mpegurl",
    "application/vnd.apple.mpegurl",
    "application/x-mpegurl",
    "text/plain",
}


def classify_source(row: dict) -> tuple[str, list[str]]:
    """Classify catalog transport/format quality, not individual stream quality."""
    if row.get("status") != 200:
        return "FAILED", ["source transport failed"]

    reasons: list[str] = []
    if row.get("m3u_entries_sampled", 0) <= 0:
        reasons.append("no #EXTINF entries in sampled content")
    if not row.get("url", "").startswith("https://"):
        reasons.append("source is not HTTPS")
    if row.get("elapsed_ms", 0) > MAX_HIGH_LATENCY_MS:
        reasons.append(f"catalog response exceeded {MAX_HIGH_LATENCY_MS} ms")
    if row.get("content_type") not in PLAYLIST_CONTENT_TYPES:
        reasons.append(f"unexpected content type: {row.get('content_type')}")
    return ("LOW" if reasons else "HIGH"), reasons


def resolve_output(value: str) -> Path:
    output = Path(value)
    return output if output.is_absolute() else ROOT / output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="reports/source-health.json")
    parser.add_argument("--quality-output", default="reports/source-quality.json")
    args = parser.parse_args()

    urls = [
        line.strip()
        for line in (ROOT / "assets/sources.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    results = []
    for url in urls:
        row: dict = {"url": url}
        started = time.monotonic()
        try:
            req = Request(url, headers={"User-Agent": "iptv-consolidated-playlist/source-health"})
            with urlopen(req, timeout=30) as response:
                data = response.read(MAX_BYTES)
                row.update(
                    {
                        "status": getattr(response, "status", 200),
                        "bytes_sampled": len(data),
                        "content_type": response.headers.get_content_type(),
                        "m3u_entries_sampled": data.count(b"#EXTINF"),
                    }
                )
        except Exception as exc:
            row.update({"status": None, "error": f"{type(exc).__name__}: {exc}"})
        row["elapsed_ms"] = round((time.monotonic() - started) * 1000)
        quality, reasons = classify_source(row)
        row["quality"] = quality
        if reasons:
            row["quality_reasons"] = reasons
        results.append(row)
        print(row)

    checked_at = datetime.now(timezone.utc).isoformat()
    report = {
        "checked_at": checked_at,
        "quality_scope": "catalog reachability and sampled playlist shape; not individual stream playback quality",
        "quality_criteria": {
            "HIGH": [
                "HTTP status 200",
                "at least one sampled #EXTINF entry",
                "HTTPS URL",
                f"response time <= {MAX_HIGH_LATENCY_MS} ms",
                "playlist-compatible content type",
            ],
            "LOW": "HTTP 200 but one or more HIGH criteria failed; retained for possible channel discovery/recheck",
            "FAILED": "source fetch did not return HTTP 200; excluded from active sources.txt",
        },
        "sources": results,
    }
    output = resolve_output(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    grouped = {"HIGH": [], "LOW": [], "FAILED": []}
    for row in results:
        grouped[row["quality"]].append(row)
    quality_report = {
        "checked_at": checked_at,
        "source_health_report": str(output.relative_to(ROOT)) if output.is_relative_to(ROOT) else str(output),
        "quality_scope": report["quality_scope"],
        "quality_criteria": report["quality_criteria"],
        "counts": {key: len(value) for key, value in grouped.items()},
        "high_quality": grouped["HIGH"],
        "low_quality": grouped["LOW"],
        "failed": grouped["FAILED"],
    }
    quality_output = resolve_output(args.quality_output)
    quality_output.parent.mkdir(parents=True, exist_ok=True)
    quality_output.write_text(json.dumps(quality_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
