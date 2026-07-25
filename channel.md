# Channel Request Register

This register tracks the current requested channels and the latest daily refresh evidence. Keep unavailable requests as `WITHHELD`; do not delete them.

## Current snapshot

- Requested channels: **83**
- Published matches in `playlist.m3u`: **49**
- Withheld pending a verified source: **13**
- New requests not yet checked: **21**
- Playlist entries in `playlist.m3u`: **55**; published additions are reflected in `manifest.json`.
- Manual final publication review: **2026-07-23T08:11:27Z**; four catalog-backed candidates published.
- Snapshot date: **2026-07-24**
<!-- DAILY_REFRESH_STATUS:START -->
- Last automated source refresh: **2026-07-24T18:47:06.365958+00:00**
- Mapped channels checked: **55**; verified unchanged: **0**; URLs refreshed: **0**
- Register rows checked: **83**; withheld rows reviewed: **34**; identity-review candidates: **0**; withheld probe failures: **32**
- Safe failures retained without replacement: probe failures **18**, unavailable catalogs **0**, no same-catalog alias match **37**, withheld no-match **2**
- Publication policy: same-source alias match plus FFprobe and short FFmpeg decode; cross-catalog replacements remain manual identity review.
<!-- DAILY_REFRESH_STATUS:END -->
- Machine source of truth for selected URLs: [`manifest.json`](./manifest.json)
- Machine source of truth for published and verified names, region, category, and language: [`assets/channel_metadata.json`](./assets/channel_metadata.json)
- `REQUESTED` rows remain register-only until a source passes verification and is added to the machine metadata.

## Channel list

`Requested` is the new stable request key. `Display` is the published single-language name. The quality snapshot comes from the latest checked-in evidence.

