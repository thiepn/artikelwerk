# Artikelwerk

Artikelwerk is a German noun-gender trainer with adaptive review, contextual and productive recall, local English glosses, vocabulary management, and a dedicated no-scroll practice screen.

## Vocabulary tracks

- **Challenge · C1–C2** — the original 1,000 difficult nouns. Challenge remains the default and only active practice corpus through V2-2.
- **Bridge · B2–C1** — a constructed 1,000-noun corpus staged for later activation: 400 Intermediate, 350 Upper Intermediate, and 250 Advanced.
- The final Bridge source-estimate mix is **600 B2 / 400 C1**. Level 2 deliberately bridges the bands with 200 B2 + 150 C1 nouns; Level 3 contains 250 upper-C1 candidates with additional lexical-complexity evidence.
- Bridge difficulty is source-informed and editorially screened. Its B2/C1 labels are targeting estimates, not official Goethe list membership.
- Challenge and Bridge have zero noun/ID overlap.
- **V2-2 does not activate Bridge in the learner UI.** The V2-1 disabled-Bridge behavior remains on `index.html` until V2-3 content review and V2-4 runtime integration are complete.

See `docs/v2-1-vocabulary-tracks.md` for the architecture/persistence contract and `docs/v2-2-bridge-corpus.md` for corpus construction, sources, screening, and licensing.

## Canonical source

`index.html` is the single human-readable application source and the file served by the current GitHub Pages configuration. Challenge glosses remain in `translations.js`. V2-2 checks in the future Bridge data as separate `bridge-corpus.js` and `bridge-translations.js` assets, but the application does not load them yet.

The former packed payload, recovered-source duplicate, patch-on-build layer, heuristic practice adapter, and source-writing workflows have been retired. Permanent CI is read-only: it validates source, Challenge content, the staged Bridge corpus, and deterministic packaging without committing or pushing generated output.

## Development

Requirements:

- Node.js 20 or newer
- Python 3.12 for content-generator syntax checks
- Playwright Chromium for browser certification

```bash
npm install --no-package-lock
npm run check
npm run certify:content
npm run certify:bridge
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
index.html                         canonical active application source
translations.js                    release-reviewed Challenge English-gloss dataset
bridge-corpus.js                    staged 1,000-row Bridge vocabulary asset
bridge-translations.js              staged Bridge English gloss/provenance runtime asset
content/bridge-provenance.json      per-entry Bridge source evidence
content/bridge-corpus-report.json   machine-readable corpus audit
scripts/generate_bridge_corpus.py   deterministic source/candidate generator
scripts/refine_bridge_corpus.py     learner-value and difficulty curation layer
scripts/certify-bridge.mjs          static Bridge corpus certification
scripts/generate_translations*.py   Challenge translation-data generators
scripts/verify-source.mjs           active source/vocabulary/translation checks
scripts/build.mjs                   deterministic static build
tests/practice-screen.mjs           responsive native practice-flow test
tests/vocabulary-tracks.mjs         V2-1 Challenge/disabled-Bridge architecture test
.github/workflows/ci.yml            read-only certification workflow
dist/                               generated artifact; never committed
```

## Release rules

- Edit `index.html`; do not restore a second editable HTML copy.
- Keep the active Challenge vocabulary IDs synchronized with `translations.js`.
- Keep all 1,000 staged Bridge rows synchronized with `bridge-translations.js` and `content/bridge-provenance.json`.
- Run `npm run ci:static` before opening a pull request.
- CI uses read-only repository permissions and uploads artifacts instead of creating commits.
- Bridge must not be enabled in the learner UI until its editorial content gate and runtime-integration phase are complete.

## Licensing

See `THIRD_PARTY_NOTICES.md`, `LICENSES/GPL-3.0.txt`, and `LICENSES/CC-BY-SA-4.0.txt`. Challenge and Bridge data licenses are documented separately.

## Content certification

- `translations.js` remains the release-reviewed Challenge gloss asset.
- `bridge-translations.js` is a **source-certified staging asset**, not yet the final editorial/release-reviewed Bridge copy.
- `content/provenance.json` retains the 1,000-word Challenge provenance; `content/bridge-provenance.json` independently records all 1,000 staged Bridge entries.
- `content/ambiguous-gender-review.json` records externally verified Challenge variant and meaning-dependent gender decisions.
- `scripts/certify-content.mjs` preserves the mature Challenge certification. `scripts/certify-bridge.mjs` separately certifies the Bridge count, 400/350/250 levels, 600/400 B2/C1 proxy mix, source evidence, local gloss coverage, licensing, article consistency, learner-value gates, and zero Challenge overlap.
- V2-3 is responsible for editorial review of Bridge glosses/examples/article notes and ambiguity handling before learner-facing activation.

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

V2-1 introduces one shared learning engine with two vocabulary scopes rather than six global difficulty levels. Challenge stays primary and default; Bridge is opt-in and automatically becomes available when later phases install Bridge-tagged rows. Practice pools, review queues, Progress analytics, Vocabulary reference views, and persistence are track-aware. Persistence schema v10 migrates all pre-V2 history into Challenge and starts Bridge at zero. `tests/vocabulary-tracks.mjs` certifies isolation, migration, responsive UX, and forward compatibility.

## V2-2 Bridge corpus research and construction

V2-2 constructs the 1,000-row Bridge dataset without activating it. The corpus is selected from pinned open lexical sources, independently corroborates single-gender nouns, excludes Challenge overlap and ambiguous/multi-gender candidates, filters basic/subtitle-noise vocabulary, and applies learner-value screening before difficulty assignment. The checked-in corpus is source-certified under CC-BY-SA-4.0 and is the input to V2-3 editorial certification.
