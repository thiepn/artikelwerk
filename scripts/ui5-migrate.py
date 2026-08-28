from pathlib import Path
import base64
import json

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
VERIFY = ROOT / "scripts" / "verify-source.mjs"
PACKAGE = ROOT / "package.json"
README = ROOT / "README.md"
MANIFEST = ROOT / "site.webmanifest"
STYLE = ROOT / "scripts" / "ui5-style.css"
ICONS = ROOT / "scripts" / "ui5-icons.json"
A11Y_TEST = ROOT / "tests" / "accessibility-finish.mjs"

html = INDEX.read_text(encoding="utf-8")
if "/* UI5 — editorial rebuild" in html:
    raise SystemExit("UI5 already applied")

replacements = [
    (
        '<span class="section-kicker">Focused practice</span>\n          <h2 id="practiceHeroTitle">Make German articles automatic.</h2>\n          <p>Train difficult C1/C2 nouns in a dedicated screen where the word, English meaning, answer choices, and feedback stay in one place.</p>',
        '<span class="section-kicker">C1/C2 noun gender</span>\n          <h2 id="practiceHeroTitle">Practice German articles.</h2>\n          <p>One word at a time. Choose the article, check the English meaning when you need it, and keep moving.</p>',
    ),
    ('<span class="section-kicker">Spaced repetition</span>', '<span class="section-kicker">Review queue</span>'),
    (
        '<span class="section-kicker">Session setup</span>\n            <h2 id="practiceSetupHeading">Choose how to practice</h2>\n            <p>Keep the defaults for a quick session, or adjust the mode, format, level, and length.</p>',
        '<span class="section-kicker">Session settings</span>\n            <h2 id="practiceSetupHeading">Choose a session</h2>\n            <p>Adjust only what you need. The defaults are ready to use.</p>',
    ),
    (
        '<span class="section-kicker">Progress</span>\n        <h2>Your learning picture</h2>\n        <p>See what is due, where article recall is improving, and which words need another pass.</p>',
        '<span class="section-kicker">Learning record</span>\n        <h2>Progress</h2>\n        <p>Recall, review load, response speed, and the words that still need work.</p>',
    ),
    (
        '<span class="section-kicker">Vocabulary</span>\n        <h2>Your reviewed noun library</h2>\n        <p>Browse 1,000 advanced nouns with certified English glosses, article guidance, examples, and learning status.</p>',
        '<span class="section-kicker">Reference</span>\n        <h2>Vocabulary</h2>\n        <p>1,000 reviewed C1/C2 nouns with English meanings, examples, grammar notes, and learning status.</p>',
    ),
    ('<meta name="theme-color" content="#1d6f5f" />', '<meta name="theme-color" content="#d45532" />'),
    ('<link rel="mask-icon" href="safari-pinned-tab.svg" color="#1d6f5f" />', '<link rel="mask-icon" href="safari-pinned-tab.svg" color="#d45532" />'),
    ('themeMeta.setAttribute("content",dark?"#131817":"#1d6f5f")', 'themeMeta.setAttribute("content",dark?"#181614":"#d45532")'),
]
for old, new in replacements:
    if old not in html:
        raise SystemExit(f"Missing UI5 migration anchor: {old[:80]}")
    html = html.replace(old, new, 1)

style = STYLE.read_text(encoding="utf-8")
if "\n</style>" not in html:
    raise SystemExit("Closing style tag missing")
html = html.replace("\n</style>", "\n" + style + "\n</style>", 1)
INDEX.write_text(html, encoding="utf-8")

favicon_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Artikelwerk">
  <rect width="64" height="64" fill="#f7f4ee"/>
  <rect width="9" height="64" fill="#d45532"/>
  <path d="M21 49 33 17h5l13 32h-6l-3-8H29l-3 8h-5Zm10-13h9l-4.6-12.5L31 36Z" fill="#191715"/>
</svg>
'''
mask_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <path d="M7 0h57v64H7zM21 49 33 17h5l13 32h-6l-3-8H29l-3 8h-5Zm10-13h9l-4.6-12.5L31 36Z"/>
</svg>
'''
(ROOT / "favicon.svg").write_text(favicon_svg, encoding="utf-8")
(ROOT / "safari-pinned-tab.svg").write_text(mask_svg, encoding="utf-8")
for name, data in json.loads(ICONS.read_text(encoding="utf-8")).items():
    (ROOT / name).write_bytes(base64.b64decode(data))

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
manifest["theme_color"] = "#d45532"
manifest["background_color"] = "#f7f4ee"
MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

