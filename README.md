# Artikelwerk

Artikelwerk is a German noun-gender trainer with adaptive review, contextual and productive recall, local English glosses, vocabulary management, and a focused no-scroll practice experience.

## Release status

Artikelwerk now ships two independently managed vocabulary tracks:

- **Challenge · C1–C2** — the original 1,000 difficult nouns and the default learner corpus.
- **Normal · B2–C1** — 1,000 editorially reviewed transition nouns: **400 Intermediate / 350 Upper Intermediate / 250 Advanced**, with a **600 B2-estimated / 400 C1-estimated** source-targeting mix.

Both tracks are learner-facing and usable in Practice, Progress, and Vocabulary. Challenge remains the default so existing users keep their current workflow; Normal is opt-in and maintains independent progress aggregates.

Challenge and Normal have zero noun/ID overlap. CEFR labels are targeting estimates, not claims of official Goethe B2/C1 list membership.

See `docs/v2-1-vocabulary-tracks.md`, `docs/v2-2-bridge-corpus.md`, `docs/v2-3-bridge-certification.md`, and `docs/v2-4-normal-runtime.md` for the architecture, corpus construction, editorial certification, and runtime activation contracts.

## Canonical source and runtime data

`index.html` is the single human-readable application source. Challenge glosses remain in `translations.js`.

The historical/internal `bridge` identifier is intentionally retained for persistence compatibility, generator paths, and V2-2/V2-3 provenance. The learner-facing product name is **Normal**.

Two layers are kept separate:

- `bridge-corpus.js` / `bridge-translations.js` — pinned V2-2 source-certified inputs used by the editorial/materialization toolchain.
- `normal-corpus.js` / `normal-translations.js` — checked-in, learner-facing runtime assets that must byte-match the deterministic V2-3 materialization.

`scripts/materialize-bridge-v23.mjs` applies the reviewed retain/replacement ledgers to the pinned V2-2 source inputs. CI rebuilds that materialization and fails if the checked-in Normal runtime assets have drifted. This matters for branch-based GitHub Pages because the files served directly from the repository are therefore the same certified data used in `dist/`.

Generated `dist/` output is never the editable source of truth.

## Development

Requirements:

- Node.js 20 or newer
- Python 3.12 for content-generator syntax checks
- Playwright Chromium for browser certification

Install dependencies and run the complete static release gate:

```bash
npm install --no-package-lock
npm run ci:static
```

Run browser certification against the built artifact:

```bash
npx playwright install chromium
python -m http.server 4173 --bind 127.0.0.1 --directory dist
```

Then, in another shell:

```bash
ARTIKELWERK_URL=http://127.0.0.1:4173 npm run test:browser
ARTIKELWERK_URL=http://127.0.0.1:4173 npm run test:content-browser
ARTIKELWERK_URL=http://127.0.0.1:4173 npm run test:shell-browser
ARTIKELWERK_URL=http://127.0.0.1:4173 npm run test:surfaces-browser
ARTIKELWERK_URL=http://127.0.0.1:4173 npm run test:a11y-browser
ARTIKELWERK_URL=http://127.0.0.1:4173 npm run test:editorial-browser
ARTIKELWERK_URL=http://127.0.0.1:4173 npm run test:visual-acceptance-browser
ARTIKELWERK_URL=http://127.0.0.1:4173 npm run test:tracks-browser
ARTIKELWERK_URL=http://127.0.0.1:4173 npm run test:session-browser
```

The GitHub Actions workflow performs the same static and rendered acceptance gates and uploads the certified `dist/` artifact plus browser evidence.

## Release certification

`npm run ci:static` is the canonical static release gate. It verifies:

- active source and Challenge vocabulary/translation integrity;
- Challenge release-reviewed content;
- the 1,000-row Normal source corpus and provenance contract;
- V2-3 replacement decisions and reviewed successors;
- retained-entry B1 lower-bound review;
- **0 hard editorial blockers across all 1,000 effective Normal entries**;
- deterministic V2-3 materialization;
- checked-in `normal-corpus.js` / `normal-translations.js` parity with that materialization;
- level/count/CEFR-targeting and Challenge-overlap invariants;
- runtime loading of the certified Normal assets;
- deterministic static packaging and packaged-output integrity.

