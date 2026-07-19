# Repository assets

This directory follows the useful parts of the [CCSH/IPTV](https://github.com/CCSH/IPTV) layout while staying small and focused on Malaysia/Singapore use:

- `sources.txt` — active public playlist inputs, including the CCSH feeds and ChinaIPTV source.
- `ccsh-urls.txt` — the imported 102-URL source inventory from CCSH/IPTV.
- `channel_metadata.json` — language-specific display labels, English-only region/category, and audio/logo mapping.
- `channel_aliases.txt` — human-editable bilingual naming and alias list.
- `logo-sources.txt` — provenance/reference list for logo assets.

The published `logo/` directory is curated rather than a wholesale copy of the reference repository's very large China-only logo archive. Missing logos can be synchronized by the logo workflow, and every published M3U entry is checked for a local icon.