verify = VERIFY.read_text(encoding="utf-8")
verify = verify.replace("manifest?.theme_color !== '#1d6f5f'", "manifest?.theme_color !== '#d45532'")
old_favicon = "if (faviconSvg.includes('gradient') || !faviconSvg.includes('#1d6f5f') || !faviconSvg.includes('#fffaf0')) fail('Favicon must use the flat UI1 brand palette without gradients.');"
new_favicon = "if (faviconSvg.includes('gradient') || !faviconSvg.includes('#d45532') || !faviconSvg.includes('#f7f4ee') || !faviconSvg.includes('#191715')) fail('Favicon must use the flat UI5 editorial palette without gradients.');"
if old_favicon not in verify:
    raise SystemExit("Favicon verification anchor missing")
verify = verify.replace(old_favicon, new_favicon, 1)
old_theme_verify = 'themeMeta.setAttribute(\\"content\\",dark?\\"#131817\\":\\"#1d6f5f\\")'
new_theme_verify = 'themeMeta.setAttribute(\\"content\\",dark?\\"#181614\\":\\"#d45532\\")'
verify = verify.replace(old_theme_verify, new_theme_verify)
ui4_anchor = "requireFragment(html, '/* UI4 — motion, interaction states, accessibility, and responsive finish */', 'UI4 finish style contract');\n"
ui5_verify = """requireFragment(html, '/* UI5 — editorial rebuild: typography and rules instead of dashboard cards */', 'UI5 editorial rebuild');
requireFragment(html, '--accent:#d45532', 'UI5 terracotta accent');
requireFragment(html, '--bg:#f7f4ee', 'UI5 paper background');
requireFragment(html, '--font-display:', 'UI5 editorial display typography');
requireFragment(html, '.practice-hero{display:block', 'UI5 borderless practice landing');
requireFragment(html, '.practice-hero-articles{display:none}', 'UI5 removed decorative article trio');
requireFragment(html, '.ui3-practice .quiz-card{border:0!important', 'UI5 cardless practice canvas');
requireFragment(html, '.article-chip{min-width:0;padding:0;border:0', 'UI5 typographic article labels');
"""
if ui5_verify not in verify:
    if ui4_anchor not in verify:
        raise SystemExit("UI4 verify anchor missing")
    verify = verify.replace(ui4_anchor, ui4_anchor + ui5_verify, 1)
doc_check = "try { await access(join(rootDir, 'docs', 'ui5-editorial-rebuild.md')); }\ncatch { fail('Missing UI5 editorial rebuild specification.'); }\n"
manifest_anchor = "const manifest = JSON.parse(await readFile(join(rootDir, 'site.webmanifest'), 'utf8'));\n"
if doc_check not in verify:
    if manifest_anchor not in verify:
        raise SystemExit("Manifest verify anchor missing")
    verify = verify.replace(manifest_anchor, doc_check + manifest_anchor, 1)
VERIFY.write_text(verify, encoding="utf-8")

package = json.loads(PACKAGE.read_text(encoding="utf-8"))
package["scripts"]["test:editorial-browser"] = "node tests/editorial-ui.mjs"
PACKAGE.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")

a11y = A11Y_TEST.read_text(encoding="utf-8")
a11y = a11y.replace("=== '#131817'", "=== '#181614'")
A11Y_TEST.write_text(a11y, encoding="utf-8")

README.write_text(
    README.read_text(encoding="utf-8").rstrip()
    + "\n\n## UI5 editorial rebuild\n\nUI5 supersedes the teal/card-based treatment with a typography-first editorial interface: paper neutrals, terracotta actions, serif learning typography, ruled sections instead of cards, a cardless fullscreen trainer, a report-like Progress view, and a reference-table Vocabulary view. The favicon family is replaced with the matching book-spine A mark. `tests/editorial-ui.mjs` certifies the anti-dashboard visual contract. See `docs/ui5-editorial-rebuild.md`.\n",
    encoding="utf-8",
)

print("Applied UI5 editorial rebuild")