Browser certification additionally verifies Normal selection, Normal practice, local English glosses, separate Challenge/Normal progress aggregates, 1,000-word per-track views, the 2,000-word combined views, persistence migration, accessibility, responsive behavior, visual acceptance, and session completion.

Release CI deliberately does **not** make network-dependent proposal discovery a shipping requirement. Replacement-pool diagnostics and proposal generators remain review-time tools; the shipping invariant is the committed reviewed ledger plus deterministic materialization.

## Repository layout

```text
index.html                              canonical active application source
translations.js                         release-reviewed Challenge English glosses
normal-corpus.js                        certified learner-facing Normal runtime corpus
normal-translations.js                  certified learner-facing Normal translations
bridge-corpus.js                         pinned V2-2 source corpus / internal build input
bridge-translations.js                   pinned V2-2 source translations / internal build input
content/bridge-provenance.json           per-entry Normal source evidence
content/bridge-editorial-review.json     V2-3 editorial retain/review ledger
content/bridge-b1-lower-bound-review.json
content/bridge-replacement-review.json   reviewed V2-3 successor ledger
scripts/materialize-bridge-v23.mjs       deterministic V2-3 materializer
scripts/audit-bridge-editorial.mjs       hard editorial release assertion
scripts/certify-bridge-v23.mjs           materialized V2-3 certification
scripts/build.mjs                        deterministic static build
tests/vocabulary-tracks.mjs             Challenge + active Normal runtime certification
tests/                                   browser, accessibility, visual, and session gates
.github/workflows/ci.yml                 read-only release certification workflow
dist/                                    generated artifact; never committed
```

## Release rules

- Edit `index.html`; do not restore a second editable HTML copy.
- Keep active Challenge IDs synchronized with `translations.js`.
- Keep the pinned V2-2 Normal source assets synchronized with formal provenance.
- Represent V2-3 editorial changes in the review ledgers; do not silently rewrite source provenance.
- Regenerate/check the learner-facing Normal runtime after editorial data changes; `npm run ci:static` rejects stale runtime assets.
- Preserve the internal `bridge` persistence key unless a deliberate schema migration is introduced.
- Run `npm run ci:static` before merge/release.
- CI remains read-only and uploads evidence/artifacts instead of committing generated output.
- Physical-device acceptance remains a manual final-release gate; see `docs/real-device-verification.md`.

## Interaction and visual system

Artikelwerk uses a typography-first editorial interface rather than a dashboard/card aesthetic. The current UI system includes:

- paper-like neutrals and restrained terracotta actions;
- serif learning typography and ruled editorial sections;
- a focused fullscreen practice surface;
- report-style Progress and reference-style Vocabulary views;
- fixed mobile navigation with practice clearance;
- keyboard focus restoration and modal background isolation;
- reduced-motion and forced-colors support;
- narrow-phone and short-landscape acceptance coverage;
- dynamic fitting for long German compounds.

Relevant design contracts live in `docs/ui1-visual-identity.md`, `docs/ui2-app-shell.md`, `docs/ui3-surface-polish.md`, `docs/ui4-interaction-accessibility.md`, `docs/ui5-editorial-rebuild.md`, and `docs/ui5-1-visual-acceptance.md`.

## Vocabulary architecture

V2-1 introduced one learning engine with isolated Challenge and Normal scopes. Persistence schema v10 migrates existing history into Challenge and initializes Normal separately. Practice pools, review queues, Progress analytics, Vocabulary views, and persistence are track-aware.

V2-2 constructed the reproducible 1,000-row Normal source corpus from pinned open lexical sources, with gender corroboration, Challenge-overlap exclusion, ambiguity filtering, lower-value/noise filtering, and source-informed difficulty assignment.

V2-3 completed editorial content certification: reviewed senses, learner glosses, meaning-bearing examples, article rules, level decisions, B1 lower-bound screening, and reviewed successors are enforced as release invariants.

V2-4 activates that certified corpus in the shared learning engine without renaming the internal `bridge` key. Normal is now selectable in Practice, Progress, and Vocabulary; combined scopes contain 2,000 nouns while Challenge remains the default and historical progress stays isolated.

## Licensing

See `THIRD_PARTY_NOTICES.md`, `LICENSES/GPL-3.0.txt`, and `LICENSES/CC-BY-SA-4.0.txt`. Challenge and Normal data licensing/provenance are documented separately in the repository.
