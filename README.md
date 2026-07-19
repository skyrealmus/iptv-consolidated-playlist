# Consolidated IPTV playlist

Public M3U playlists consolidated for personal IPTV-player use.

## Playlist links

- Main playlist (best responding endpoint per requested channel): [`playlist.m3u`](./playlist.m3u)
- Strict quality-pass playlist: [`accepted.m3u`](./accepted.m3u)

Raw URLs:

- `https://raw.githubusercontent.com/skyrealmus/iptv-consolidated-playlist/main/playlist.m3u`
- `https://raw.githubusercontent.com/skyrealmus/iptv-consolidated-playlist/main/accepted.m3u`

## Current snapshot

- Requested channels: 70
- Channels with a responding candidate: 36
- Strict quality-pass channels: 2
- Probe method: Guovin/iptv-api parser and stream probe
- Main playlist policy: one best responding URL per requested channel; strict passes are preferred
- Strict thresholds: minimum 0.5 MiB/s and 1280x720–3840x2160 resolution

The streams are public third-party endpoints and may be geo-blocked, rate-limited, changed, or removed without notice. A playlist HTTP 200 or a prior probe is not a guarantee of continuous playback. No credentials or private URLs are included.

## Sources

1. `https://live.hacks.tools/iptv/languages/eng.m3u`
2. `https://live.hacks.tools/iptv/languages/malaysia.m3u`
3. `https://raw.githubusercontent.com/YueChan/Live/refs/heads/main/Global.m3u`
4. `https://raw.githubusercontent.com/Guovin/TV/gd/output/result.m3u`
5. `https://live.hacks.tools/iptv/languages/zho.m3u`
6. `https://live.hacks.tools/iptv/languages/singapore.m3u`
7. `https://cdn.jsdelivr.net/gh/Kimentanm/aptv/m3u/iptv.m3u`
8. `https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u`
9. `https://bit.ly/iptv-aptv`
10. `https://tv.iill.top/m3u/Gather`
11. `https://bit.ly/suxuang`
12. `https://iptv-org.github.io/iptv/index.m3u`
13. `https://www.3kjs.com/tv.txt`
