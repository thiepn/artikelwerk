# V2-1 — Vocabulary Track Architecture & UX

V2-1 prepares Artikelwerk for a second 1,000-word corpus without changing the existing certified vocabulary content.

## Product contract

Artikelwerk has two vocabulary tracks:

- **Challenge · C1–C2** — the original 1,000 difficult nouns. This remains the default.
- **Bridge · B2–C1** — the future 1,000-word intermediate / upper-intermediate corpus. In V2-1 the track exists in the data model and UX but stays unavailable until V2-2 installs its words.

No existing noun is reclassified. Existing rows implicitly belong to `challenge`; future Bridge rows explicitly carry `track: "bridge"` through the vocabulary factory.

## Practice

Session Settings gains a Vocabulary selector. Difficulty labels are track-specific:

### Challenge
- All advanced levels
- Level 1 — Advanced
- Level 2 — Difficult
- Level 3 — Very Difficult

### Bridge
- All B2–C1 levels
- Level 1 — Intermediate
- Level 2 — Upper Intermediate
- Level 3 — Advanced

The home screen keeps Challenge as the main path and exposes a secondary Bridge action. Bridge automatically enables when Bridge rows exist; V2-1 does not fabricate or duplicate easier vocabulary.

Review Queue, Practice, Adaptive, Mistakes, Weak Words, Random, Timed Challenge, Today's Review, and Unknown Words all use the selected track before applying their existing mode/difficulty filters.

## Progress isolation

Persistence schema v10 adds `aggregatesByTrack` while retaining the existing global `aggregates` object for the All-vocabulary view.

A v9 migration assigns all historical aggregate data to Challenge because every pre-V2 word belongs to Challenge. Bridge starts at zero. Per-word SRS state stays keyed by unique word ID and therefore does not need a second storage tree.

Progress supports:
- Current track
- Challenge
- Bridge
- All vocabulary

Answer totals, accuracy, current/best streak, timing analytics, confidence calibration, article confusion, activity, mastery, due counts, and weak/stubborn lists are scoped to the selected Progress set.

## Vocabulary reference

Vocabulary supports the same Current / Challenge / Bridge / All scope. Track selection is separate from ordinary search/filter controls. Word detail explicitly shows its vocabulary set and level.

## Forward compatibility

V2-2 can add Bridge rows without changing Practice, Progress, Review Queue, or Vocabulary architecture. Adding rows with the Bridge track automatically enables the currently disabled Bridge controls and changes their count labels.

## Non-goals

V2-1 does not add, generate, translate, or certify any new nouns. It does not change scoring, SRS scheduling, article correctness, examples, translations, or the UI5.1 editorial art direction.
