# UI1 — Artikelwerk visual identity

Status: implemented foundation. This document defines the visual contract for UI2–UI4.

## Product character

Artikelwerk is an advanced language-learning tool, not a generic dashboard and not a game skin. The visual target is **editorial, calm, confident, and study-focused**. It should feel appropriate for an adult learner doing serious C1/C2 work while remaining approachable on a phone.

### Inspiration principles

The direction is informed by current language-learning products without copying their visual assets:

- **Babbel** — mature course framing, short structured lessons, clear grammar support and progress visibility: https://www.babbel.com/mobile
- **Busuu** — real-life language positioning, expert-designed learning structure and straightforward progress framing: https://www.busuu.com/en
- **Drops** — visual craft, simplicity and a vocabulary-first product identity: https://languagedrops.com/about
- **Duolingo** — immediate feedback and clear progress cues only; Artikelwerk deliberately does not adopt mascot-driven or reward-heavy gamification: https://www.duolingo.com/nojs/splash

## Brand mark

The Artikelwerk mark is a custom geometric **A** on a deep-teal field. It is intentionally flat and legible at favicon scale.

Rules:

- no gradients;
- no shadows inside the mark;
- no tiny text such as “der / die / das” inside the icon;
- preserve the cream-on-teal contrast;
- use the SVG as the canonical vector source;
- raster derivatives exist only for browser/platform compatibility.

## Color system

### Light

| Token | Value | Use |
|---|---|---|
| `--bg` | `#f6f3ec` | warm page background |
| `--surface` | `#fffdf8` | primary surfaces |
| `--surface-2` | `#efede6` | secondary controls / hover |
| `--text` | `#1c2421` | primary text |
| `--muted` | `#68716c` | supporting text |
| `--border` | `#d8ddd8` | default separators |
| `--accent` | `#1d6f5f` | primary action / selection |
| `--accent-soft` | `#e5f2ee` | restrained accent background |

### Dark

| Token | Value | Use |
|---|---|---|
| `--bg` | `#131817` | page background |
| `--surface` | `#1a211f` | primary surfaces |
| `--surface-2` | `#232b28` | secondary controls / hover |
| `--text` | `#f2f4ef` | primary text |
| `--muted` | `#9fa9a3` | supporting text |
| `--border` | `#333d38` | separators |
| `--accent` | `#78c8b4` | primary action / selection |
| `--accent-soft` | `#203a34` | restrained accent background |

Semantic green, red and amber remain reserved for correct, incorrect and caution states. They are not decorative palette colors.

## Typography

Artikelwerk uses a local system UI stack. No remote web font is required, preserving offline behavior and avoiding visual loading shifts.

Hierarchy principles:

- noun/question content is the dominant type on practice screens;
- page titles are compact rather than marketing-sized;
- metadata labels are small and quiet;
- body copy uses normal sentence case;
- uppercase is reserved for short metadata labels, never long paragraphs;
- default interface weights should stay between 600 and 800 instead of making every control extra-bold.

## Shape and elevation

- core radius: `12px`;
- small controls: `9px`;
- large containers only: up to `16px`;
- pills are reserved for real chips/badges, not ordinary buttons or navigation;
- panels use a 1px border and very light elevation;
- large floating shadows, glassmorphism and blurred translucent cards are prohibited.

## Navigation foundation

The main tabs are now flat and separated by a bottom rule. The active section is communicated with a simple accent underline rather than a rounded segmented-control container. UI2 may change the app-shell structure, but it must preserve this restrained visual language.

## Interaction foundation

- touch targets remain at least 44px where practical;
- hover/pressed feedback is short and subtle;
- primary actions use the single accent color;
- correct/incorrect feedback may use semantic color but must not shift layout;
- focus rings remain clearly visible in both themes;
- no decorative motion should compete with learning content.

## Explicit anti-patterns

Do not introduce:

- gradients;
- glassmorphism;
- neon glow;
- oversized “AI dashboard” cards;
- arbitrary accent colors per section;
- rounded rectangles around every piece of text;
- decorative empty hero areas inside the application;
- emoji as primary UI icons;
- mascot or streak mechanics solely for decoration.

## UI2 handoff

UI2 should use this foundation to redesign the app shell and navigation. The next phase should improve header density, mobile navigation, page hierarchy and the first-screen “what should I do now?” flow without changing learning behavior.
