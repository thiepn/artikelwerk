from pathlib import Path
import json
import re
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
BUILD = ROOT / "scripts" / "build.mjs"
VERIFY = ROOT / "scripts" / "verify-source.mjs"
README = ROOT / "README.md"
DOCS = ROOT / "docs" / "ui1-visual-identity.md"

ACCENT = "#1d6f5f"
ACCENT_DARK = "#12473d"
CREAM = "#fffaf0"
BG = "#f6f3ec"
DARK_BG = "#131817"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


html = INDEX.read_text(encoding="utf-8")

# Head identity + favicon metadata.
description = '<meta name="description" content="A focused C1/C2 German noun-gender trainer with adaptive review, contextual practice, and productive recall." />'
head_addition = '''<meta name="theme-color" content="#1d6f5f" />
<meta name="apple-mobile-web-app-title" content="Artikelwerk" />
<link rel="icon" href="favicon.svg" type="image/svg+xml" />
<link rel="icon" href="favicon-32x32.png" sizes="32x32" type="image/png" />
<link rel="icon" href="favicon-16x16.png" sizes="16x16" type="image/png" />
<link rel="shortcut icon" href="favicon.ico" />
<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png" />
<link rel="mask-icon" href="safari-pinned-tab.svg" color="#1d6f5f" />
<link rel="manifest" href="site.webmanifest" />'''
if 'href="favicon.svg"' not in html:
    html = replace_once(html, description, description + "\n" + head_addition, "favicon metadata")

# Visual tokens: warm editorial foundation, one accent, flatter surfaces.
theme_pattern = re.compile(r'  :root\{\n.*?  \}\n  \[data-theme="dark"\]\{\n.*?  \}\n  \*\{box-sizing:border-box\}', re.S)
new_theme = '''  :root{
    color-scheme:light;
    --bg:#f6f3ec; --surface:#fffdf8; --surface-2:#efede6; --surface-3:#e6e3db;
    --text:#1c2421; --text-soft:#39443f; --muted:#68716c;
    --border:#d8ddd8; --border-strong:#bcc6c0;
    --accent:#1d6f5f; --accent-2:#16594c; --accent-dark:#12473d; --accent-soft:#e5f2ee;
    --good:#2d7a4d; --good-bg:#eaf5ee; --bad:#b34b43; --bad-bg:#fbefed; --warn:#95681f;
    --shadow-sm:0 1px 2px rgba(28,36,33,.055);
    --shadow:0 1px 2px rgba(28,36,33,.055),0 10px 28px rgba(28,36,33,.045);
    --radius-sm:9px; --radius:12px; --radius-lg:16px;
    --font-ui:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  }
  [data-theme="dark"]{
    color-scheme:dark;
    --bg:#131817; --surface:#1a211f; --surface-2:#232b28; --surface-3:#2a3430;
    --text:#f2f4ef; --text-soft:#d6ddd8; --muted:#9fa9a3;
    --border:#333d38; --border-strong:#4b5952;
    --accent:#78c8b4; --accent-2:#91d7c5; --accent-dark:#b1e5d7; --accent-soft:#203a34;
    --good:#72c98e; --good-bg:#1d3527; --bad:#ef9186; --bad-bg:#3a2422; --warn:#deb86e;
    --shadow-sm:0 1px 2px rgba(0,0,0,.18);
    --shadow:0 1px 2px rgba(0,0,0,.22),0 12px 30px rgba(0,0,0,.16);
  }
  *{box-sizing:border-box}'''
html, n = theme_pattern.subn(new_theme, html, count=1)
if n != 1:
    raise RuntimeError(f"theme token block: expected one match, found {n}")

