#!/usr/bin/env python3
"""Dependency-free repository and M3U integrity checks."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ATTR = re.compile(r'([\w-]+)="([^"]*)"')


def parse(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    entries = []
    for i, line in enumerate(lines):
        if not line.startswith("#EXTINF:"):
            continue
        if i + 1 >= len(lines) or lines[i + 1].startswith("#") or not lines[i + 1].strip():
            raise AssertionError(f"{path.name}: missing URL after line {i + 1}")
        attrs = dict(ATTR.findall(line))
        display = line.split(",", 1)[1] if "," in line else ""
        entries.append((attrs, display, lines[i + 1].strip()))
    if not entries:
        raise AssertionError(f"{path.name}: no EXTINF entries")
    for attrs, display, url in entries:
        for required in ("tvg-id", "tvg-name", "tvg-logo", "group-title", "tvg-country", "tvg-category"):
            if not attrs.get(required):
                raise AssertionError(f"{path.name}: missing {required} for {display}")
        if " / " not in attrs["tvg-name"]:
            raise AssertionError(f"{path.name}: non-bilingual tvg-name for {display}")
        parts = urlsplit(url)
        if parts.username or parts.password:
            raise AssertionError(f"{path.name}: credential-bearing stream URL")
        logo = unquote(urlsplit(attrs["tvg-logo"]).path).split("/logo/", 1)[-1]
        if not (ROOT / "logo" / logo).is_file():
            raise AssertionError(f"{path.name}: missing local logo {logo}")
    return entries


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    expected = len(manifest["entries"])
    if len(manifest.get("repository_profile", {}).get("languages", [])) != 2:
        raise AssertionError("repository_profile must declare English and Chinese")
    if (ROOT / "accepted.m3u").exists():
        raise AssertionError("accepted.m3u must not be published")
    all_entries = parse(ROOT / "playlist.m3u")
    if len(all_entries) != expected:
        raise AssertionError(f"playlist count {len(all_entries)} != manifest {expected}")
    print(f"validated bilingual playlist: playlist={len(all_entries)} logos={len(list((ROOT/'logo').iterdir()))}")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, json.JSONDecodeError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
