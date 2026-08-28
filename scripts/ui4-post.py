from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
VERIFY = ROOT / "scripts" / "verify-source.mjs"
TEST = ROOT / "tests" / "accessibility-finish.mjs"
DOC = ROOT / "docs" / "ui4-interaction-accessibility.md"

html = INDEX.read_text(encoding="utf-8")

anchor = '''    isOpen(){ return Boolean(this.element() && !this.element().hidden); },
    isTouchLike(){ return Boolean(navigator.maxTouchPoints>0 || window.matchMedia?.("(pointer: coarse)").matches); },
    open(){'''
replacement = '''    isOpen(){ return Boolean(this.element() && !this.element().hidden); },
    isTouchLike(){ return Boolean(navigator.maxTouchPoints>0 || window.matchMedia?.("(pointer: coarse)").matches); },
    backgroundNodes(){
      return [
        DOM.$(".app-header"),
        DOM.$("#practiceView > .practice-hero"),
        DOM.$("#practiceView > .practice-support-grid"),
        DOM.$("#statsView"),
        DOM.$("#libraryView")
      ].filter(Boolean);
    },
    setBackgroundInert(enabled){
      this.backgroundNodes().forEach(node=>{ node.inert=Boolean(enabled); });
    },
    open(){'''
if anchor not in html:
    raise SystemExit("PracticeScreen method anchor not found")
html = html.replace(anchor, replacement, 1)

open_anchor = '''      screen.setAttribute("aria-hidden","false");
      document.body.classList.add("practice-open");
      this.updateSubtitle();'''
open_replacement = '''      screen.setAttribute("aria-hidden","false");
      document.body.classList.add("practice-open");
      this.setBackgroundInert(true);
      this.updateSubtitle();'''
if open_anchor not in html:
    raise SystemExit("Practice open inert anchor not found")
html = html.replace(open_anchor, open_replacement, 1)

close_anchor = '''      screen.setAttribute("aria-hidden","true");
      document.body.classList.remove("practice-open");
      if(restoreFocus){'''
close_replacement = '''      screen.setAttribute("aria-hidden","true");
      document.body.classList.remove("practice-open");
      this.setBackgroundInert(false);
      if(restoreFocus){'''
if close_anchor not in html:
    raise SystemExit("Practice close inert anchor not found")
html = html.replace(close_anchor, close_replacement, 1)
INDEX.write_text(html, encoding="utf-8")

verify = VERIFY.read_text(encoding="utf-8")
verify_anchor = "requireFragment(html, 'this.setAppInert(true);', 'modal background inertness');\n"
verify_line = "requireFragment(html, 'this.setBackgroundInert(true);', 'practice background inertness');\n"
if verify_line not in verify:
    if verify_anchor not in verify:
        raise SystemExit("UI4 modal inert verification anchor not found")
    verify = verify.replace(verify_anchor, verify_anchor + verify_line, 1)
VERIFY.write_text(verify, encoding="utf-8")

test = TEST.read_text(encoding="utf-8")
practice_anchor = '''  await page.locator('#practiceScreen:not([hidden])').waitFor({ state: 'visible' });
  await page.waitForTimeout(30);
  assert(await page.evaluate(() => document.activeElement?.id) === 'nounPrompt', `${profile.name}: practice did not focus the exercise prompt`);'''
practice_replacement = '''  await page.locator('#practiceScreen:not([hidden])').waitFor({ state: 'visible' });
  await page.waitForTimeout(30);
  assert(await page.locator('.app-header').evaluate(el => el.inert === true), `${profile.name}: app chrome is not inert behind fullscreen practice`);
  assert(await page.locator('.practice-hero').evaluate(el => el.inert === true), `${profile.name}: practice setup remains interactive behind fullscreen practice`);
  assert(await page.evaluate(() => document.activeElement?.id) === 'nounPrompt', `${profile.name}: practice did not focus the exercise prompt`);'''
if practice_anchor not in test:
    raise SystemExit("UI4 practice isolation test anchor not found")
test = test.replace(practice_anchor, practice_replacement, 1)

close_anchor = '''  await page.keyboard.press('Escape');
  assert(await page.evaluate(() => document.activeElement?.id) === 'openPracticeBtn', `${profile.name}: practice close did not restore the launcher`);'''
close_replacement = '''  await page.keyboard.press('Escape');
  assert(await page.locator('.app-header').evaluate(el => el.inert === false), `${profile.name}: app chrome remained inert after practice close`);
  assert(await page.locator('.practice-hero').evaluate(el => el.inert === false), `${profile.name}: practice setup remained inert after practice close`);
  assert(await page.evaluate(() => document.activeElement?.id) === 'openPracticeBtn', `${profile.name}: practice close did not restore the launcher`);'''
if close_anchor not in test:
    raise SystemExit("UI4 practice close test anchor not found")
test = test.replace(close_anchor, close_replacement, 1)

forced_anchor = '''  await page.locator('#openPracticeBtn').click();
  const borderStyle = await page.locator('.answer-btn').first().evaluate(el => getComputedStyle(el).borderStyle);
  assert(borderStyle !== 'none', 'forced-colors: answer controls lost their structural border');'''
forced_replacement = '''  await page.locator('#openPracticeBtn').click();
  const borderStyle = await page.locator('.answer-btn').first().evaluate(el => getComputedStyle(el).borderStyle);
  assert(borderStyle !== 'none', 'forced-colors: answer controls lost their structural border');
  await page.locator('.answer-btn').first().click();
  const correct = page.locator('.answer-btn.correct').first();
  await correct.waitFor({ state: 'visible' });
  const correctBorder = await correct.evaluate(el => getComputedStyle(el).borderStyle);
  assert(correctBorder === 'double', `forced-colors: correct state is not structurally distinct (border-style ${correctBorder})`);'''
if forced_anchor not in test:
    raise SystemExit("UI4 forced-color test anchor not found")
test = test.replace(forced_anchor, forced_replacement, 1)
TEST.write_text(test, encoding="utf-8")

doc = DOC.read_text(encoding="utf-8")
doc_anchor = "- Opening a modal makes the background application inert.\n"
doc_line = "- Opening fullscreen Practice makes the app header, setup surface, and inactive views inert while leaving the practice dialog operable.\n"
if doc_line not in doc:
    if doc_anchor not in doc:
        raise SystemExit("UI4 document inertness anchor not found")
    doc = doc.replace(doc_anchor, doc_anchor + doc_line, 1)
DOC.write_text(doc, encoding="utf-8")

print("Hardened UI4 practice isolation and forced-colors state verification.")