replacements = {
    'html,body{margin:0;min-height:100%;background:var(--bg);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}':
    'html,body{margin:0;min-height:100%;background:var(--bg);color:var(--text);font-family:var(--font-ui);text-rendering:optimizeLegibility;-webkit-font-smoothing:antialiased}',
    'button{cursor:pointer}':
    'button{cursor:pointer;-webkit-tap-highlight-color:transparent}',
    '.app{max-width:1180px;margin:0 auto;padding:20px}':
    '.app{max-width:1160px;margin:0 auto;padding:24px}',
    'header{display:flex;gap:16px;align-items:center;justify-content:space-between;margin-bottom:20px}':
    'header{display:flex;gap:16px;align-items:center;justify-content:space-between;margin-bottom:18px}',
    '.brand{display:flex;align-items:center;gap:12px}':
    '.brand{display:flex;align-items:center;gap:11px}',
    '.brand-mark{width:40px;height:40px;border-radius:12px;background:var(--text);color:var(--bg);display:grid;place-items:center;font-weight:850;letter-spacing:-.04em}':
    '.brand-mark{width:40px;height:40px;border-radius:10px;overflow:hidden;flex:0 0 auto;box-shadow:var(--shadow-sm)} .brand-mark img{display:block;width:100%;height:100%}',
    '.brand h1{font-size:1.05rem;margin:0;letter-spacing:-.02em}':
    '.brand h1{font-size:1.06rem;margin:0;font-weight:780;letter-spacing:-.025em}',
    '.brand p{font-size:.8rem;color:var(--muted);margin:2px 0 0}':
    '.brand p{font-size:.78rem;color:var(--muted);margin:2px 0 0}',
    '.icon-btn,.ghost-btn,.primary-btn,.danger-btn{border:1px solid var(--border);background:var(--surface);color:var(--text);border-radius:12px;padding:10px 13px;font-weight:700}':
    '.icon-btn,.ghost-btn,.primary-btn,.danger-btn{border:1px solid var(--border);background:var(--surface);color:var(--text);border-radius:var(--radius-sm);padding:10px 13px;font-weight:700;transition:background .14s ease,border-color .14s ease,transform .14s ease,color .14s ease}',
    '.icon-btn:hover,.ghost-btn:hover{background:var(--surface-2)}':
    '.icon-btn:hover,.ghost-btn:hover{background:var(--surface-2);border-color:var(--border-strong)}',
    '.primary-btn{background:var(--accent);color:white;border-color:var(--accent);padding:11px 16px}':
    '.primary-btn{background:var(--accent);color:#fff;border-color:var(--accent);padding:11px 16px}',
    '.primary-btn:hover{background:var(--accent-2)}':
    '.primary-btn:hover{background:var(--accent-2);border-color:var(--accent-2)}',
    '.tabs{display:flex;gap:8px;background:var(--surface);padding:6px;border:1px solid var(--border);border-radius:14px;margin-bottom:18px;overflow:auto}':
    '.tabs{display:flex;gap:3px;background:transparent;padding:0;border:0;border-bottom:1px solid var(--border);border-radius:0;margin-bottom:20px;overflow:auto}',
    '.tab{border:0;background:transparent;color:var(--muted);padding:9px 14px;border-radius:10px;font-weight:750;white-space:nowrap}':
    '.tab{border:0;background:transparent;color:var(--muted);padding:10px 13px 11px;border-radius:0;font-weight:720;white-space:nowrap;box-shadow:inset 0 -2px 0 transparent}',
    '.tab.active{background:var(--surface-2);color:var(--text)}':
    '.tab.active{background:transparent;color:var(--text);box-shadow:inset 0 -2px 0 var(--accent)}',
    '.panel{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow)}':
    '.panel{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow-sm)}',
    '.control label{display:block;font-size:.72rem;color:var(--muted);font-weight:750;margin:0 0 5px 3px;text-transform:uppercase;letter-spacing:.06em}':
    '.control label{display:block;font-size:.71rem;color:var(--muted);font-weight:740;margin:0 0 6px 2px;text-transform:uppercase;letter-spacing:.055em}',
    'select,input[type="search"]{width:100%;border:1px solid var(--border);background:var(--surface-2);color:var(--text);padding:11px 12px;border-radius:11px;outline:none}':
    'select,input[type="search"]{width:100%;border:1px solid var(--border);background:var(--surface);color:var(--text);padding:11px 12px;border-radius:var(--radius-sm);outline:none;box-shadow:inset 0 1px 0 rgba(255,255,255,.025)}',
    'select:focus,input:focus,button:focus-visible{outline:3px solid color-mix(in srgb,var(--accent) 30%,transparent);outline-offset:2px}':
    'select:focus,input:focus,button:focus-visible{outline:3px solid color-mix(in srgb,var(--accent) 28%,transparent);outline-offset:2px;border-color:var(--accent)}',
    '.quiz-card{min-height:520px;padding:34px;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden}':
    '.quiz-card{min-height:520px;padding:34px;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden}',
    '.badge{display:inline-flex;align-items:center;border:1px solid var(--border);background:var(--surface-2);padding:6px 9px;border-radius:999px;color:var(--muted);font-size:.78rem;font-weight:800}':
    '.badge{display:inline-flex;align-items:center;border:1px solid var(--border);background:var(--surface);padding:6px 9px;border-radius:999px;color:var(--muted);font-size:.78rem;font-weight:760}',
    '.answer-btn{border:1px solid var(--border);background:var(--surface-2);color:var(--text);padding:18px 12px;border-radius:15px;font-weight:850;font-size:1.1rem;transition:transform .12s ease,background .12s ease,border .12s ease}':
    '.answer-btn{border:1px solid var(--border);background:var(--surface);color:var(--text);padding:18px 12px;border-radius:var(--radius);font-weight:800;font-size:1.1rem;box-shadow:0 1px 0 color-mix(in srgb,var(--border) 75%,transparent);transition:transform .12s ease,background .12s ease,border-color .12s ease}',
    '.answer-btn:hover{transform:translateY(-1px);border-color:var(--muted)}':
    '.answer-btn:hover{transform:translateY(-1px);background:var(--surface-2);border-color:var(--border-strong)}',
}
for old, new in replacements.items():
    html = replace_once(html, old, new, old[:48])

