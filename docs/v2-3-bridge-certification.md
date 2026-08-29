# V2-3 — Bridge Content Certification & Editorial Review

## Certification decision

**Status: RELEASE CERTIFICATION WITHHELD.**

The V2-2 Bridge corpus is reproducible and source-traceable, but the current `source-certified` marker is not an editorial release certification. V2-3 deliberately separates those concepts.

### What already passes

- Exactly 1,000 Bridge nouns.
- Level distribution remains 400 Intermediate / 350 Upper Intermediate / 250 Advanced.
- Source targeting remains 600 B2-estimated / 400 C1-estimated.
- Challenge overlap is zero.
- Every retained noun has one quiz article and source-corroborated gender evidence.
- Source archives, commits, checksums, licensing, frequency evidence, and selection methodology remain pinned and reproducible.

### Why release certification is withheld

1. **All 1,000 Bridge provenance entries are only `source-certified`.** None currently carries the Challenge-style `release-reviewed` editorial state or an explicit reviewed sense identifier.
2. **All 1,000 learner examples are selected from eight generic templates.** They prove article insertion but do not reliably teach a noun's meaning, collocations, register, or normal context.
3. **The raw Wiktionary translation flattening is not sense-safe.** It can retain irrelevant, archaic, domain-labelled, or simply misleading secondary translations. Confirmed examples in the checked-in asset include `Flüchtling → refugee; flibbertigibbet`, `Herzschlag → heart attack; beating of the heart`, `Vollmond → full moon; baldie`, and `Chemie → chemistry; Psychologie: attunement`.
4. **Taxonomy is too weak to be an editorial signal.** V2-2 currently places 923 / 1,000 nouns in `bridge-general`.
5. **Learner-value heuristics are useful for selection but cannot substitute for editorial sense review.** They consume the same source gloss text whose secondary senses can be noisy.
6. **The existing certification script checks shape and provenance, not meaning.** A non-empty gloss under 145 characters and a grammatically article-matching generic example can pass even when the learner-facing sense is poor.

## Standards used for V2-3

V2-3 keeps the existing label **B2→C1-targeted**. It does not claim that the 1,000 nouns constitute an official CEFR or Goethe B2/C1 vocabulary list.

The editorial standard is aligned to three external principles:

- **CEFR Companion Volume:** B2 vocabulary control should already be generally accurate; at C1, less-common vocabulary should be used idiomatically and appropriately. Vocabulary competence increasingly depends on collocations and lexical chunks, not isolated word rarity.
- **Goethe-Zertifikat B1 word list:** use the official B1 list as a lower-bound exclusion/reference signal, not as proof that every noun absent from the list is B2+. Its own selection criterion is relevance in contemporary everyday German across private/public life and also work, school, and training.
- **Goethe-Zertifikat C1:** the target user should be able to use German effectively and flexibly in public, academic, and professional life. Advanced Bridge content should therefore prioritize precise, current, useful abstract/institutional/process vocabulary over subtitle rarity or novelty.

## V2-3 editorial contract

A Bridge noun may be marked `release-reviewed` only when all applicable checks below pass.

### 1. Headword and gender

- Canonical contemporary spelling.
- One unambiguous article for the reviewed target sense.
- Multi-gender or sense-dependent nouns require an explicit sense decision; otherwise replace the noun.
- No person/name-only interpretation silently reduced to one quiz answer.

### 2. English learner gloss

- One primary modern learner meaning; a second meaning is allowed only when common and genuinely useful.
- The gloss must describe the reviewed German sense, not merely reproduce the first extraction string.
- Remove source annotations, labels, obsolete meanings, jokes, rare dictionary curiosities, and domain fragments that do not belong in the learner surface.
- Avoid needlessly obscure English words when a normal English equivalent exists.
- Explicit reviewed-sense metadata is required.

### 3. Example sentence

