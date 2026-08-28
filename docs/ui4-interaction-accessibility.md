# UI4 — Motion, Interaction States, Accessibility & Responsive Finish

UI4 is the final interface-finish phase before release certification. It does not alter vocabulary, scoring, SRS scheduling, session semantics, or certified translations.

## Standards target

The implementation is aligned to WCAG 2.2 interaction concerns relevant to this static application, especially keyboard operability, Focus Not Obscured (2.4.11), Target Size (Minimum) (2.5.8), and robust visible focus. Artikelwerk intentionally keeps its own primary controls at 44 CSS px or larger even though WCAG 2.2 AA permits smaller targets in defined cases.

Reference material:

- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C WCAG 2.2 changes: https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
- MDN prefers-reduced-motion: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- MDN forced-colors: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/forced-colors

## Motion contract

- Motion is restrained to short opacity/2–4 px entrance transitions for ordinary views and dialogs; fullscreen Practice uses opacity-only motion so animation cannot create scrollable overflow.
- Hover lift is only applied where the device actually supports hover with a fine pointer.
- `prefers-reduced-motion: reduce` removes non-essential animations and transitions completely.
- Programmatic scrolling uses `auto` rather than `smooth` when reduced motion is requested.
- Timed-practice scoring and timing logic are unchanged.

## Interaction-state contract

- Buttons have consistent hover, active, selected, focus, and disabled states.
- Correct and incorrect article buttons remain distinguishable by border/state treatment, not color alone.
- Confidence selection remains an `aria-pressed` state.
- Theme switching exposes `aria-pressed` and synchronizes browser theme color.
- Native controls retain a minimum 44 px block size.

## Keyboard and focus contract

- Interactive focus uses a two-pixel solid outline with three-pixel offset.
- Mobile scroll padding/margins account for both the sticky top bar and fixed bottom navigation.
- Opening a modal makes the background application inert.
- Opening fullscreen Practice makes the app header, setup surface, and inactive views inert while leaving the practice dialog operable.
- Closing a modal restores the opener when it still exists.
- Reopening the already-visible practice surface (for example after a session-summary retry) does not overwrite the original practice return-focus target.
- Practice and modal Tab loops remain bounded to their active dialog.
- Arrow/Home/End tab navigation remains unchanged.

## Contrast and assistive display modes

- `prefers-contrast: more` strengthens focus and structural borders.
- `forced-colors: active` uses system focus colors and distinct border styles for correct/incorrect states.
- No essential state relies solely on shadows, gradients, or animation.

## Responsive finish

Certified layouts include:

- 320×568 narrow phone
- 360×640 small phone
- 390×844 modern phone
- 412×915 large phone
- 768×1024 tablet
- 844×390 touch landscape
- 1440×900 desktop

The 320 px profile also acts as the reflow stress case: document-level horizontal scrolling is forbidden; intentionally wide vocabulary tables may scroll only inside their table wrapper.

## Acceptance boundary

Automated browser certification can verify responsive geometry, keyboard behavior, reduced-motion emulation, forced-colors emulation, modal isolation, and focus placement. It does not replace physical-device, real screen-reader, or real browser/OS accessibility acceptance.

## Next phase

RC1 — Physical-device, browser, and assistive-technology acceptance followed by final release certification.
