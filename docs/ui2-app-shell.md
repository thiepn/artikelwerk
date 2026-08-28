# UI2 — App Shell, Navigation & Main-Screen Hierarchy

## Goal

Make Artikelwerk behave and read like a focused language-learning application rather than a generic analytics dashboard, without changing the learning engine or certified content.

## Application shell

### Desktop

The brand, primary navigation, and utility actions now share one integrated header. Primary destinations are:

1. **Practice** — the learning task.
2. **Progress** — learner-facing interpretation of statistics.
3. **Vocabulary** — the reviewed noun library.

The navigation uses the existing tab semantics and IDs, preserving keyboard behavior and application state.

### Mobile

Primary navigation moves to a persistent bottom bar. The compact top bar retains identity, data controls, and theme control. This separates global navigation from the learning content and avoids a sticky tab strip competing with the first practice card.

The dedicated practice dialog remains above the app shell and hides the bottom navigation while open.

## Practice hierarchy

The Practice screen now reads in this order:

1. **Primary practice hero** — one dominant Start practice action.
2. **Today's review** — due/relearning state and a direct review action.
3. **Session setup** — mode, format, difficulty, and length controls.

The setup controls remain visible and fully functional; they are visually secondary rather than hidden behind disclosure UI.

## Progress hierarchy

The Statistics destination is labeled **Progress** in navigation while retaining the existing internal view ID. A concise screen heading explains the purpose before presenting metrics.

## Vocabulary hierarchy

Vocabulary receives a screen heading before filters and tables, so search/filter controls no longer appear without context.

## Accessibility and responsive rules

- Existing `role=tablist`, `role=tab`, `aria-selected`, and `aria-controls` relationships are preserved.
- Mobile navigation retains 44px+ touch targets.
- No horizontal document overflow is allowed at certified widths.
- Dedicated practice remains a fixed no-scroll modal and remains visually above the shell.
- Navigation remains keyboard-addressable on desktop.
- No new network dependencies, icon fonts, or remote UI libraries were introduced.

## UI3 handoff

UI3 should polish the individual screens within this hierarchy: practice-card presentation, answer/feedback states, vocabulary rows/details, and progress visualizations. It should not rework the global shell again unless device testing exposes a concrete usability defect.
