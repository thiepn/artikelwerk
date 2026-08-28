# Real-device content verification

## Automated device-profile certification

The CI matrix covers:

| Profile | Viewport | Touch/mobile | Automated content checks |
|---|---:|---|---|
| Small phone | 360×640 | yes | required |
| Modern phone | 390×844 | yes | required |
| Large Android | 412×915 | yes | required |
| Phone landscape | 844×390 | yes | required |
| Tablet | 768×1024 | yes | required |
| Desktop | 1440×900 | no | required |

The test verifies the seven former translation fallbacks, representative editorially corrected derived glosses, Primat, Dossier, Erbe, Mangel, Hinweis, practice rendering, content-certification labels, no unavailable glosses, no external runtime requests, no console errors, and viewport containment. Screenshots are retained as CI artifacts.

## Physical-device release gate

Physical-device verification cannot be executed from the repository automation environment. Before the final public release, manually run the same acceptance flow on at least:

- one current Android/Chrome phone;
- one older/small Android device;
- one iPhone/Safari device;
- one tablet;
- one desktop Chromium browser.

For each device, verify: no page movement during practice, all feedback remains accessible, the English gloss is correct, the More details panel is usable, portrait/landscape transitions recover correctly, production keyboard behavior is stable, and refresh preserves progress.

Final release status: **automated device-profile certification complete; physical-device acceptance pending**.
