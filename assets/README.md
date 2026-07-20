# Repository assets

This directory contains the source catalogs, channel metadata, and local logo inputs for Malaysia/Singapore use:

- `sources.txt` — active public playlist inputs (82 URLs after removing unavailable upstream references and the latest health quarantine).
- `failed-sources.txt` — 31 URLs quarantined from the active list after the latest source-health failure, with failure reasons.
- `channel_metadata.json` — language-specific display labels, English-only region/category, and audio/logo mapping.
- `channel_aliases.txt` — human-editable bilingual naming and alias list.
- `logo-sources.txt` — provenance/reference list for logo assets.

The published `logo/` directory is curated rather than a wholesale copy of the reference repository's very large China-only logo archive. Missing logos can be synchronized by the logo workflow, and every published M3U entry is checked for a local icon.