- Natural contemporary German.
- Semantically demonstrates the reviewed noun meaning.
- Uses a normal collocation or realistic context where possible.
- Article/case agreement must be correct.
- No generic `X wurde ... erwähnt/geprüft/betrachtet` filler may count as the release example.
- Examples should be independently understandable without the English gloss.

### 4. Learner value

- Appropriate for a learner intentionally bridging B2 toward C1.
- High utility outweighs rarity.
- Transparent internationalisms may stay only when gender learning or functional usefulness justifies the slot.
- Low-value props, entertainment vocabulary, highly specific person labels, and subtitle artifacts should be replaced when a stronger eligible candidate exists.
- Official Goethe B1 vocabulary is treated as a strong lower-bound review signal. A B1-list collision requires explicit justification or replacement.

### 5. Level calibration

- **Level 1 — Intermediate:** high-utility B2-targeted nouns; not basic everyday vocabulary merely made difficult by article uncertainty.
- **Level 2 — Upper Intermediate:** stronger B2 plus accessible C1 transition vocabulary.
- **Level 3 — Advanced:** useful current C1-targeted vocabulary with precision, abstraction, institutional/professional relevance, or productive formal morphology.
- Preserve 400 / 350 / 250 and 600 B2 / 400 C1 unless a later version explicitly changes the product contract.

## Required release metadata

V2-3 must stop overloading `reviewStatus` with source traceability.

Each release-reviewed entry should expose separate fields equivalent to:

```json
{
  "sourceStatus": "source-certified",
  "reviewStatus": "release-reviewed",
  "reviewedSenseIds": ["..."],
  "glossReview": "editorial",
  "exampleReview": "editorial",
  "levelReview": "editorial"
}
```

The exact source sense identifier may be a stable local ID derived from the pinned source extraction; it must not depend on a live network lookup at runtime.

## CI release gate

`certify:bridge` must eventually reject the release when any of the following remain:

- a Bridge entry without `release-reviewed` status;
- missing reviewed-sense metadata;
- a generic V2-2 example template;
- a known source annotation or blocked glossary artifact in the learner gloss;
- duplicate IDs/nouns or Challenge overlap;
- invalid article/gender evidence;
- level-count or B2/C1-contract drift;
- a release override that is absent from formal provenance;
- unresolved editorial exceptions.

V2-3 may keep a separate audit command that reports softer risks (transparent cognates, generic taxonomy, low learner-value nouns) without automatically treating every flagged item as a defect.

## Review order

1. **Sense/gloss triage:** remove clearly wrong and noisy translations first because learner-value scoring and example writing depend on the intended sense.
2. **Low-value/replacement pass:** review the weakest Level 1/2 candidates and transparent borrowings against the remaining eligible source pool.
3. **Level 3 precision pass:** verify that Advanced entries are useful current C1-oriented vocabulary rather than rare subtitle vocabulary.
4. **Example rewrite:** write one meaning-bearing example for every retained noun after the headword set is stable.
5. **Final provenance + CI:** promote only the fully reviewed final set to `release-reviewed`, then enforce the hard gate in `certify:bridge`.

## Non-goals

- Do not rewrite the original Challenge corpus as part of V2-3.
- Do not claim official Goethe B2/C1 list membership.
- Do not change SRS, scoring, track architecture, progress migration, or visual design.
- Do not sacrifice lexical quality merely to force article balance; the current article distribution is descriptive, not a target quota.

## V2-3 exit criteria

V2-3 is complete only when:

- **1,000 / 1,000** Bridge entries are editorially `release-reviewed`;
- **1,000 / 1,000** have explicit reviewed sense metadata;
- **1,000 / 1,000** have meaning-bearing reviewed German examples;
- **0** blocked/noisy learner glosses remain;
- **0** unresolved gender/sense ambiguities remain;
- **0** Challenge overlaps remain;
- level counts remain **400 / 350 / 250**;
- source targeting remains **600 B2 / 400 C1** unless deliberately versioned otherwise;
- the stricter `certify:bridge` gate and full browser suite pass on the certified commit.