| # | Reported issue | Requested | Display | Category | Status | Latest quality snapshot | Daily action |
|---:|---|---|---|---|---|---|---|
| 1 | — | `CCTV-1` | CCTV-1 综合 | General | PUBLISHED | resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 2 | — | `CCTV-4` | CCTV-4 中文国际 | News | PUBLISHED | resolution=1920x1080; China mainland version verified; Europe variant excluded | Retest daily; replace only after playback and identity pass. |
| 3 | — | `CCTV-5` | CCTV-5 体育 | Sports | PUBLISHED | resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 4 | — | `CCTV-5+` | CCTV-5+ 体育赛事 | Sports | PUBLISHED | resolution=1280x720 | Retest daily; replace only after playback and identity pass. |
| 5 | — | `CCTV-7` | CCTV-7 国防军事 | General | PUBLISHED | resolution=1280x720 | Retest daily; replace only after playback and identity pass. |
| 6 | — | `CCTV-9` | CCTV-9 纪录 | Documentary | PUBLISHED | resolution=1280x720 | Retest daily; replace only after playback and identity pass. |
| 7 | — | `CCTV-10` | CCTV-10 科教 | Documentary | PUBLISHED | resolution=1280x720 | Retest daily; replace only after playback and identity pass. |
| 8 | New request | `CCTV-13` | CCTV-13 | News | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 9 | — | `CCTV-16` | CCTV-16 奥林匹克 | Sports | PUBLISHED | resolution=1280x720 | Retest daily; replace only after playback and identity pass. |
| 10 | — | `CCTV 风云足球` | CCTV 风云足球 | Sports | PUBLISHED | resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 11 | — | `CCTV世界地理` | CCTV 世界地理 | Documentary | PUBLISHED | speed=0.141x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 12 | — | `CCTV 兵器科技` | CCTV 兵器科技 | Documentary | PUBLISHED | resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 13 | — | `翡翠台` | TVB 翡翠台 | General | PUBLISHED | speed=12.232x; resolution=3840x2160 | Retest daily; replace only after playback and identity pass. |
| 14 | — | `无线新闻台` | 无线新闻台 | News | PUBLISHED | 1920x1080 H.264/AAC; visible 无线新闻台 watermark; source_index=77 | Retest daily; replace only after playback and identity pass. |
| 15 | New request | `TVB Plus` | TVB Plus | General | REQUESTED | current frame lacked TVB Plus identity | Keep REQUESTED; publish only after correct identity and playback pass. |
| 16 | — | `凤凰中文` | 凤凰中文台 | General | PUBLISHED | speed=0.066x | Retest daily; replace only after playback and identity pass. |
| 17 | Playback failed | `凤凰香港` | 凤凰香港 | News | WITHHELD | withheld — tested candidates were interruption/expired pages or failed ffprobe | Keep withheld; publish only after correct identity and playback pass. |
| 18 | — | `凤凰资讯` | 凤凰资讯台 | News | PUBLISHED | speed=0.013x | Retest daily; replace only after playback and identity pass. |
| 19 | — | `ViuTV` | ViuTV | General | PUBLISHED | 1920x1080 H.264; AAC rendition verified; visible viuTV watermark; source_index=77 | Retest daily; replace only after playback and identity pass. |
| 20 | Playback/identity failed | `明珠台` | 明珠台 | General | WITHHELD | 11 current candidates probed; 1 decoded an unbranded black-and-white performance with no TVB Pearl identity | Keep withheld; publish only after correct identity and playback pass. |
| 21 | — | `TVBS Asia` | TVBS 亚洲 | News | PUBLISHED | speed=0.189x; resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 22 | Playback failed | `EBC Variety` | 东森综合 | General | WITHHELD | withheld — vpstv candidate returned 403; catalog-extracted token URL was allowed by policy but timed out on the final probe | Keep withheld; publish only after a current exact candidate passes playback and identity checks. |
| 23 | New request | `华丽翡翠台` | 华丽翡翠台 | General | REQUESTED | current frame showed only base 翡翠台; exact variant unverified | Keep REQUESTED; publish only after exact variant identity passes. |
| 24 | Playback failed | `TVB 星河` | TVB 星河 | General | WITHHELD | withheld — label-matched candidates showed CCTV channels, not TVB星河 | Keep withheld; publish only after correct identity and playback pass. |
| 25 | New request | `中天亚洲` | 中天亚洲台 | News | WITHHELD | all safe exact candidates failed ffprobe or FFmpeg decode | Keep withheld; publish only after correct identity and playback pass. |
| 26 | Playback failed | `CNA HD` | CNA HD | News | PUBLISHED | speed=9.270x; resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 27 | Slow / VPN fallback | `Channel U` | U频道 (Geo-blocked) | General | PUBLISHED | 960x540 H.264/AAC; three current frames showed the U watermark, wondershop.sg, Singapore phone 6373 9898, and SGD pricing; public catalog source_index=5 | Retest daily; replace only after a better exact/source-only candidate passes playback and identity checks. |
| 28 | Wrong mapping | `Channel 8` | 8频道 | General | WITHHELD | fresh playable candidates showed Thailand, Russia/MIR, or other non-Singapore stations; official meWATCH source is DRM-restricted and Singapore VPN restricted | Keep withheld; publish only after correct identity and playback pass. |
| 29 | New request | `Channel 5` | Channel 5 | General | REQUESTED | current frame was WATCH NEXT VIDEO placeholder | Keep REQUESTED; publish only after correct identity and playback pass. |
| 30 | Slow / Glitch / VPN fallback | `8TV / 八度空间` | 八度空间 (Geo-blocked) | General | PUBLISHED | reused previous URL; resolution=1920x1080; current FFmpeg decode passed; historical speed=0.00347x; frame showed 8 LIVE/WOWshop; marked Geo-blocked for player-side VPN use | Retest daily; replace only after a better exact candidate passes playback and identity checks. |
| 31 | — | `Astro AEC` | Astro AEC 高清 | General | PUBLISHED | speed=0.009x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 32 | — | `Astro QJ` | Astro QJ 娱乐 | General | PUBLISHED | speed=0.003x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 33 | — | `Astro AOD` | Astro AOD 高清 | General | PUBLISHED | speed=0.244x; resolution=1920x1080; recheck flag | Retest daily; replace only after playback and identity pass. |
| 34 | New request | `Astro 欢喜台` | Astro 欢喜台 | General | WITHHELD | all safe exact candidates failed ffprobe or FFmpeg decode | Keep withheld; publish only after correct identity and playback pass. |
| 35 | New request | `爱奇艺` | 爱奇艺 | General | WITHHELD | all safe label-matched candidates failed ffprobe or FFmpeg decode | Keep withheld; publish only after correct identity and playback pass. |
| 36 | — | `Astro Grandstand` | Astro Grandstand | Sports | PUBLISHED | speed=0.007x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 37 | — | `Astro Premier League` | Astro Premier League | Sports | PUBLISHED | speed=0.006x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 38 | — | `Astro Premier League 2` | Astro Premier League 2 | Sports | PUBLISHED | speed=0.009x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 39 | — | `Astro Football` | Astro Football | Sports | PUBLISHED | speed=0.046x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 40 | Wrong mapping | `Astro Badminton` | Astro Badminton | Sports | WITHHELD | withheld — wrong mapping: tested source labelled Astro Badminton 2 showed astro AWANI | Keep withheld; publish only after correct identity and playback pass. |
| 41 | — | `Astro Sports Plus` | Astro Sports Plus | Sports | PUBLISHED | speed=0.005x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 42 | New request | `Now Sports Prime` | Now Sports Prime | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 43 | New request | `Now Sports 617` | Now Sports 617 | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 44 | New request | `Now Sports 618` | Now Sports 618 | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 45 | — | `CNN HD` | CNN HD | News | PUBLISHED | speed=0.102x; recheck flag | Retest daily; replace only after playback and identity pass. |
| 46 | — | `Bloomberg Television` | Bloomberg Television | News | PUBLISHED | speed=0.150x; resolution=1280x720; recheck flag | Retest daily; replace only after playback and identity pass. |
| 47 | — | `BBC News` | BBC News | News | PUBLISHED | speed=1.012x; resolution=1280x720 | Retest daily; replace only after playback and identity pass. |
| 48 | — | `Reuters` | Reuters | News | PUBLISHED | speed=2.450x; resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 49 | New request | `CNBC` | CNBC | News | PUBLISHED | resolution=640x360; frame-verified CNBC logo and programme branding | Retest daily; replace only after playback and identity pass. |
| 50 | New request | `Fox News` | Fox News | News | WITHHELD | three final-gate frames were commercials with no Fox News channel identity | Keep withheld; publish only after correct identity and playback pass. |
| 51 | — | `Disney XD` | Disney XD | Kids | PUBLISHED | speed=0.132x; resolution=1280x720; recheck flag | Retest daily; replace only after playback and identity pass. |
| 52 | — | `Kartoon Channel` | Kartoon Channel | Kids | PUBLISHED | speed=0.716x; resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 53 | — | `Nickelodeon` | Nickelodeon | Kids | PUBLISHED | speed=0.085x; resolution=1920x1080; recheck flag | Retest daily; replace only after playback and identity pass. |
| 54 | — | `Nick Jr` | Nick Jr | Kids | PUBLISHED | speed=0.028x; resolution=1048x576; recheck flag | Retest daily; replace only after playback and identity pass. |
| 55 | — | `Moonbug Kids` | Moonbug Kids | Kids | PUBLISHED | speed=0.165x; resolution=1920x1080; recheck flag | Retest daily; replace only after playback and identity pass. |
| 56 | — | `DreamWorks` | DreamWorks | Kids | PUBLISHED | 1920x1080 H.264/AAC; DreamWorks crescent watermark visible; source_index=77 | Retest daily; replace only after playback and identity pass. |
| 57 | New request | `Cartoon Network` | Cartoon Network (Geo-blocked) | Kids | PUBLISHED | resolution=1920x1080; three final-gate frames showed Cartoon Network watermark; public catalog source_index=57 | Retest daily; replace only after playback and identity pass. |
| 58 | — | `Love Nature 4K` | Love Nature 4K | Documentary | PUBLISHED | speed=0.271x; resolution=3840x2160; recheck flag | Retest daily; replace only after playback and identity pass. |
| 59 | — | `BBC Earth` | BBC Earth | Documentary | PUBLISHED | speed=0.791x; resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 60 | New request | `Animal Planet` | Animal Planet | Documentary | PUBLISHED | resolution=1920x1080; frame-verified Animal Planet watermark | Retest daily; replace only after playback and identity pass. |
| 61 | — | `National Geographic` | National Geographic | Documentary | PUBLISHED | speed=0.337x; resolution=1920x1080; recheck flag | Retest daily; replace only after playback and identity pass. |
| 62 | — | `Wild Earth` | Wild Earth | Documentary | PUBLISHED | speed=1.118x; resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 63 | New request | `Discovery` | Discovery | Documentary | PUBLISHED | resolution=1920x1080; frame-verified Discovery Channel watermark | Retest daily; replace only after playback and identity pass. |
| 64 | — | `beIN Sports Xtra` | beIN Sports Xtra | Sports | PUBLISHED | speed=1.949x; resolution=1920x1080 | Retest daily; replace only after playback and identity pass. |
| 65 | New request | `Asian Food Network` | Asian Food Network | General | WITHHELD | no exact or explicit candidate in 82 active catalogs | Keep withheld; publish only after correct identity and playback pass. |
| 66 | New request | `beIN SPORTS` | beIN SPORTS | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 67 | New request | `beIN SPORTS 2` | beIN SPORTS 2 | Sports | WITHHELD | decoded candidate displayed a Russian unavailable slate, not beIN SPORTS 2 | Keep withheld; publish only after correct identity and playback pass. |
| 68 | New request | `beIN SPORTS 3` | beIN SPORTS 3 (Geo-blocked) | Sports | PUBLISHED | resolution=1920x1080; three final-gate frames showed beIN SPORTS 3 watermark; public catalog source_index=57 | Retest daily; replace only after playback and identity pass. |
| 69 | New request | `beIN SPORTS 4` | beIN SPORTS 4 | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 70 | New request | `beIN SPORTS 5` | beIN SPORTS 5 | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 71 | New request | `TNT Sport 1` | TNT Sport 1 | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 72 | New request | `TNT Sport 2` | TNT Sport 2 | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 73 | New request | `TNT Sport 3` | TNT Sport 3 | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 74 | New request | `TNT Sport 4` | TNT Sport 4 | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 75 | — | `Hub Sports 1` | Hub Sports 1 | Sports | PUBLISHED | 1920x1080 H.264; HUB sports 1 watermark visible; catalog-derived signed URL; current video-only playlist | Retest daily; replace only after playback and identity pass. |
| 76 | New request | `Hub Sports 2` | Hub Sports 2 | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 77 | New request | `Hub Sports 3` | Hub Sports 3 | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 78 | New request | `Hub Sports 4` | Hub Sports 4 | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 79 | New request | `Hub Sports 5` | Hub Sports 5 | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 80 | New request | `Hub Sports 6` | Hub Sports 6 | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 81 | New request | `Hub Sports 7` | Hub Sports 7 | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 82 | New request | `Hub Sports 8` | Hub Sports 8 | Sports | REQUESTED | not yet checked | Discover and verify source, playback, and identity before publication. |
| 83 | New request | `Premier Sports` | Premier Sports | Sports | WITHHELD | playable candidates were Premier Sports 1/2, not the requested unnumbered target | Keep withheld; publish only after correct identity and playback pass. |

