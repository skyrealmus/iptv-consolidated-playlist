# Malaysia & Singapore IPTV — English / 中文

A curated public IPTV playlist for Malaysia and Singapore users, with **English-first channel names followed by Simplified Chinese labels**.

## Playlist links

[`playlist.m3u`](./playlist.m3u) — one best responding stream per requested channel.

Raw URLs:

```text
https://raw.githubusercontent.com/skyrealmus/iptv-consolidated-playlist/refs/heads/main/playlist.m3u
```

The playlist includes `tvg-name`, `tvg-logo`, `tvg-country`, English-only `tvg-category` and `group-title`, and available `tvg-chno` metadata. Example:

```text
#EXTINF:-1 tvg-name="CNA HD / 亚洲新闻台" tvg-logo="..." group-title="Singapore" tvg-category="News",CNA HD / 亚洲新闻台
```

English is the canonical matching name; Chinese is the player-facing label after `/`. This keeps English-language IPTV apps readable while making the list convenient for Chinese-speaking users.

## Current snapshot

- Unique requested channel names tracked: 51
- Channels with a selected candidate: 51
- Probe method: Guovin/iptv-api parser and stream probe
- Main policy: one selected URL per requested channel, grouped by similarity
- Local channel logos: 51
- Public source inputs: 14

Streams are public third-party endpoints and may be geo-blocked, rate-limited, changed, or removed without notice. A playlist HTTP 200 or a prior probe is not a guarantee of continuous playback. Obvious token-bearing fallback URLs are not published.

## Repository layout

```text
assets/
  sources.txt             # public M3U/TXT inputs
  channel_metadata.json   # English / 简体中文 names, regions, categories, logo files
  channel_aliases.txt     # human-editable aliases
  logo-sources.txt        # logo provenance/reference inputs
logo/                     # curated local logos used by every published entry
scripts/
  build_playlists.py      # deterministic M3U generator
  sync_logos.py           # fetches missing curated logos only
  validate_repo.py        # dependency-free playlist and asset checks
  check_sources.py        # lightweight source HTTP health report
.github/workflows/
  validate.yml            # push/PR validation
  update-playlists.yml    # daily deterministic playlist rebuild
  logo-assets.yml         # weekly missing-logo synchronization
  source-health.yml       # weekly source health report
manifest.json             # stream snapshot, source provenance, and repo profile
```

The repository intentionally keeps logos local, so players do not depend on third-party logo hosts. The manifest retains the original logo URL as provenance.

## Automation

GitHub Actions use UTC schedules and write only to `main` with normal commits—there is no force-push history cleaner and no WARP/network proxy dependency.

- **Validate playlists** runs on relevant pushes and pull requests.
- **Build playlists** runs daily at 01:00 Asia/Singapore and is also manually dispatchable.
- **Logo assets** runs weekly at 08:00 Asia/Singapore and downloads only missing curated icons.
- **Source health** runs weekly and records HTTP status, sampled bytes, and sampled M3U entry counts in `reports/source-health.json`.

The current static stream snapshot is not silently replaced merely because a source is temporarily unavailable. Source health is reported separately; stream selection remains an explicit, quality-checked update.

## Local maintenance

From the repository root:

```bash
python3 scripts/sync_logos.py
python3 scripts/build_playlists.py
python3 scripts/validate_repo.py
python3 scripts/build_playlists.py --check
```

To inspect source availability:

```bash
python3 scripts/check_sources.py
```

## Sources

The complete input list is maintained in [`assets/sources.txt`](./assets/sources.txt).

## Disclaimer

This project is a personal technical aggregation and formatting tool. It does not own, host, or guarantee third-party streams. Channel names, logos, and stream URLs belong to their respective providers or rights holders. Users are responsible for complying with applicable laws, service terms, and copyright requirements in their location.

## Licence

This repository is released under the MIT License; third-party assets remain subject to their own licences and terms.
