# UI5 — Editorial Interface Rebuild

UI5 supersedes the visual direction established in UI1–UI4 while preserving their responsive and accessibility behavior. The previous warm-teal implementation still used the visual grammar of a generated SaaS dashboard: a large rounded hero card, separate rounded support cards, pill controls, mini KPI tiles, and nested card surfaces. UI5 removes that grammar rather than recoloring it.

## Visual direction

- paper-like neutral canvas with ink typography
- restrained terracotta action accent (`#d45532`)
- local serif display stack for learning words and major headings
- thin rules and whitespace replace card containers
- 4–6px radii only where controls need shape; structural surfaces are flat
- no hero card, metric-card grid, article chips, or confidence pills
- no gradients, glass effects, neon, decorative blobs, or mascot language

## Surfaces

The Practice landing is a typographic page with a flat review queue and inline session settings. Fullscreen Practice is a study canvas, not a card. Progress is formatted as a report. Vocabulary behaves like a reference table with a right-side detail sheet.

## Favicon

The green rounded-square mark is replaced by an editorial book-spine A: warm paper, terracotta vertical rule, and black letterform. SVG, ICO, PNG, Apple touch, and manifest icons are regenerated together.

## Acceptance

`tests/editorial-ui.mjs` rejects the reappearance of the key dashboard patterns and captures desktop/mobile evidence for Practice, Progress, and Vocabulary. Existing content, practice, shell, surface, and accessibility suites remain mandatory.