html = replace_once(
    html,
    '<div class="brand-mark" aria-hidden="true">A</div>',
    '<div class="brand-mark" aria-hidden="true"><img src="favicon.svg" alt="" width="40" height="40"></div>',
    "brand mark image",
)

foundation_marker = '  *{box-sizing:border-box}\n'
foundation_add = '''  *{box-sizing:border-box}
  ::selection{background:var(--accent-soft);color:var(--text)}
  body{accent-color:var(--accent)}
  a{color:var(--accent-2)}
'''
html = replace_once(html, foundation_marker, foundation_add, "foundation CSS")
INDEX.write_text(html, encoding="utf-8")

# Brand assets.
favicon_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="Artikelwerk">
  <rect width="512" height="512" rx="112" fill="#1d6f5f"/>
  <path d="M151 370 239 151c6-15 28-15 34 0l88 219" fill="none" stroke="#fffaf0" stroke-width="44" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M198 286h116" fill="none" stroke="#fffaf0" stroke-width="38" stroke-linecap="round"/>
</svg>\n'''
(ROOT / "favicon.svg").write_text(favicon_svg, encoding="utf-8")

pinned_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <path d="M151 370 239 151c6-15 28-15 34 0l88 219" fill="none" stroke="#000" stroke-width="54" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M198 286h116" fill="none" stroke="#000" stroke-width="48" stroke-linecap="round"/>
</svg>\n'''
(ROOT / "safari-pinned-tab.svg").write_text(pinned_svg, encoding="utf-8")

manifest = {
    "name": "Artikelwerk",
    "short_name": "Artikelwerk",
    "description": "C1/C2 German noun-gender trainer",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "background_color": BG,
    "theme_color": ACCENT,
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
    ],
}
(ROOT / "site.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def draw_mark(size: int, rounded: bool, transparent: bool):
    scale = 4
    s = size * scale
    mode = "RGBA" if transparent else "RGB"
    bg = (0, 0, 0, 0) if transparent else (29, 111, 95)
    image = Image.new(mode, (s, s), bg)
    draw = ImageDraw.Draw(image)
    accent = (29, 111, 95, 255) if transparent else (29, 111, 95)
    cream = (255, 250, 240, 255) if transparent else (255, 250, 240)
    if rounded:
        draw.rounded_rectangle((0, 0, s - 1, s - 1), radius=round(s * 112 / 512), fill=accent)
    elif transparent:
        draw.rectangle((0, 0, s - 1, s - 1), fill=accent)
    # Geometric A: draw at 4x and downsample for clean small favicons.
    pts = [(151, 370), (256, 128), (361, 370)]
    pts = [(round(x * s / 512), round(y * s / 512)) for x, y in pts]
    width = round(44 * s / 512)
    draw.line(pts, fill=cream, width=width, joint="curve")
    r = width // 2
    for x, y in (pts[0], pts[-1]):
        draw.ellipse((x-r, y-r, x+r, y+r), fill=cream)
    cross = [(198, 286), (314, 286)]
    cross = [(round(x * s / 512), round(y * s / 512)) for x, y in cross]
    cross_w = round(38 * s / 512)
    draw.line(cross, fill=cream, width=cross_w)
    rr = cross_w // 2
    for x, y in cross:
        draw.ellipse((x-rr, y-rr, x+rr, y+rr), fill=cream)
    image = image.resize((size, size), Image.Resampling.LANCZOS)
    return image

for size, name in [(16, "favicon-16x16.png"), (32, "favicon-32x32.png")]:
    draw_mark(size, rounded=True, transparent=True).save(ROOT / name, "PNG", optimize=True)

draw_mark(180, rounded=False, transparent=False).save(ROOT / "apple-touch-icon.png", "PNG", optimize=True)
draw_mark(192, rounded=False, transparent=False).save(ROOT / "icon-192.png", "PNG", optimize=True)
draw_mark(512, rounded=False, transparent=False).save(ROOT / "icon-512.png", "PNG", optimize=True)
draw_mark(256, rounded=True, transparent=True).save(ROOT / "favicon.ico", format="ICO", sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])

