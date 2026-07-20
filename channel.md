# Channel Request and Daily Live-Source Check

This is the complete requested-channel register for the daily live-source refresh. Keep every requested channel in this file even when its stream is unavailable; use `WITHHELD` instead of deleting a request.

## Current snapshot

- Requested channels: **67**
- Published in `playlist.m3u`: **44**
- Withheld pending a verified source: **9**
- Newly requested and not yet checked: **14**
- Snapshot date: **2026-07-20**
- Machine source of truth for selected URLs: [`manifest.json`](./manifest.json)
- Machine source of truth for published and verified names, region, category, and language: [`assets/channel_metadata.json`](./assets/channel_metadata.json)
- `REQUESTED` rows remain register-only until a source passes verification and is added to the machine metadata.

## Full channel list

`Requested` is the stable request key used for source matching. `Display` is the published single-language name. The quality snapshot is evidence from the latest checked-in manifest; refresh it after each daily run.

| # | Reported issue | Requested | Display | Region | Category | Language | Status | Latest quality snapshot | Daily action |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | — | `CCTV-1` | CCTV-1 综合 | China | General | Chinese | PUBLISHED | resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 2 | — | `CCTV-5` | CCTV-5 体育 | China | Sports | Chinese | PUBLISHED | resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 3 | — | `CCTV-5+` | CCTV-5+ 体育赛事 | China | Sports | Chinese | PUBLISHED | resolution=1280x720 | Retest daily; replace only after playback and identity pass. |
| 4 | — | `CCTV-7` | CCTV-7 国防军事 | China | General | Chinese | PUBLISHED | resolution=1280x720 | Retest daily; replace only after playback and identity pass. |
| 5 | — | `CCTV-9` | CCTV-9 纪录 | China | Documentary | Chinese | PUBLISHED | resolution=1280x720 | Retest daily; replace only after playback and identity pass. |
| 6 | — | `CCTV-10` | CCTV-10 科教 | China | Documentary | Chinese | PUBLISHED | resolution=1280x720 | Retest daily; replace only after playback and identity pass. |
| 7 | — | `CCTV-16` | CCTV-16 奥林匹克 | China | Sports | Chinese | PUBLISHED | resolution=1280x720 | Retest daily; replace only after playback and identity pass. |
| 8 | — | `CCTV Fengyun Football` | CCTV 风云足球 | China | Sports | Chinese | PUBLISHED | resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 9 | — | `CCTV世界地理` | CCTV 世界地理 | China | Documentary | Chinese | PUBLISHED | speed=0.141x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 10 | — | `CCTV Weaponry Technology` | CCTV 兵器科技 | China | Documentary | Chinese | PUBLISHED | resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 11 | — | `CCTV4 HD` | CCTV-4 中文国际 | China | News | Chinese | PUBLISHED | speed=0.050x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 12 | Playback failed | `明珠台` | 明珠台 | Hong Kong | General | Chinese | WITHHELD | withheld — all tested public candidates failed ffprobe; no verified replacement | Keep withheld; publish only after correct identity and playback pass. |
| 13 | — | `Phoenix Chinese Channel HD` | 凤凰中文台 | China | Entertainment | Chinese | PUBLISHED | speed=0.066x | Retest daily; replace only after playback and identity pass. |
| 14 | — | `Phoenix Info News HD` | 凤凰资讯台 | China | News | Chinese | PUBLISHED | speed=0.013x | Retest daily; replace only after playback and identity pass. |
| 15 | Playback failed | `Phoenix Hong Kong` | 凤凰香港 | Hong Kong | News | Chinese | WITHHELD | withheld — tested candidates were interruption/expired pages or failed ffprobe | Keep withheld; publish only after correct identity and playback pass. |
| 16 | — | `Phoenix TV` | 凤凰卫视 | Hong Kong | News | Chinese | PUBLISHED | speed/resolution not recorded; recheck flag | Retest daily; replace only after playback and identity pass. |
| 17 | — | `TVBS Asia` | TVBS 亚洲 | Taiwan | News | Chinese | PUBLISHED | speed=0.189x; resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 18 | Playback failed | `EBC Variety` | 东森综合 | Taiwan | Entertainment | Chinese | WITHHELD | withheld — candidate returned 403; alternate token-bearing URL was not eligible for publication | Keep withheld; publish only after correct identity and playback pass. |
| 19 | — | `TVB Jade` | TVB 翡翠台 | Hong Kong | Entertainment | Chinese | PUBLISHED | speed=12.232x; resolution=3840x2160 | Retest daily; replace only after playback and identity pass. |
| 20 | Playback failed | `TVB Entertainment News` | TVB 娱乐新闻 | Hong Kong | News | Chinese | WITHHELD | withheld — all tested public candidates failed ffprobe or returned 403 | Keep withheld; publish only after correct identity and playback pass. |
| 21 | Playback failed | `TVB Xing He HD` | TVB 星河 | Hong Kong | Entertainment | Chinese | WITHHELD | withheld — label-matched candidates showed CCTV channels, not TVB星河 | Keep withheld; publish only after correct identity and playback pass. |
| 22 | — | `CGTN HD` | CGTN HD | China | News | English | PUBLISHED | speed=0.210x; resolution=1920x1080; recheck flag | Retest daily; replace only after playback and identity pass. |
| 23 | — | `CGTN Documentary` | CGTN Documentary | China | Documentary | English | PUBLISHED | speed=0.208x; resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 24 | Playback failed | `CNA HD` | CNA HD | Singapore | News | English | PUBLISHED | speed=9.270x; resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 25 | Playback failed | `Channel U` | U频道 | Singapore | Entertainment | Chinese | WITHHELD | withheld — wrong mapping: tested stream showed Shenzhen TV; official meWATCH stream is encrypted and Singapore VPN restricted | Keep withheld; publish only after correct identity and playback pass. |
| 26 | Wrong mapping | `Channel 8` | 8频道 | Singapore | General | Chinese | WITHHELD | withheld — wrong mapping: tested stream showed Channel 8 Thailand; official meWATCH stream is encrypted and Singapore VPN restricted | Keep withheld; publish only after correct identity and playback pass. |
| 27 | Slow / Glitch | `8TV` | 八度空间 | Malaysia | General | Chinese | WITHHELD | withheld — no verified playable alternative; candidate returned expired.html and prior source was slow/glitchy | Keep withheld; publish only after correct identity and playback pass. |
| 28 | — | `Astro AEC HD` | Astro AEC 高清 | Malaysia | Entertainment | Chinese | PUBLISHED | speed=0.009x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 29 | — | `Astro QJ` | Astro QJ 娱乐 | Malaysia | Entertainment | Chinese | PUBLISHED | speed=0.003x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 30 | — | `Astro AOD HD` | Astro AOD 高清 | Malaysia | Entertainment | Chinese | PUBLISHED | speed=0.244x; resolution=1920x1080; recheck flag | Retest daily; replace only after playback and identity pass. |
| 31 | — | `Astro Grandstand` | Astro Grandstand | Malaysia | Sports | English | PUBLISHED | speed=0.007x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 32 | — | `Astro Premier League` | Astro Premier League | Malaysia | Sports | English | PUBLISHED | speed=0.006x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 33 | — | `Astro Premier League 2` | Astro Premier League 2 | Malaysia | Sports | English | PUBLISHED | speed=0.009x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 34 | — | `Astro Football` | Astro Football | Malaysia | Sports | English | PUBLISHED | speed=0.046x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 35 | Wrong mapping | `Astro Badminton` | Astro Badminton | Malaysia | Sports | English | WITHHELD | withheld — wrong mapping: tested source labelled Astro Badminton 2 showed astro AWANI | Keep withheld; publish only after correct identity and playback pass. |
| 36 | — | `Astro Sports Plus` | Astro Sports Plus | Malaysia | Sports | English | PUBLISHED | speed=0.005x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 37 | — | `CNN HD` | CNN HD | International | News | English | PUBLISHED | speed=0.102x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 38 | — | `Bloomberg Television` | Bloomberg Television | International | News | English | PUBLISHED | speed=0.150x; resolution=1280x720; recheck flag | Retest daily; replace only after playback and identity pass. |
| 39 | — | `Love Nature 4K` | Love Nature 4K | International | Documentary | English | PUBLISHED | speed=0.271x; resolution=3840x2160; recheck flag | Retest daily; replace only after playback and identity pass. |
| 40 | — | `BBC Earth` | BBC Earth | International | Documentary | English | PUBLISHED | speed=0.791x; resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 41 | — | `History` | History | International | Documentary | English | PUBLISHED | speed=0.107x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 42 | — | `Nickelodeon` | Nickelodeon | International | Kids | English | PUBLISHED | speed=0.085x; resolution=1920x1080; recheck flag | Retest daily; replace only after playback and identity pass. |
| 43 | — | `Nick Jr` | Nick Jr | International | Kids | English | PUBLISHED | speed=0.028x; resolution=1048x576; recheck flag | Retest daily; replace only after playback and identity pass. |
| 44 | — | `Moonbug Kids` | Moonbug Kids | International | Kids | English | PUBLISHED | speed=0.165x; resolution=1920x1080; recheck flag | Retest daily; replace only after playback and identity pass. |
| 45 | — | `AXN` | AXN | International | Entertainment | English | PUBLISHED | speed=0.107x; resolution=1280x720; recheck flag | Retest daily; replace only after playback and identity pass. |
| 46 | — | `BBC News` | BBC News | International | News | English | PUBLISHED | speed=1.012x; resolution=1280x720 | Retest daily; replace only after playback and identity pass. |
| 47 | — | `Reuters` | Reuters | International | News | English | PUBLISHED | speed=2.450x; resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 48 | — | `Disney XD` | Disney XD | International | Kids | English | PUBLISHED | speed=0.132x; resolution=1280x720; recheck flag | Retest daily; replace only after playback and identity pass. |
| 49 | — | `National Geographic` | National Geographic | International | Documentary | English | PUBLISHED | speed=0.337x; resolution=1920x1080; recheck flag | Retest daily; replace only after playback and identity pass. |
| 50 | — | `Wild Earth` | Wild Earth | International | Documentary | English | PUBLISHED | speed=1.118x; resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 51 | — | `Kartoon Channel` | Kartoon Channel | International | Kids | English | PUBLISHED | speed=0.716x; resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 52 | — | `History Hit` | History Hit | International | Documentary | English | PUBLISHED | speed=0.597x; resolution=1280x720 | Retest daily; replace only after playback and identity pass. |
| 53 | — | `beIN Sports Xtra` | beIN Sports Xtra | International | Sports | English | PUBLISHED | speed=1.949x; resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 54 | New request | `爱奇艺 iQIYI` | 爱奇艺 | China | Entertainment | Chinese | REQUESTED | not yet checked | Discover and verify a current source before publication. |
| 55 | New request | `中天亚洲台 CTI Asia` | 中天亚洲台 | Taiwan | News | Chinese | REQUESTED | not yet checked | Discover and verify a current source before publication. |
| 56 | New request | `Astro欢喜台 Astro Hua Hee Dai` | Astro 欢喜台 | Malaysia | Entertainment | Chinese | REQUESTED | not yet checked | Discover and verify a current source before publication. |
| 57 | New request | `Cartoon Network` | Cartoon Network | International | Kids | English | REQUESTED | not yet checked | Discover and verify a current source before publication. |
| 58 | New request | `Asian Food Network` | Asian Food Network | International | Entertainment | English | REQUESTED | not yet checked | Discover and verify a current source before publication. |
| 59 | New request | `Astro Tennis` | Astro Tennis | Malaysia | Sports | English | REQUESTED | not yet checked | Discover and verify a current source before publication. |
| 60 | New request | `beIN SPORTS 1` | beIN SPORTS 1 | International | Sports | English | REQUESTED | not yet checked | Discover and verify a current source before publication. |
| 61 | New request | `beIN SPORTS 2` | beIN SPORTS 2 | International | Sports | English | REQUESTED | not yet checked | Discover and verify a current source before publication. |
| 62 | New request | `beIN SPORTS 3` | beIN SPORTS 3 | International | Sports | English | REQUESTED | not yet checked | Discover and verify a current source before publication. |
| 63 | New request | `Premier Sports` | Premier Sports | International | Sports | English | REQUESTED | not yet checked | Discover and verify a current source before publication. |
| 64 | New request | `CNBC` | CNBC | International | News | English | REQUESTED | not yet checked | Discover and verify a current source before publication. |
| 65 | New request | `Fox News` | Fox News | International | News | English | REQUESTED | not yet checked | Discover and verify a current source before publication. |
| 66 | New request | `Animal Planet` | Animal Planet | International | Documentary | English | REQUESTED | not yet checked | Discover and verify a current source before publication. |
| 67 | New request | `Discovery` | Discovery | International | Documentary | English | REQUESTED | not yet checked | Discover and verify a current source before publication. |

