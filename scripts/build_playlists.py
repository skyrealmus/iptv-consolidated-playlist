#!/usr/bin/env python3
"""Build a language-specific M3U output from the checked-in stream manifest."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
METADATA = ROOT / "assets" / "channel_metadata.json"


def load_data():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))["channels"]
    return manifest, metadata


def raw_base():
    repository = os.environ.get("GITHUB_REPOSITORY", "skyrealmus/iptv-consolidated-playlist")
    # Published playlist URLs stay stable on main; override explicitly for a fork.
    ref = os.environ.get("PLAYLIST_REF", "main")
    return f"https://raw.githubusercontent.com/{repository}/refs/heads/{quote(ref, safe='')}"


def attr(value: object) -> str:
    return str(value).replace("&", "&amp;").replace('"', "&quot;")


def render_entry(entry: dict, info: dict) -> str:
    requested = entry["requested"]
    display = info["display_name"]
    logo = f"{raw_base()}/logo/{quote(info['logo_file'])}"
    fields = [
        f'tvg-id="{attr(requested)}"',
        f'tvg-name="{attr(display)}"',
        f'tvg-logo="{attr(logo)}"',
        f'tvg-language="{attr(info["language"])}"',
        f'audio-language="{attr(info["audio_language"])}"',
    ]
    if entry.get("epg") is not None:
        fields.append(f'tvg-chno="{attr(entry["epg"])}"')
    fields.extend([
        f'group-title="{attr(info["group"])}"',
        f'tvg-country="{attr(info["country"])}"',
        f'tvg-category="{attr(info["category"])}"',
    ])
    return f"#EXTINF:-1 {' '.join(fields)},{display}\n{entry['url']}"


def render(entries: list[dict], metadata: dict) -> str:
    blocks = ["#EXTM3U"]
    for entry in entries:
        info = metadata.get(entry["requested"])
        if not info:
            raise ValueError(f"No channel metadata for {entry['requested']}")
        blocks.append(render_entry(entry, info))
    return "\n".join(blocks) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated files differ")
    args = parser.parse_args()
    manifest, metadata = load_data()
    entries = manifest["entries"]
    outputs = {ROOT / "playlist.m3u": render(entries, metadata)}
    mismatches = []
    for path, content in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                mismatches.append(path.name)
        else:
            path.write_text(content, encoding="utf-8")
    if mismatches:
        print("generated output mismatch:", ", ".join(mismatches), file=sys.stderr)
        return 1
    print(f"playlist entries={len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
