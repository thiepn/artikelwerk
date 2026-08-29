# UI5.1 — Visual Acceptance Fixes

UI5.1 is a targeted acceptance pass on the editorial UI5 direction. It does not redesign the product or alter vocabulary, scoring, SRS, translations, or session semantics.

## Acceptance fixes

### Practice typography

- Standard and production prompts must never use arbitrary mid-word wrapping.
- Long German compounds are dynamically fitted to the available practice width.
- `Untersuchungsgegenstand` is a required regression case on desktop and mobile.
- Context sentences remain normally wrapping and may use German hyphenation where appropriate.
- Desktop maximum noun scale and question padding are reduced so Practice reads as a learning surface rather than a poster.

### Mobile navigation clearance

- The fixed bottom navigation keeps a dedicated document-flow exclusion zone.
- Deep focused controls must be scrollable fully above the navigation.
- Existing focus-not-obscured behavior remains mandatory.

### Mobile Vocabulary filters

- Search remains immediately visible.
- The five primary secondary filters are collapsed behind a single `Filters` disclosure on narrow screens.
- The disclosure shows an active-filter count.
- Desktop keeps the full primary filter row.
- Existing filter IDs and filter semantics remain unchanged.

### Progress hierarchy

- Core overview, activity, forgotten words, accuracy, missed words, learning status, and confidence remain directly visible.
- Lower diagnostic material (response speed, confusion matrix, stubborn-word analysis) is collapsed behind `More learning diagnostics` on mobile and remains expanded on desktop.
- Mobile helper copy is increased to a readable minimum and section spacing is strengthened.

## Certification

`tests/visual-acceptance.mjs` verifies the UI5.1 acceptance blockers in addition to all existing Practice, content, shell, surface, accessibility, and UI5 editorial suites. Rendered UI5.1 screenshots are uploaded for visual review before merge.
