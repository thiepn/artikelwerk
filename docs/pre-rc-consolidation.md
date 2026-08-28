# Pre-RC main consolidation

The UI/content work from PRs #4–#8 was developed as a stacked branch chain. Because the parent PRs were merged before their child branches were merged back into them, GitHub recorded those child PRs as merged without propagating their later commits to `main`.

This branch is therefore being consolidated directly into `main` before RC.

The consolidation includes:

- certified local vocabulary content and provenance
- corrected generated examples and targeted inflection fixes
- Artikelwerk favicon / touch-icon / manifest asset family
- UI1 visual identity and theme foundation
- UI2 application shell and navigation hierarchy
- UI3 Practice, Vocabulary, and Progress polish
- UI4 motion, focus, accessibility, and responsive finish
- permanent read-only CI for all five browser suites

No additional learning, scoring, SRS, or vocabulary behavior is introduced by the consolidation itself.
