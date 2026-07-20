# Malaysia & Singapore IPTV — Language-specific channel names

A curated public IPTV playlist for Malaysia and Singapore users. Chinese-language channels use Chinese display names; English-language channels use English display names.

## Playlist links

[`playlist.m3u`](./playlist.m3u) — one best responding stream per requested channel.

Raw URLs:

```text
https://raw.githubusercontent.com/skyrealmus/iptv-consolidated-playlist/refs/heads/main/playlist.m3u
```

The playlist includes `tvg-name`, `tvg-logo`, `tvg-country`, `tvg-language`, `audio-language`, English-only `tvg-category` and `group-title`, and available `tvg-chno` metadata. Example:

```text
#EXTINF:-1 tvg-name="CNA HD" tvg-logo="..." tvg-language="English" audio-language="English" group-title="Singapore" tvg-category="News",CNA HD
```

Channel aliases remain bilingual for source matching, but published channel names are single-language. `audio-language="English"` identifies English-language channels; it does not transcode or alter a provider's HLS audio track.

## Current snapshot

- Unique requested channel names tracked: 53
- Channels with a verified public playlist entry: 44
- Nine channels are explicitly withheld pending a correct, playable, identity-verified source; see [`reports/targeted-channel-audit.json`](./reports/targeted-channel-audit.json)
- Probe method: Guovin/iptv-api parser and stream probe, with targeted FFmpeg/HLS speed checks and video-frame identity checks for reported channels
- Main policy: one selected URL per requested channel, grouped by category in this order: General, News, Entertainment, Sports, Documentary, Kids; Chinese channels precede English channels within each category
- Singapore additions: Channel U (`U频道`) and Channel 8 (`8频道`) are tracked in metadata but withheld from the public playlist until a non-DRM, identity-verified public stream is available
- Local logos: 53 tracked; 44 referenced by the public playlist
- Public source inputs: 82 active URLs; 31 failed URLs quarantined in [`assets/failed-sources.txt`](./assets/failed-sources.txt)

Streams are public third-party endpoints and may be geo-blocked, rate-limited, changed, or removed without notice. A playlist HTTP 200 or a prior probe is not a guarantee of continuous playback. Obvious token-bearing fallback URLs are not published.

## Repository layout

```text
assets/
  sources.txt             # active public M3U/TXT inputs (84 URLs)
  failed-sources.txt      # 31 URLs quarantined after the latest health failure
  channel_metadata.json   # language-specific names, regions, categories, audio metadata
  channel_aliases.txt     # human-editable aliases
  logo-sources.txt        # logo provenance/reference inputs
logo/                     # curated local logos used by every published entry
scripts/
  build_playlists.py      # deterministic M3U generator
  sync_logos.py           # fetches missing curated logos only
  validate_repo.py        # dependency-free playlist and asset checks
  check_sources.py        # lightweight source HTTP health report
reports/
  source-health.json      # active source catalog availability snapshot
  stream-speed.json       # targeted candidate probe and speed-test evidence
.github/workflows/
  validate.yml            # push/PR validation
  update-playlists.yml    # daily deterministic playlist rebuild
  logo-assets.yml         # weekly missing-logo synchronization
  source-health.yml       # weekly source health report
manifest.json             # stream snapshot, source provenance, and repo profile
```

The repository intentionally keeps logos local, so players do not depend on third-party logo hosts. The manifest retains the original logo URL as provenance.

[`assets/sources.txt`](./assets/sources.txt) is the active public source inventory with 82 URLs. URLs that failed the latest health check are quarantined in [`assets/failed-sources.txt`](./assets/failed-sources.txt) and are not scanned as active inputs until revalidated.

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

The active input list is maintained in [`assets/sources.txt`](./assets/sources.txt); quarantined failures are recorded in [`assets/failed-sources.txt`](./assets/failed-sources.txt).

## Disclaimer

This project is a personal technical aggregation and formatting tool. It does not own, host, or guarantee third-party streams. Channel names, logos, and stream URLs belong to their respective providers or rights holders. Users are responsible for complying with applicable laws, service terms, and copyright requirements in their location.

## Licence

This repository is released under the MIT License; third-party assets remain subject to their own licences and terms.
