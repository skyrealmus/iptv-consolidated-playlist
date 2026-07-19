# Repository assets

This directory follows the useful parts of the [CCSH/IPTV](https://github.com/CCSH/IPTV) layout while staying small and focused on Malaysia/Singapore use:

- `sources.txt` — public playlist inputs, including the ChinaIPTV source.
- `channel_metadata.json` — English-first / 简体中文 labels, English-only region/category, and logo mapping.
- `channel_aliases.txt` — human-editable bilingual naming and alias list.
- `logo-sources.txt` — provenance/reference list for logo assets.

The published `logo/` directory is curated rather than a wholesale copy of the reference repository's very large China-only logo archive. Missing logos can be synchronized by the logo workflow, and every published M3U entry is checked for a local icon.
