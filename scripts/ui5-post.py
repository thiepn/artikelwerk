from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "scripts" / "verify-source.mjs"
SHELL = ROOT / "tests" / "app-shell.mjs"

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

print("Updated legacy UI2/UI4 assertions for UI5")