# Deterministic release includes identity assets.
build = BUILD.read_text(encoding="utf-8")
asset_lines = '''  ['favicon.svg', 'favicon.svg'],
  ['favicon.ico', 'favicon.ico'],
  ['favicon-16x16.png', 'favicon-16x16.png'],
  ['favicon-32x32.png', 'favicon-32x32.png'],
  ['apple-touch-icon.png', 'apple-touch-icon.png'],
  ['safari-pinned-tab.svg', 'safari-pinned-tab.svg'],
  ['site.webmanifest', 'site.webmanifest'],
  ['icon-192.png', 'icon-192.png'],
  ['icon-512.png', 'icon-512.png'],
'''
if "['favicon.svg', 'favicon.svg']" not in build:
    build = replace_once(build, "  ['.nojekyll', '.nojekyll'],\n", "  ['.nojekyll', '.nojekyll'],\n" + asset_lines, "release identity assets")
BUILD.write_text(build, encoding="utf-8")

# Source certification now guards the UI1 identity contract.
verify = VERIFY.read_text(encoding="utf-8")
ui_checks = '''requireFragment(html, '<link rel="icon" href="favicon.svg" type="image/svg+xml" />', 'SVG favicon');
requireFragment(html, '<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png" />', 'Apple touch icon');
requireFragment(html, '<link rel="manifest" href="site.webmanifest" />', 'web app manifest');
requireFragment(html, '--accent:#1d6f5f', 'UI1 primary accent');
requireFragment(html, '--bg:#f6f3ec', 'UI1 warm light background');
requireFragment(html, '--bg:#131817', 'UI1 dark background');
requireFragment(html, '--radius:12px', 'UI1 restrained radius');
requireFragment(html, 'box-shadow:var(--shadow-sm)', 'UI1 restrained surface elevation');
requireFragment(html, '<img src="favicon.svg" alt="" width="40" height="40">', 'UI1 brand mark');

const uiAssetPaths = [
  'favicon.svg','favicon.ico','favicon-16x16.png','favicon-32x32.png','apple-touch-icon.png',
  'safari-pinned-tab.svg','site.webmanifest','icon-192.png','icon-512.png','docs/ui1-visual-identity.md'
];
for (const relativePath of uiAssetPaths) {
  try { await access(join(rootDir, relativePath)); }
  catch { fail(`Missing UI1 identity asset: ${relativePath}`); }
}
const manifest = JSON.parse(await readFile(join(rootDir, 'site.webmanifest'), 'utf8'));
if (manifest?.name !== 'Artikelwerk' || manifest?.theme_color !== '#1d6f5f') fail('Invalid Artikelwerk manifest identity.');
if (!Array.isArray(manifest.icons) || !manifest.icons.some(icon => icon.sizes === '192x192') || !manifest.icons.some(icon => icon.sizes === '512x512')) fail('Manifest must expose 192px and 512px icons.');
const faviconSvg = await readFile(join(rootDir, 'favicon.svg'), 'utf8');
if (faviconSvg.includes('gradient') || !faviconSvg.includes('#1d6f5f') || !faviconSvg.includes('#fffaf0')) fail('Favicon must use the flat UI1 brand palette without gradients.');
'''
anchor = "requireFragment(html, '<title>Artikelwerk', 'application title');\n"
if "UI1 primary accent" not in verify:
    verify = replace_once(verify, anchor, anchor + ui_checks, "UI1 source verification")
VERIFY.write_text(verify, encoding="utf-8")

spec = '''# UI1 — Artikelwerk visual identity

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
'''
DOCS.parent.mkdir(parents=True, exist_ok=True)
DOCS.write_text(spec, encoding="utf-8")

readme = README.read_text(encoding="utf-8")
section = '''\n## Visual identity\n\nUI1 establishes Artikelwerk's original visual foundation: warm editorial neutrals, a single deep-teal accent, restrained borders/radii/elevation, a geometric `A` brand mark, full favicon/platform icon coverage, and light/dark theme tokens. See `docs/ui1-visual-identity.md`.\n'''
if "## Visual identity" not in readme:
    readme += section
README.write_text(readme, encoding="utf-8")

print("UI1 migration applied: theme tokens, favicon family, manifest, build assets, verification, and design specification.")
