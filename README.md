# Artikelwerk

C1/C2 German noun-gender trainer with adaptive review, vocabulary management, and a dedicated no-scroll practice screen.

## Development

- `app-source.html` is the editable application source.
- `index.html` is the GitHub Pages release file.
- `translations.js` contains the compact English-gloss data used during practice.
- `scripts/apply_practice_screen.py` applies the release UI patch.
- `scripts/generate_translations.py` selects dictionary-backed glosses.
- `scripts/generate_translations_v2.py` adds explicitly marked compound cues where no exact dictionary entry exists.
- `tests/practice-screen.mjs` checks mobile viewport stability and the complete practice flow in Chromium.

The production page is served directly from the repository root.
