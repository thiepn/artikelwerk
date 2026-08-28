# Artikelwerk

Artikelwerk is a C1/C2 German noun-gender trainer with adaptive review, contextual and productive recall, local English glosses, vocabulary management, and a dedicated no-scroll practice screen.

## Canonical source

`index.html` is the single human-readable application source and the file served by the current GitHub Pages configuration. `translations.js` is the checked-in local English-gloss dataset used by that application.

The former packed payload, recovered-source duplicate, patch-on-build layer, heuristic practice adapter, and source-writing workflows have been retired. CI validates and packages the repository but never commits or pushes generated output.

## Development

Requirements:

- Node.js 20 or newer
- Python 3.12 for translation-generator syntax checks
- Playwright Chromium for browser certification

```bash
npm install --no-package-lock
npm run check
npm run build
npm run test:build
npx playwright install chromium
ARTIKELWERK_URL=http://127.0.0.1:4173 npm run test:browser
```

For the browser test, serve `dist/` on port `4173`, for example:

```bash
python -m http.server 4173 --directory dist
```

## Repository layout

```text
index.html                         canonical application source
translations.js                    local English-gloss dataset
docs/translation-coverage.txt      generated coverage evidence
scripts/generate_translations*.py  translation-data generators
scripts/verify-source.mjs          source, vocabulary, and translation checks
scripts/build.mjs                  deterministic static build
scripts/verify-dist.mjs            artifact round-trip verification
tests/practice-screen.mjs          responsive native practice-flow test
.github/workflows/ci.yml           read-only certification workflow
dist/                              generated artifact; never committed
```

## Release rules

- Edit `index.html`; do not restore a second editable HTML copy.
- Keep all 1,000 vocabulary IDs synchronized with `translations.js`.
- Run `npm run ci:static` before opening a pull request.
- CI uses read-only repository permissions and uploads artifacts instead of creating commits.
- The root application remains directly deployable by GitHub Pages while a later deployment migration can publish the certified `dist/` artifact.

## Licensing

See `THIRD_PARTY_NOTICES.md` and `LICENSES/GPL-3.0.txt` for the FreeDict-derived English-gloss subset.

## Content certification

- `translations.js` is the runtime-certified local gloss asset.
- `content/provenance.json` records source kind and review state for all 1,000 nouns.
- `content/ambiguous-gender-review.json` records externally verified variant and meaning-dependent gender decisions.
- `scripts/certify-content.mjs` exhaustively validates translation, provenance, example, ambiguity, and targeted inflection invariants.
- `tests/content-runtime.mjs` verifies the certified content surface across mobile, landscape, tablet, and desktop browser profiles.

Physical-device acceptance remains a manual final-release gate; see `docs/real-device-verification.md`.
