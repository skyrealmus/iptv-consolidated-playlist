# Consolidated IPTV playlist

Public M3U playlists consolidated for personal IPTV-player use.

## Playlist links

- Main playlist (best responding endpoint per requested channel): [`playlist.m3u`](./playlist.m3u)
- Strict quality-pass playlist: [`accepted.m3u`](./accepted.m3u)

Raw URLs:

- `https://github.com/skyrealmus/iptv-consolidated-playlist/raw/refs/heads/main/playlist.m3u`
- `https://github.com/skyrealmus/iptv-consolidated-playlist/raw/refs/heads/main/accepted.m3u`

## Current snapshot

- Unique requested channel names tracked: 85
- Channels with a responding candidate: 49
- Strict quality-pass channels: 10
- Probe method: Guovin/iptv-api parser and stream probe
- Main playlist policy: one best responding URL per requested channel; strict passes are preferred
- Strict thresholds: minimum 0.5 MiB/s and 1280x720–3840x2160 resolution
- Entries without a supplied EPG number omit `tvg-chno`

The streams are public third-party endpoints and may be geo-blocked, rate-limited, changed, or removed without notice. A playlist HTTP 200 or a prior probe is not a guarantee of continuous playback. Obvious token-bearing fallback URLs were not published.

Source 14 was fetched with HTTP 200 and parsed into 68 entries. It adds no new published URL in this snapshot: TVBS-Asia duplicates an existing endpoint; its CCTV-4 candidate contains access credentials and was excluded; its Bloomberg and Celestial Movies candidates failed probing.

## Additional requested channels

Added candidates were checked for: BBC News, Eurosport 4K, Reuters, Discovery Channel, Disney XD, Big Ten Network, National Geographic, Cartoon Network, Wild Earth, Animal Planet (the supplied name was spelled `Animal Plannet`), BBC Earth, Kartoon Channel, History Hit, beIN Sports Xtra, CGTN纪录, CCTV4, CCTV世界地理, and TVBS-Asia.

No trustworthy responding candidate was available in this snapshot for: **Eurosport 4K, Discovery Channel, Cartoon Network, or Animal Planet**. The original requested set included 70 names; the added set contributes 15 new unique names because Discovery Channel, Cartoon Network, and BBC Earth were already requested. `BBC Earth` was already present and was refreshed to the fastest current responding endpoint.

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
14. `https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/cnTV_AutoUpdate.m3u8`
