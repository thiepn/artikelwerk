# Artikelwerk

Artikelwerk is a German noun-gender trainer with adaptive review, contextual and productive recall, local English glosses, vocabulary management, and a dedicated no-scroll practice screen.

## Vocabulary tracks

- **Challenge · C1–C2** — the original 1,000 difficult nouns. Challenge remains the default practice experience.
- **Bridge · B2–C1** — 1,000 additional intermediate-to-advanced nouns: 400 Intermediate, 350 Upper Intermediate, and 250 Advanced.
- Bridge difficulty is source-informed and editorially screened. Its B2/C1 labels are targeting estimates, not official Goethe list membership.
- Existing progress remains Challenge progress; Bridge starts independently, while **All vocabulary** reports across all 2,000 installed nouns.
- Challenge and Bridge have zero noun/ID overlap.

See `docs/v2-1-vocabulary-tracks.md` for the architecture/persistence contract and `docs/v2-2-bridge-corpus.md` for corpus construction, sources, screening, and licensing.

## Canonical source

`index.html` is the single human-readable application source and the file served by the current GitHub Pages configuration. Challenge glosses remain in `translations.js`; the checked-in Bridge corpus and glosses live in the separate `bridge-corpus.js` and `bridge-translations.js` assets.

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
translations.js                    Challenge English-gloss dataset
bridge-corpus.js                    1,000-row Bridge vocabulary asset
bridge-translations.js              Bridge English gloss + provenance runtime asset
docs/translation-coverage.txt      generated coverage evidence
scripts/generate_translations*.py  translation-data generators
scripts/verify-source.mjs          source, vocabulary, and translation checks
scripts/build.mjs                  deterministic static build
scripts/verify-dist.mjs            artifact round-trip verification
tests/practice-screen.mjs          responsive native practice-flow test
tests/vocabulary-tracks.mjs        Challenge/Bridge architecture and migration test
.github/workflows/ci.yml           read-only certification workflow
dist/                              generated artifact; never committed
```

## Release rules

- Edit `index.html`; do not restore a second editable HTML copy.
- Keep all installed vocabulary IDs synchronized with `translations.js`.
- Run `npm run ci:static` before opening a pull request.
- CI uses read-only repository permissions and uploads artifacts instead of creating commits.
- The root application remains directly deployable by GitHub Pages while a later deployment migration can publish the certified `dist/` artifact.

## Licensing

See `THIRD_PARTY_NOTICES.md`, `LICENSES/GPL-3.0.txt`, and `LICENSES/CC-BY-SA-4.0.txt`. Challenge and Bridge data licenses are documented separately.

## Content certification

- `translations.js` is the release-reviewed Challenge gloss asset; `bridge-translations.js` is the source-certified Bridge gloss asset.
- `content/provenance.json` retains the 1,000-word Challenge provenance; `content/bridge-provenance.json` independently records all 1,000 Bridge entries.
- `content/ambiguous-gender-review.json` records externally verified variant and meaning-dependent gender decisions.
- `scripts/certify-content.mjs` preserves the mature Challenge certification. `scripts/certify-bridge.mjs` separately certifies the 1,000-row Bridge split, source evidence, translations, licensing, examples, and zero overlap.
- `tests/content-runtime.mjs` verifies the certified content surface across mobile, landscape, tablet, and desktop browser profiles.

Physical-device acceptance remains a manual final-release gate; see `docs/real-device-verification.md`.

## Visual identity

UI1 establishes Artikelwerk's original visual foundation: warm editorial neutrals, a single deep-teal accent, restrained borders/radii/elevation, a geometric `A` brand mark, full favicon/platform icon coverage, and light/dark theme tokens. See `docs/ui1-visual-identity.md`.

## UI2 application shell

- Desktop primary navigation is integrated into the application header.
- Mobile primary navigation uses a fixed bottom bar while practice remains a full-screen modal.
- Practice is ordered as primary action → review queue → session setup.
- `tests/app-shell.mjs` certifies shell hierarchy and navigation at desktop and mobile widths.
- See `docs/ui2-app-shell.md` for the shell contract and UI3 handoff.

## UI3 surface polish

- Dedicated practice uses a focused exercise hierarchy with structured article controls and contained feedback.
- Progress uses one learner-oriented overview instead of ten equal KPI cards.
- Vocabulary uses a denser reference-library surface with restrained filters and word details.
- `tests/surface-polish.mjs` certifies these surfaces across desktop and mobile profiles.
- See `docs/ui3-surface-polish.md` for the UI3 contract and UI4 handoff.

## UI4 interaction, accessibility, and responsive finish

- Focus indicators use a stable two-pixel perimeter and fixed-chrome-safe scroll margins.
- Modals inert the background application and restore focus on close.
- Reduced-motion preferences disable non-essential animation and smooth scrolling.
- Forced-colors/high-contrast modes retain visible state and focus cues.
- Narrow-phone and short-landscape breakpoints are explicitly certified.
- `tests/accessibility-finish.mjs` exercises keyboard focus, target sizes, modal isolation, theme semantics, reduced motion, forced colors, and responsive reflow.
- See `docs/ui4-interaction-accessibility.md` for the UI4 contract and pre-RC handoff.

## UI5 editorial rebuild

UI5 supersedes the teal/card-based treatment with a typography-first editorial interface: paper neutrals, terracotta actions, serif learning typography, ruled sections instead of cards, a cardless fullscreen trainer, a report-like Progress view, and a reference-table Vocabulary view. The favicon family is replaced with the matching book-spine A mark. `tests/editorial-ui.mjs` certifies the anti-dashboard visual contract. See `docs/ui5-editorial-rebuild.md`.

## UI5.1 visual acceptance fixes

UI5.1 keeps the editorial UI5 direction while fixing the release-gate defects found in rendered acceptance review: dynamic fitting for long German compounds, mobile bottom-navigation clearance, compact mobile Vocabulary filters, a calmer mobile Progress hierarchy, and tighter desktop Practice spacing. See `docs/ui5-1-visual-acceptance.md`.

## V2-1 vocabulary track architecture

V2-1 introduces one shared learning engine with two vocabulary scopes rather than six global difficulty levels. Challenge stays primary and default; Bridge is opt-in and automatically becomes available when V2-2 installs Bridge-tagged rows. Practice pools, review queues, Progress analytics, Vocabulary reference views, and persistence are track-aware. Persistence schema v10 migrates all pre-V2 history into Challenge and starts Bridge at zero. `tests/vocabulary-tracks.mjs` certifies isolation, migration, responsive UX, and forward compatibility.