## Daily refresh rules

1. Check every row, including `WITHHELD` and `REQUESTED`, against active public catalogs in [`assets/sources.txt`](./assets/sources.txt). Do not use [`assets/failed-sources.txt`](./assets/failed-sources.txt) until rechecked.
2. Accept a replacement only when the same catalog has the requested alias and the URL passes FFprobe, short FFmpeg decode, playback-quality checks, and visible identity verification.
3. Never publish private credentials, DRM-only, expired, or identity-mismatched URLs. Catalog-derived signed URLs are allowed only with provenance and successful current checks. Geo-blocked fallbacks must be labelled `(Geo-blocked)`.
4. Record selected URLs in `manifest.json`, evidence in `reports/stream-speed.json`, and changed status/snapshots here.
5. Run:

   ```bash
   python3 scripts/build_playlists.py
   python3 scripts/validate_repo.py
   python3 scripts/build_playlists.py --check
   ```

6. Confirm `accepted.m3u` is absent, then run `git diff --check` and verify the public playlist after pushing.

## Status

- `PUBLISHED`: a selected, currently verified source is in `playlist.m3u`; retest daily.
- `WITHHELD`: no safe source currently passes playback and identity checks; keep the request and reason.
- `REQUESTED`: source, playback, and identity verification are not complete.
- HTTP `200` or a matching label alone is never sufficient; stability and identity matter more than speed.