## Daily refresh workflow

1. Read every row in this file; do not silently drop `WITHHELD` channels.
2. Discover current candidates from the active public catalog in [`assets/sources.txt`](./assets/sources.txt). Do not use [`assets/failed-sources.txt`](./assets/failed-sources.txt) until a recheck passes.
3. Match candidates using the requested name and aliases. Do not trust a source label alone.
4. Probe candidates with FFprobe, then run a short FFmpeg decode to confirm actual video frames.
5. Check quality: HTTP/HLS availability, startup delay, decode success, resolution, throughput/decode speed, stalls/glitches, and `403`/expired/`nosignal` responses.
6. Check identity for reported, changed, or ambiguous channels using a visible logo/watermark or other on-screen evidence. A wrong channel fails even when playback works.
7. Do not publish credential-bearing, token-bearing, DRM-only, geo-restricted, expired, or identity-mismatched URLs.
8. Update the selected URL and evidence in `manifest.json` and `reports/stream-speed.json`; update this file's status/snapshot when the result changes.
9. Run the repository checks:

   ```bash
   python3 scripts/build_playlists.py
   python3 scripts/validate_repo.py
   python3 scripts/build_playlists.py --check
   ```

10. Confirm `accepted.m3u` is absent, run `git diff --check`, and verify the public raw playlist after pushing.

## Status rules

- `PUBLISHED`: one selected public source is currently included in `playlist.m3u`; it still requires daily retesting.
- `WITHHELD`: no source currently passes identity and playback checks, or the source is unsafe to publish. Keep the request row and record the reason in `manifest.json`/the audit report.
- `REQUESTED`: the channel has been added to this register but has not yet completed source, playback, and identity verification.
- A faster source is not automatically better: prefer a source that is both materially stable and identity-correct.
- Never restore a removed mapping only because the URL responds HTTP 200; require decoded playback and channel-identity evidence.

## Verification rule

Do not accept a source from its label alone. Confirm playback with FFprobe/FFmpeg and verify the visible channel identity before publishing it in `playlist.m3u`.
