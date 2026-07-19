#!/usr/bin/env python3
"""Record lightweight HTTP health for configured public source inputs."""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 2_000_000


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="reports/source-health.json")
    args = parser.parse_args()
    urls = [line.strip() for line in (ROOT / "assets/sources.txt").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")]
    results = []
    for url in urls:
        row = {"url": url}
        started = time.monotonic()
        try:
            req = Request(url, headers={"User-Agent": "iptv-consolidated-playlist/source-health"})
            with urlopen(req, timeout=30) as response:
                data = response.read(MAX_BYTES)
                row.update({"status": getattr(response, "status", 200), "bytes_sampled": len(data),
                            "content_type": response.headers.get_content_type(),
                            "m3u_entries_sampled": data.count(b"#EXTINF")})
        except Exception as exc:
            row.update({"status": None, "error": f"{type(exc).__name__}: {exc}"})
        row["elapsed_ms"] = round((time.monotonic() - started) * 1000)
        results.append(row)
        print(row)
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "sources": results}
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
