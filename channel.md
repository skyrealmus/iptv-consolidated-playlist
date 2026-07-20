# Channel Request

This file is the reference list for the reported IPTV channel issues. Keep the original requested names when matching sources, and update the status here when an item is resolved.

## Requests

| Issue | Requested channel | Repository/canonical name | Required follow-up |
|---|---|---|---|
| Wrong mapping | 8频道 | Channel 8 / 8频道 | Find and verify the correct Singapore Channel 8 stream. |
| Wrong mapping | Astro Badminton | Astro Badminton | Find and verify the correct Astro Badminton stream. |
| Playback failed | CNA | CNA HD / CNA | Verify a playable, identity-correct source. |
| Playback failed | U频道 | Channel U / U频道 | Find and verify the correct Singapore Channel U stream. |
| Playback failed | Pearl | Pearl | Find and verify a playable source. |
| Playback failed | TVB娱乐新闻 | TVB Entertainment News / 无线新闻 | Find and verify a playable source. |
| Playback failed | TVB星河 | TVB Xing He HD / 无线星河 | Find and verify a playable source. |
| Playback failed | 凤凰香港 | Phoenix Hong Kong | Find and verify a playable source. |
| Playback failed | 东森综合 | EBC Variety / 东森综合 | Find and verify a playable source. |
| Slow / Glitch | 8度空间 | 8TV / 八度空间 | Find a faster and more stable source. |

## Verification rule

Do not accept a source from its label alone. Confirm playback with FFprobe/FFmpeg and verify the visible channel identity before publishing it in `playlist.m3u`.
