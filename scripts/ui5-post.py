from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
VERIFY = ROOT / "scripts" / "verify-source.mjs"
SHELL = ROOT / "tests" / "app-shell.mjs"

# Keep the visually quiet theme control while preserving the existing 44px touch-target floor.
html = INDEX.read_text(encoding="utf-8")
old_theme_size = '#themeBtn{width:40px;min-width:40px;height:40px;border:0;background:transparent;border-radius:50%;color:var(--muted)}'
new_theme_size = '#themeBtn{width:44px;min-width:44px;height:44px;border:0;background:transparent;border-radius:50%;color:var(--muted)}'
if old_theme_size not in html:
    raise SystemExit("Missing UI5 theme-target size anchor")
html = html.replace(old_theme_size, new_theme_size, 1)
INDEX.write_text(html, encoding="utf-8")

verify = VERIFY.read_text(encoding="utf-8")
changes = [
    ("requireFragment(html, 'Your learning picture', 'progress view heading');", "requireFragment(html, '<h2>Progress</h2>', 'progress view heading');"),
    ("requireFragment(html, 'Your reviewed noun library', 'vocabulary view heading');", "requireFragment(html, '<h2>Vocabulary</h2>', 'vocabulary view heading');"),
    ('requireFragment(html, \'themeMeta.setAttribute("content",dark?"#131817":"#1d6f5f")\', \'theme-color synchronization\');', 'requireFragment(html, \'themeMeta.setAttribute("content",dark?"#181614":"#d45532")\', \'theme-color synchronization\');'),
]
for old, new in changes:
    if old not in verify:
        raise SystemExit(f"Missing verifier UI5 anchor: {old}")
    verify = verify.replace(old, new, 1)
VERIFY.write_text(verify, encoding="utf-8")

shell = SHELL.read_text(encoding="utf-8")
changes = [
    ('assert.match((await page.locator("#statsView .view-heading h2").textContent())||"",/learning picture/i);', 'assert.equal(((await page.locator("#statsView .view-heading h2").textContent())||"").trim(),"Progress");'),
    ('assert.match((await page.locator("#libraryView .view-heading h2").textContent())||"",/reviewed noun library/i);', 'assert.equal(((await page.locator("#libraryView .view-heading h2").textContent())||"").trim(),"Vocabulary");'),
]
for old, new in changes:
    if old not in shell:
        raise SystemExit(f"Missing shell copy anchor: {old}")
    shell = shell.replace(old, new, 1)
SHELL.write_text(shell, encoding="utf-8")

print("Updated UI5 target sizing and legacy UI2/UI4 assertions")
