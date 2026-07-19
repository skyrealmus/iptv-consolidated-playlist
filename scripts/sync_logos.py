#!/usr/bin/env python3
"""Synchronize missing curated logos from manifest provenance URLs."""
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="replace existing files")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    metadata = json.loads((ROOT / "assets/channel_metadata.json").read_text(encoding="utf-8"))["channels"]
    logo_dir = ROOT / "logo"
    logo_dir.mkdir(exist_ok=True)
    ok = skipped = failed = 0
    for entry in manifest["entries"]:
        name = entry["requested"]
        info = metadata[name]
        target = logo_dir / info["logo_file"]
        if target.exists() and not args.refresh:
            skipped += 1
            continue
        source = info.get("source_logo") or entry.get("logo")
        try:
            request = Request(source, headers={"User-Agent": "iptv-consolidated-playlist/logo-sync"})
            with urlopen(request, timeout=30) as response:
                data = response.read(4_000_000)
                content_type = (response.headers.get_content_type() or "").lower()
            if not data or not (content_type.startswith("image/") or target.suffix == ".svg"):
                raise ValueError(f"unexpected content type {content_type!r}")
            target.write_bytes(data)
            ok += 1
            print(f"synced {name} -> {target.relative_to(ROOT)}")
        except Exception as exc:
            failed += 1
            print(f"warning: could not sync {name}: {exc}", file=sys.stderr)
    print(f"logo sync: downloaded={ok} skipped={skipped} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
