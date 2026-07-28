# IPTV Consolidated Playlist

A source-backed IPTV playlist repository for the household channel inventory.

## Current snapshot

The current inventory is a direct **94-entry import** from:

`https://live.yjzq.dpdns.org/output/m3u`

- `channel.md` — human-readable 94-channel register
- `manifest.json` — 94 imported stream entries and provenance
- `playlist.m3u` — generated playlist containing all 94 entries
- `assets/channel_metadata.json` — normalized display/category/language/logo metadata
- `assets/channel_aliases.txt` — exact aliases from the imported catalog
- `assets/sources.txt` — active catalog inventory, including the supplied source
- `assets/failed-sources.txt` — quarantined historical sources

`IMPORTED` entries are retained because the user requested an exact catalog replacement. They are not represented as independently identity-verified. A bounded HTTP first-byte sample reached 58/94 entries at import time; 35 timed out and 1 returned an error. The latest conservative VLC playback profile passed **58** entries and failed **36**; no visible identity verification was performed.

## Build and validation

```bash
python3 scripts/validate_repo.py
python3 scripts/build_playlists.py
python3 scripts/build_playlists.py --check
```

The builder preserves `source_order` for imported snapshots. It emits local-logo URLs from `logo/` so generated playlists remain self-contained and verifiable.

## Source and refresh policy

`vlc`/`cvlc` (VLC 3.x) is required for the bounded playback profile. The probe uses VLC's dummy interface and a short local transport output; it does not invoke `ffprobe` or `ffmpeg` directly. The supplied catalog is the source of truth for this snapshot. URLs are copied exactly from the catalog. The repository does not claim that a catalog listing proves current playback, stream quality, or visible identity; run the refresh/probe workflow before promoting entries to `PUBLISHED`.

Source health checks can be run with:

```bash
python3 scripts/check_sources.py --output reports/source-health.json --quality-output reports/source-quality.json
python3 scripts/refresh_sources.py --dry-run
```

Reports in `reports/` are evidence snapshots and should state their method and scope.
