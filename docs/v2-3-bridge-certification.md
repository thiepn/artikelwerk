# V2-3 — Normal Content Certification & Editorial Review

## Certification decision

**Status: RELEASE-CERTIFIED.**

V2-3 has completed the hard editorial pass for the 1,000-word Normal corpus. The checked-in V2-2 source extraction remains separately traceable as `source-certified`; learner-facing Normal release data is materialized from the V2-3 review ledgers and must pass the release gate before a build is accepted.

This phase certifies **content**. It does not by itself activate Normal in the learner UI; runtime activation remains a separate integration step.

## Certified result

The release gate now requires all of the following and passes on the certified branch:

- exactly **1,000 / 1,000** effective Normal entries;
- exactly **400 Intermediate / 350 Upper Intermediate / 250 Advanced** entries;
- the source-targeting contract remains **600 B2-estimated / 400 C1-estimated**;
- **0** Challenge noun/ID overlaps;
- **1,000 / 1,000** effective entries are editorially `release-reviewed`;
- **1,000 / 1,000** effective entries have reviewed-sense metadata;
- learner-facing gloss, example, rule, and level review are complete;
- every replacement decision has a fully reviewed successor before materialization;
- the official B1 lower-bound review is incorporated into retain/replace decisions;
- generic V2-2 example templates and blocked/noisy glossary artifacts are hard failures;
- unresolved gender/sense ambiguity, malformed tuple data, duplicate IDs/nouns, and invalid article evidence are hard failures;
- deterministic V2-3 materialization and packaged-output verification pass.

## Editorial standard

V2-3 keeps the product label **B2→C1-targeted**. It does not claim that Artikelwerk Normal is an official CEFR or Goethe B2/C1 vocabulary list.

The final review contract prioritizes:

1. **Headword and gender** — canonical contemporary spelling and one defensible article for the reviewed sense.
2. **Learner gloss** — one primary modern meaning, with at most one useful secondary meaning and no extraction noise or source annotations.
3. **Example sentence** — natural contemporary German that demonstrates the reviewed meaning and a realistic context or collocation.
4. **Gender rule** — a useful productive pattern where one exists, otherwise an explicit lexical/compound explanation rather than a fabricated rule.
5. **Learner value** — useful B2→C1 vocabulary over subtitle rarity, low-value props, transparent filler, or narrow person labels.
6. **Level calibration** — preserve the 400/350/250 product contract and the 600/400 B2/C1 source-targeting mix.
7. **Lower-bound screening** — Goethe B1 evidence is a strong replacement/review signal, not proof that every absent word is B2+.

## Review architecture

V2-3 deliberately separates source provenance from editorial release review.

The source assets remain reproducible and traceable. Editorial decisions are stored in review ledgers and batches, including:

- retained-entry editorial reviews;
- B1 lower-bound decisions;
- replacement decisions;
- successor reviews with explicit sense, gloss, example, rule, level, and B1-screen status.

`materialize-bridge-v23.mjs` applies those reviewed decisions deterministically when building the release artifact. This avoids mutating the pinned V2-2 source extraction merely to represent a later editorial decision.

## Hard release gate

`npm run ci:static` is the canonical static release gate. It executes source/content certification, Normal source certification, successor-ledger auditing, retained-entry B1 auditing, the editorial release assertion, deterministic V2-3 materialization, V2-3 certification, and packaged-output verification.

The release assertion fails if any effective entry has a hard blocker, including:

- `not-release-reviewed`;
- `missing-reviewed-sense`;
- missing gloss/example/rule/level editorial review;
- `replacement-pending`;
- generic examples;
- garbage or source-annotated glosses;
- excessive gloss senses;
- examples that do not contain the reviewed headword;
- tuple-contract violations.

Softer signals such as transparent cognates or generic taxonomy remain auditable without automatically invalidating otherwise reviewed content.

## CI policy

Release CI is deterministic and read-only.

Review-time candidate-pool diagnostics and replacement proposal generators remain available in the repository, but they are intentionally **not** required release-CI steps because they retrieve pinned external lexical sources. Once successor decisions are reviewed and committed, release correctness is determined by the checked-in ledgers and deterministic materializer—not by re-running a network-dependent discovery process.

CI additionally runs the full browser certification suite against the built `dist/` artifact, including practice flow, content runtime, app shell, surface polish, accessibility, editorial UI, visual acceptance, vocabulary-track architecture, and session completion.

## Exit criteria

V2-3 is complete when both of these conditions hold:

1. `npm run ci:static` passes with **0 hard editorial blockers** across all 1,000 effective Normal entries.
2. The full CI browser/visual/session suite passes on the same commit.

Those are the authoritative release criteria. Historical proposal artifacts and review-time diagnostics are not release blockers after the reviewed successor ledger has been certified.

## Handoff

V2-3 is a **content-certification completion**, not a runtime-activation phase. Normal should remain disabled in the learner-facing UI until the separate runtime integration is implemented and certified without regressing Challenge data, persistence isolation, practice flow, accessibility, or session completion.
