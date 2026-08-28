# UI3 — Practice, Vocabulary & Progress Surface Polish

UI3 polishes the three learner-facing destinations on top of the UI1 identity and UI2 shell. It does not change scheduling, scoring, vocabulary content, translation certification, or the dedicated-practice interaction model.

## Practice

The dedicated practice screen is treated as a focused exercise workspace rather than a generic large card.

- question/session status is compact and secondary
- the noun remains the strongest typographic element
- article controls use a small keyboard-number cell plus a lowercase article label
- confidence controls are quiet pill controls rather than competing buttons
- English meaning uses the accent-tinted learning surface only when revealed
- feedback is a contained result surface with explicit success/error affordances
- the unfamiliar-word action is deliberately visually subordinate
- mobile continues to fit the answer, feedback, and next action without page scrolling

## Progress

The former ten equal KPI cards were replaced by one hierarchy:

1. overall accuracy as the primary learning signal
2. due / weak / mastered / seen as supporting metrics
3. answer count / streak / response speed / stubborn / relearning as compact secondary evidence

All ten existing metric IDs remain in the DOM so runtime calculations are unchanged. Detailed analytics remain below the overview, but their cards, activity counters, bars, and list items use flatter, denser presentation.

## Vocabulary

Vocabulary is treated as a reference library rather than a dashboard.

- quick filters are one compact filter surface
- advanced filters are a quieter disclosure
- the table surface is flatter and denser
- article chips use the single Artikelwerk accent rather than arbitrary per-gender colors
- row hover/selection affordance is subtle
- word detail uses restrained bordered fields and fewer nested visual cards
- mobile keeps search, primary filters, and word detail usable without document-level horizontal overflow

## Interaction and accessibility

UI3 preserves every existing runtime ID and ARIA relationship used by practice, progress, vocabulary, and dialogs. Touch targets remain at least 44px where actions require direct interaction. Ordinary dialogs remain above the sticky app chrome; the dedicated practice screen remains the highest application layer.

## Certification

`tests/surface-polish.mjs` certifies the UI3 contract on 1440×900 desktop plus 360×740, 390×844, and 412×915 mobile profiles. The suite checks practice-control structure, feedback containment, progress hierarchy, vocabulary filter/detail usability, modal stacking, viewport containment, horizontal overflow, and browser errors.

## UI4 handoff

UI4 should focus on motion, interaction states, empty/loading states, accessibility finishing, and cross-browser/zoom polish. It should not reintroduce card-heavy dashboards or decorative color systems.
