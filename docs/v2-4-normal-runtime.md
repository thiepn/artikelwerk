# V2-4 — Normal Runtime Activation

## Decision

**Status: ACTIVE AND RELEASE-GATED.**

V2-4 activates the editorially certified 1,000-word **Normal · B2–C1** corpus in Artikelwerk's existing shared learning engine.

Challenge remains the default track. The internal identifier `bridge` is intentionally retained for persistence compatibility and historical generator/provenance paths; it is no longer the learner-facing product name.

## Runtime contract

Artikelwerk loads three local vocabulary assets before the application starts:

1. `translations.js` — Challenge English glosses and provenance.
2. `normal-translations.js` — certified Normal glosses/provenance merged into the same translation globals.
3. `normal-corpus.js` — the certified 1,000-row Normal vocabulary tuples.

The inline vocabulary bank then combines the original 1,000 Challenge rows with the Normal runtime rows through the existing `createVocabularyEntry` factory. This produces one 2,000-word engine with track-aware filtering rather than two separate learning implementations.

## Certification boundary

The pinned V2-2 files `bridge-corpus.js` and `bridge-translations.js` remain source/build inputs. They are **not** the learner-facing Normal runtime.

`scripts/materialize-bridge-v23.mjs` deterministically applies V2-3 editorial decisions and writes the generated certified corpus. The checked-in learner-facing files:

- `normal-corpus.js`
- `normal-translations.js`

must byte-match that generated materialization. `scripts/verify-dist.mjs` enforces this parity on every static release check.

This parity requirement is specifically intended to make branch-based GitHub Pages safe: repository-root runtime files and packaged `dist/` runtime files are the same certified data.

## Product behavior

### Practice

- Challenge remains selected by default.
- Normal is selectable from the vocabulary control and the secondary Practice action.
- Normal exposes its own difficulty labels:
  - Level 1 — Intermediate
  - Level 2 — Upper Intermediate
  - Level 3 — Advanced
- Every practice mode continues to scope its pool by the selected track before applying mode/difficulty rules.

### Progress

Progress supports:

- Current track
- Challenge
- Normal
- All vocabulary

Challenge and Normal maintain separate aggregate answer/correct/streak totals. The All view combines them.

### Vocabulary

Vocabulary supports the same four scopes. Challenge and Normal each contain 1,000 nouns; All vocabulary contains 2,000.

Word detail shows the set identity so a Normal word is visibly labeled **Normal · B2–C1**.

## Persistence compatibility

No storage reset is required.

Schema v10 already stores the selected vocabulary track and `aggregatesByTrack`. Historical v9 aggregate data migrates entirely into Challenge because no Normal runtime existed before that schema. Normal begins at zero for migrated users.

The stored identifier remains `bridge`. Renaming that key would require an unnecessary persistence migration and would risk invalidating saved settings/aggregates, so V2-4 changes only the product-facing label.

## Release gates

Release CI must fail if any of the following occur:

- Normal runtime assets are missing from `index.html`;
- the checked-in Normal runtime differs from the V2-3 materialization;
- the Normal option or Practice CTA is disabled despite the certified 1,000-word corpus;
- Normal practice cannot start;
- a Normal word lacks its local English gloss;
- Challenge practice increments Normal aggregates or vice versa;
- either per-track Vocabulary/Progress scope loses its 1,000-word contract;
- All vocabulary does not expose the 2,000-word union;
- v9→v10 migration invents historical Normal progress;
- browser errors, horizontal overflow, accessibility regressions, visual regressions, or session-completion failures occur.

`tests/vocabulary-tracks.mjs` exercises the Normal-specific runtime behavior on desktop and mobile; the rest of the browser suite protects the shared application surfaces.

## Exit criteria

V2-4 is complete when the exact release commit passes:

1. `npm run ci:static`;
2. the full Playwright browser/accessibility/visual/session suite;
3. zero open repository issues relevant to the release;
4. zero unresolved PR review threads.
