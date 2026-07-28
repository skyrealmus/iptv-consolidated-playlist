# IPTV Consolidated Playlist

At 08:00 Asia/Singapore daily, GitHub Actions VLC-checks every published URL for playback plus black/blank and stale video, then replaces failed URLs only with VLC-verified exact matches from the configured public catalogs.

Local verification:

```bash
python3 scripts/refresh_sources.py
python3 scripts/build_playlists.py
python3 scripts/validate_repo.py
```
