# Malaysia & Singapore IPTV Playlist

A curated public playlist with **44 verified entries** for **53 requested channels**. Nine channels remain withheld until a correct, playable, identity-verified source is available.

## Use

Playlist: [`playlist.m3u`](./playlist.m3u)

Raw URL:

```text
https://raw.githubusercontent.com/skyrealmus/iptv-consolidated-playlist/refs/heads/main/playlist.m3u
```

The playlist includes channel names, logos, language, country, category, and audio-language metadata. Player groups use channel types such as News, Kids, Sports, and Documentary; country remains available in `tvg-country`. Chinese channels use Chinese display names; English channels use English display names.

## Channel refresh

[`channel.md`](./channel.md) is the full channel request list and daily live-source quality-check register. It records published and withheld channels without exposing private endpoints or credentials.

## Repository layout

```text
assets/
  sources.txt             # active public source inputs
  failed-sources.txt      # quarantined source URLs awaiting recheck
  channel_metadata.json   # channel names, regions, categories, and logos
  channel_aliases.txt     # source-matching aliases
logo/                     # curated local logos
scripts/
  build_playlists.py      # deterministic playlist generator
  refresh_sources.py      # refreshes mapped URLs and reviews withheld rows with bounded probes
  check_sources.py        # source HTTP health check
  sync_logos.py           # fetches missing logos
  validate_repo.py        # playlist and asset validation
reports/                  # source and stream-check evidence
manifest.json             # selected streams and metadata
.github/workflows/        # validation and scheduled maintenance
```

## Local checks

From the repository root:

```bash
python3 scripts/build_playlists.py
python3 scripts/validate_repo.py
python3 scripts/build_playlists.py --check

# Preview the daily source refresh without changing manifest.json
python3 scripts/refresh_sources.py --dry-run
```

The scheduled workflow refreshes existing channel-to-catalog mappings: the
catalog label must match a configured alias, and the candidate must pass FFprobe
plus a short FFmpeg decode. It also scans all register rows, including
`WITHHELD`, and records bounded candidate probes for manual identity review.
It never automatically publishes a new cross-catalog mapping because stream
identity still requires human review.
The latest run is recorded in [`reports/daily-refresh.json`](./reports/daily-refresh.json).

## Disclaimer

Streams are provided by third parties and may change, disappear, or be unavailable in some locations. This project does not host or guarantee them. Users are responsible for following applicable laws, service terms, and copyright requirements.

## License

MIT. Third-party logos and stream sources remain subject to their own terms.
