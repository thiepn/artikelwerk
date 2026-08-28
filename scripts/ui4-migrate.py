from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
VERIFY = ROOT / "scripts" / "verify-source.mjs"
PACKAGE = ROOT / "package.json"
README = ROOT / "README.md"
DOC = ROOT / "docs" / "ui4-interaction-accessibility.md"
TEST = ROOT / "tests" / "accessibility-finish.mjs"

html = INDEX.read_text(encoding="utf-8")

# Theme toggle semantics.
old_theme = '<button class="icon-btn" id="themeBtn" aria-label="Switch to dark mode" title="Switch to dark mode">◐</button>'
new_theme = '<button class="icon-btn" id="themeBtn" aria-label="Switch to dark mode" aria-pressed="false" title="Switch to dark mode">◐</button>'
if old_theme not in html:
    raise SystemExit("UI4 theme-button anchor not found")
html = html.replace(old_theme, new_theme, 1)

ui4_css = r'''

  /* UI4 — motion, interaction states, accessibility, and responsive finish */
  :root{--focus-ring:var(--accent);--motion-fast:120ms;--motion-standard:160ms}
  html{scroll-padding-block:84px 96px}
  :where(button,a[href],input,select,summary,[tabindex]:not([tabindex="-1"])){scroll-margin-block:84px 96px}
  :where(button,a[href],input,select,summary,[tabindex]:not([tabindex="-1"])):focus-visible{outline:2px solid var(--focus-ring);outline-offset:3px}
  .tab:focus-visible{outline:2px solid var(--focus-ring);outline-offset:3px}
  button,summary,.tab{touch-action:manipulation}
  .library-advanced summary{min-height:44px;display:flex;align-items:center;justify-content:space-between;gap:12px}
  .primary-btn,.ghost-btn,.icon-btn,.danger-btn,.answer-btn,.confidence-btn,.practice-close-btn,.practice-translation-btn,.tab{transition:background-color var(--motion-fast) ease,border-color var(--motion-fast) ease,color var(--motion-fast) ease,box-shadow var(--motion-fast) ease,transform var(--motion-fast) ease}
  :where(.primary-btn,.ghost-btn,.icon-btn,.danger-btn,.answer-btn,.confidence-btn,.practice-close-btn,.practice-translation-btn):active:not(:disabled){transform:translateY(1px)}
  .answer-btn:active:not(:disabled){transform:translateY(1px) scale(.995)}
  button:disabled,select:disabled,input:disabled{opacity:.52;filter:saturate(.68)}
  button:disabled{cursor:not-allowed}
  .answer-btn.correct{box-shadow:inset 0 0 0 1px var(--good)}
  .answer-btn.incorrect{box-shadow:inset 0 0 0 1px var(--bad)}
  .answer-btn.correct .answer-article::after{content:"  ✓";font-size:.78em}
  .answer-btn.incorrect .answer-article::after{content:"  ×";font-size:.78em}
  .confidence-btn[aria-pressed="true"]{box-shadow:0 0 0 2px color-mix(in srgb,var(--accent) 24%,transparent)}
  .modal-backdrop.show{overscroll-behavior:contain}

  @media(hover:hover) and (pointer:fine){
    .primary-btn:hover:not(:disabled){transform:translateY(-1px)}
    .word-open-btn:hover{text-decoration-thickness:1px}
  }
  @media(hover:none){
    .answer-btn:hover,.primary-btn:hover:not(:disabled){transform:none}
  }

  @media(prefers-reduced-motion:no-preference){
    .view.active{animation:ui4ViewIn var(--motion-fast) ease-out}
    .modal-backdrop.show{animation:ui4FadeIn var(--motion-fast) ease-out}
    .modal-backdrop.show>.modal{animation:ui4ModalIn var(--motion-standard) cubic-bezier(.2,.75,.25,1)}
    .practice-screen:not([hidden]) .practice-screen-shell{animation:ui4SurfaceIn var(--motion-standard) ease-out}
  }
  @keyframes ui4ViewIn{from{opacity:.985;transform:translateY(2px)}to{opacity:1;transform:none}}
  @keyframes ui4FadeIn{from{opacity:0}to{opacity:1}}
  @keyframes ui4ModalIn{from{opacity:.98;transform:translateY(4px)}to{opacity:1;transform:none}}
  @keyframes ui4SurfaceIn{from{opacity:.99;transform:translateY(2px)}to{opacity:1;transform:none}}

  @media(max-width:720px){
    html{scroll-padding-top:76px;scroll-padding-bottom:calc(86px + env(safe-area-inset-bottom))}
    :where(button,a[href],input,select,summary,[tabindex]:not([tabindex="-1"])){scroll-margin-top:76px;scroll-margin-bottom:calc(86px + env(safe-area-inset-bottom))}
  }
  @media(max-width:360px){
    .app{padding-left:10px;padding-right:10px}
    .app-header{margin-left:-10px;margin-right:-10px;padding-left:10px;padding-right:10px}
    .brand h1{font-size:.95rem}
    .app-nav{padding-left:4px;padding-right:4px}
    .app-nav .tab{font-size:.64rem;padding-inline:2px}
    .practice-hero{padding:18px 16px}
    .practice-support-grid .review-queue-panel,.practice-setup-panel{padding:14px}
    .progress-meta{grid-template-columns:repeat(2,minmax(0,1fr))}
    .library-filter-bar{padding:8px}
  }
  @media(max-height:500px) and (min-width:721px) and (max-width:940px){
    .app{padding-bottom:24px}
    .app-header{position:static;grid-template-columns:auto minmax(0,1fr) auto;min-height:54px;margin-bottom:14px;padding-top:0}
    .app-header .app-nav{grid-column:auto;grid-row:auto;justify-self:center;width:auto;min-height:54px}
    .app-nav .tab{min-height:54px}
    .brand p{display:none}
    .view-heading{margin-bottom:12px}
  }

  @media(prefers-reduced-motion:reduce){
    :root{--motion-fast:0ms;--motion-standard:0ms}
    *,*::before,*::after{scroll-behavior:auto!important;animation:none!important;transition:none!important}
    :where(.primary-btn,.ghost-btn,.icon-btn,.danger-btn,.answer-btn,.confidence-btn,.practice-close-btn,.practice-translation-btn):active:not(:disabled){transform:none}
  }
  @media(prefers-contrast:more){
    :root{--border-strong:var(--text-soft)}
    :where(button,input,select,summary):focus-visible{outline-width:3px}
    .answer-btn,.confidence-btn,.library-table-panel,.progress-overview{border-width:2px}
  }
  @media(forced-colors:active){
    :root{--focus-ring:Highlight}
    :where(button,a[href],input,select,summary,[tabindex]:not([tabindex="-1"])):focus-visible{outline:2px solid Highlight!important;outline-offset:3px}
    .primary-btn,.ghost-btn,.icon-btn,.danger-btn,.answer-btn,.confidence-btn,.practice-close-btn,.practice-translation-btn,.panel,.modal{border-color:CanvasText}
    .answer-btn.correct{border:3px double Highlight;box-shadow:none}
    .answer-btn.incorrect{border:3px dashed CanvasText;box-shadow:none}
    .translation-hint.show,.feedback.show{border-color:CanvasText}
  }
'''
if "/* UI4 — motion, interaction states, accessibility, and responsive finish */" in html:
    raise SystemExit("UI4 CSS already present")
if "\n</style>" not in html:
    raise SystemExit("Closing style tag not found")
html = html.replace("\n</style>", ui4_css + "\n</style>", 1)

# Preserve the original practice launcher when practice is reopened from a summary modal.
old_practice_open = '''    open(){
      const screen=this.element();
      if(!screen) return;
      this.returnFocus=(typeof HTMLElement!=="undefined" && document.activeElement instanceof HTMLElement)?document.activeElement:DOM.$("#openPracticeBtn");
      screen.hidden=false;
      screen.setAttribute("aria-hidden","false");'''
new_practice_open = '''    open(){
      const screen=this.element();
      if(!screen) return;
      const wasOpen=!screen.hidden;
      if(!wasOpen){
        this.returnFocus=(typeof HTMLElement!=="undefined" && document.activeElement instanceof HTMLElement)?document.activeElement:DOM.$("#openPracticeBtn");
        screen.hidden=false;
      }
      screen.setAttribute("aria-hidden","false");'''
if old_practice_open not in html:
    raise SystemExit("PracticeScreen.open anchor not found")
html = html.replace(old_practice_open, new_practice_open, 1)

# Accessibility helpers: motion preference, safe scrolling, and modal background inertness.
old_a11y_head = '''  const AccessibilityManager = {
    announce(message){'''
new_a11y_head = '''  const AccessibilityManager = {
    prefersReducedMotion(){ return Boolean(window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches); },
    scrollIntoView(target,{block="nearest",inline="nearest"}={}){
      if(!target?.scrollIntoView) return;
      target.scrollIntoView({behavior:this.prefersReducedMotion()?"auto":"smooth",block,inline});
    },
    setAppInert(enabled){
      const app=DOM.$("#app");
      if(app) app.inert=Boolean(enabled);
    },
    announce(message){'''
if old_a11y_head not in html:
    raise SystemExit("AccessibilityManager anchor not found")
html = html.replace(old_a11y_head, new_a11y_head, 1)

old_open_modal = '''      modal.classList.add("show");
      document.body.classList.add("modal-open");
      requestAnimationFrame(()=>{'''
new_open_modal = '''      modal.classList.add("show");
      document.body.classList.add("modal-open");
      this.setAppInert(true);
      requestAnimationFrame(()=>{'''
if old_open_modal not in html:
    raise SystemExit("openModal inert anchor not found")
html = html.replace(old_open_modal, new_open_modal, 1)

old_close_modal = '''      modal._returnFocus=null;
      if(!this.activeModal()) document.body.classList.remove("modal-open");
      requestAnimationFrame(()=>{'''
new_close_modal = '''      modal._returnFocus=null;
      if(!this.activeModal()){
        document.body.classList.remove("modal-open");
        this.setAppInert(false);
      }
      requestAnimationFrame(()=>{'''
if old_close_modal not in html:
    raise SystemExit("closeModal inert anchor not found")
html = html.replace(old_close_modal, new_close_modal, 1)

old_theme_sync = '''      button.setAttribute("aria-label",label);
      button.title=label;
    },'''
new_theme_sync = '''      button.setAttribute("aria-label",label);
      button.setAttribute("aria-pressed",dark?"true":"false");
      button.title=label;
      const themeMeta=document.querySelector('meta[name="theme-color"]');
      if(themeMeta) themeMeta.setAttribute("content",dark?"#131817":"#1d6f5f");
    },'''
if old_theme_sync not in html:
    raise SystemExit("ThemeManager sync anchor not found")
html = html.replace(old_theme_sync, new_theme_sync, 1)

old_data_scroll = '''        if(panel){ panel.scrollIntoView({behavior:"smooth",block:"start"}); panel.focus({preventScroll:true}); }'''
new_data_scroll = '''        if(panel){ AccessibilityManager.scrollIntoView(panel,{block:"start"}); panel.focus({preventScroll:true}); }'''
if old_data_scroll not in html:
    raise SystemExit("Data-control smooth-scroll anchor not found")
html = html.replace(old_data_scroll, new_data_scroll, 1)

old_view_tail = '''      if(view==="stats") StatisticsView.render();
      if(view==="library") VocabularyView.render();
    },'''
new_view_tail = '''      if(view==="stats") StatisticsView.render();
      if(view==="library") VocabularyView.render();
      const viewLabel=DOM.$(`.tab[data-view="${view}"] .nav-label`)?.textContent?.trim()||view;
      AccessibilityManager.announce(`${viewLabel} view.`);
    },'''
if old_view_tail not in html:
    raise SystemExit("AppUI.setView tail anchor not found")
html = html.replace(old_view_tail, new_view_tail, 1)

INDEX.write_text(html, encoding="utf-8")

# Add permanent UI4 structural invariants.
verify = VERIFY.read_text(encoding="utf-8")
verify_anchor = "requireFragment(html, '/* UI3 — practice, vocabulary, and progress surface polish */', 'UI3 surface style contract');\n"
verify_lines = """requireFragment(html, '/* UI4 — motion, interaction states, accessibility, and responsive finish */', 'UI4 finish style contract');
requireFragment(html, 'aria-pressed=\"false\" title=\"Switch to dark mode\"', 'theme toggle pressed-state semantics');
requireFragment(html, '--focus-ring:var(--accent)', 'visible focus token');
requireFragment(html, '@media(prefers-reduced-motion:reduce)', 'reduced-motion support');
requireFragment(html, '@media(forced-colors:active)', 'forced-colors support');
requireFragment(html, 'scroll-padding-bottom:calc(86px + env(safe-area-inset-bottom))', 'mobile focus-not-obscured spacing');
requireFragment(html, 'const wasOpen=!screen.hidden;', 'practice focus-return preservation');
requireFragment(html, 'this.setAppInert(true);', 'modal background inertness');
requireFragment(html, 'this.prefersReducedMotion()?\"auto\":\"smooth\"', 'motion-aware programmatic scrolling');
requireFragment(html, 'themeMeta.setAttribute(\"content\",dark?\"#131817\":\"#1d6f5f\")', 'theme-color synchronization');
"""
if verify_lines not in verify:
    if verify_anchor not in verify:
        raise SystemExit("verify-source UI3 anchor not found")
    verify = verify.replace(verify_anchor, verify_anchor + verify_lines, 1)

doc_check = """try { await access(join(rootDir, 'docs', 'ui4-interaction-accessibility.md')); }
catch { fail('Missing UI4 interaction/accessibility specification.'); }
"""
insert_before = "const manifest = JSON.parse(await readFile(join(rootDir, 'site.webmanifest'), 'utf8'));\n"
if doc_check not in verify:
    if insert_before not in verify:
        raise SystemExit("verify-source document-check anchor not found")
    verify = verify.replace(insert_before, doc_check + insert_before, 1)
VERIFY.write_text(verify, encoding="utf-8")

package = json.loads(PACKAGE.read_text(encoding="utf-8"))
package["scripts"]["test:a11y-browser"] = "node tests/accessibility-finish.mjs"
PACKAGE.write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

readme = README.read_text(encoding="utf-8").rstrip() + "\n\n## UI4 interaction, accessibility, and responsive finish\n\n- Focus indicators use a stable two-pixel perimeter and fixed-chrome-safe scroll margins.\n- Modals inert the background application and restore focus on close.\n- Reduced-motion preferences disable non-essential animation and smooth scrolling.\n- Forced-colors/high-contrast modes retain visible state and focus cues.\n- Narrow-phone and short-landscape breakpoints are explicitly certified.\n- `tests/accessibility-finish.mjs` exercises keyboard focus, target sizes, modal isolation, theme semantics, reduced motion, forced colors, and responsive reflow.\n- See `docs/ui4-interaction-accessibility.md` for the UI4 contract and pre-RC handoff.\n"
README.write_text(readme, encoding="utf-8")

DOC.write_text('''# UI4 — Motion, Interaction States, Accessibility & Responsive Finish

UI4 is the final interface-finish phase before release certification. It does not alter vocabulary, scoring, SRS scheduling, session semantics, or certified translations.

## Standards target

The implementation is aligned to WCAG 2.2 interaction concerns relevant to this static application, especially keyboard operability, Focus Not Obscured (2.4.11), Target Size (Minimum) (2.5.8), and robust visible focus. Artikelwerk intentionally keeps its own primary controls at 44 CSS px or larger even though WCAG 2.2 AA permits smaller targets in defined cases.

Reference material:

- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C WCAG 2.2 changes: https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
- MDN prefers-reduced-motion: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- MDN forced-colors: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/forced-colors

## Motion contract

- Motion is restrained to short opacity/2–4 px entrance transitions for views and dialogs.
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
''', encoding="utf-8")

TEST.write_text(r'''import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';

const baseURL = process.env.ARTIKELWERK_URL || 'http://127.0.0.1:4173';
const evidenceDir = 'test-artifacts/ui4';
await mkdir(evidenceDir, { recursive: true });

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function collectErrors(page, label) {
  const errors = [];
  page.on('pageerror', error => errors.push(`pageerror: ${error.message}`));
  page.on('console', message => {
    if (message.type() === 'error') errors.push(`console: ${message.text()}`);
  });
  return () => assert(errors.length === 0, `${label}: browser errors: ${errors.join(' | ')}`);
}

async function assertNoDocumentOverflow(page, label) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  assert(overflow <= 1, `${label}: document horizontally overflows by ${overflow}px`);
}

async function assertTarget(page, selector, label, minimum = 44) {
  const box = await page.locator(selector).boundingBox();
  assert(box, `${label}: missing ${selector}`);
  assert(box.width >= minimum && box.height >= minimum, `${label}: ${selector} target is ${Math.round(box.width)}×${Math.round(box.height)}, expected at least ${minimum}×${minimum}`);
}

async function assertFocusRing(page, selector, label) {
  await page.locator(selector).focus();
  const style = await page.locator(selector).evaluate(el => {
    const cs = getComputedStyle(el);
    return { style: cs.outlineStyle, width: parseFloat(cs.outlineWidth), offset: parseFloat(cs.outlineOffset) };
  });
  assert(style.style !== 'none' && style.width >= 2, `${label}: ${selector} lacks a >=2px visible focus outline`);
  assert(style.offset >= 2, `${label}: ${selector} focus outline offset is too small`);
}

const browser = await chromium.launch({ headless: true });
const profiles = [
  { name: 'narrow-phone', width: 320, height: 568, mobile: true, touch: true },
  { name: 'small-phone', width: 360, height: 640, mobile: true, touch: true },
  { name: 'modern-phone', width: 390, height: 844, mobile: true, touch: true },
  { name: 'large-phone', width: 412, height: 915, mobile: true, touch: true },
  { name: 'tablet', width: 768, height: 1024, mobile: true, touch: true },
  { name: 'touch-landscape', width: 844, height: 390, mobile: true, touch: true },
  { name: 'desktop', width: 1440, height: 900, mobile: false, touch: false },
];

for (const profile of profiles) {
  const context = await browser.newContext({
    viewport: { width: profile.width, height: profile.height },
    isMobile: profile.mobile,
    hasTouch: profile.touch,
  });
  const page = await context.newPage();
  const finishErrors = await collectErrors(page, profile.name);
  await page.goto(baseURL, { waitUntil: 'networkidle' });

  await assertNoDocumentOverflow(page, profile.name);
  await assertTarget(page, '#themeBtn', profile.name);
  await assertTarget(page, '#openPracticeBtn', profile.name);
  await assertTarget(page, '#tabPractice', profile.name);
  await assertTarget(page, '#tabStats', profile.name);
  await assertTarget(page, '#tabLibrary', profile.name);
  await assertFocusRing(page, '#openPracticeBtn', profile.name);

  // Theme is a real toggle state and browser chrome metadata stays synchronized.
  const beforeTheme = await page.locator('#themeBtn').getAttribute('aria-pressed');
  assert(beforeTheme === 'false', `${profile.name}: theme toggle should begin aria-pressed=false in the fresh context`);
  await page.locator('#themeBtn').click();
  assert(await page.locator('#themeBtn').getAttribute('aria-pressed') === 'true', `${profile.name}: dark theme did not expose aria-pressed=true`);
  assert(await page.locator('meta[name="theme-color"]').getAttribute('content') === '#131817', `${profile.name}: dark theme-color metadata was not synchronized`);
  await page.locator('#themeBtn').click();

  // Keyboard tab navigation preserves the ARIA tab model.
  await page.locator('#tabPractice').focus();
  await page.keyboard.press('ArrowRight');
  assert(await page.locator('#tabStats').getAttribute('aria-selected') === 'true', `${profile.name}: ArrowRight did not select Progress`);
  assert(await page.evaluate(() => document.activeElement?.id) === 'tabStats', `${profile.name}: keyboard tab focus did not move to Progress`);

  // Word-detail modal isolates the background and restores focus on Escape.
  await page.locator('#tabLibrary').click();
  const wordButton = page.locator('.word-open-btn').first();
  await wordButton.focus();
  await wordButton.click();
  await page.locator('#wordDetailModal.show').waitFor({ state: 'visible' });
  assert(await page.locator('#app').evaluate(el => el.inert === true), `${profile.name}: background app is not inert while word detail is open`);
  assert(await page.evaluate(() => Boolean(document.activeElement?.closest('#wordDetailModal'))), `${profile.name}: focus did not enter word-detail modal`);
  await page.keyboard.press('Escape');
  assert(await page.locator('#app').evaluate(el => el.inert === false), `${profile.name}: background app remained inert after modal close`);
  assert(await page.evaluate(() => document.activeElement?.classList.contains('word-open-btn') === true), `${profile.name}: modal close did not restore the vocabulary opener`);

  // Dedicated practice still owns focus and returns it to the launcher.
  await page.locator('#tabPractice').click();
  await page.locator('#openPracticeBtn').focus();
  await page.locator('#openPracticeBtn').click();
  await page.locator('#practiceScreen:not([hidden])').waitFor({ state: 'visible' });
  await page.waitForTimeout(30);
  assert(await page.evaluate(() => document.activeElement?.id) === 'nounPrompt', `${profile.name}: practice did not focus the exercise prompt`);
  await assertTarget(page, '#closePracticeBtn', `${profile.name} practice`);
  await assertTarget(page, '#showTranslationBtn', `${profile.name} practice`);
  await assertTarget(page, '.answer-btn[data-article="der"]', `${profile.name} practice`);
  await page.keyboard.press('Escape');
  assert(await page.evaluate(() => document.activeElement?.id) === 'openPracticeBtn', `${profile.name}: practice close did not restore the launcher`);

  // Mobile fixed navigation must leave focused deep controls unobscured.
  if (profile.width <= 720) {
    await page.locator('#resetBtn').click();
    const resetAll = page.locator('#resetAllBtn');
    await resetAll.focus();
    await resetAll.evaluate(el => el.scrollIntoView({ block: 'nearest' }));
    await page.waitForTimeout(30);
    const geometry = await page.evaluate(() => {
      const target = document.querySelector('#resetAllBtn').getBoundingClientRect();
      const nav = document.querySelector('.app-nav').getBoundingClientRect();
      return { targetTop: target.top, targetBottom: target.bottom, navTop: nav.top, viewport: innerHeight };
    });
    assert(geometry.targetTop >= -1 && geometry.targetBottom <= geometry.navTop + 1, `${profile.name}: focused destructive control is obscured by fixed mobile navigation`);
  }

  await assertNoDocumentOverflow(page, `${profile.name} after interactions`);
  if (['narrow-phone', 'touch-landscape', 'desktop'].includes(profile.name)) {
    await page.screenshot({ path: `${evidenceDir}/${profile.name}.png`, fullPage: true });
  }
  finishErrors();
  await context.close();
}

// Reduced motion must remove transitions and convert smooth programmatic scrolling to auto.
{
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  const page = await context.newPage();
  await page.addInitScript(() => {
    const original = Element.prototype.scrollIntoView;
    Element.prototype.scrollIntoView = function(options) {
      window.__artikelwerkLastScrollBehavior = options?.behavior ?? null;
      return original.call(this, options);
    };
  });
  const finishErrors = await collectErrors(page, 'reduced-motion');
  await page.goto(baseURL, { waitUntil: 'networkidle' });
  assert(await page.evaluate(() => matchMedia('(prefers-reduced-motion: reduce)').matches), 'reduced-motion: media preference is not active');
  const transitionDuration = await page.locator('#openPracticeBtn').evaluate(el => getComputedStyle(el).transitionDuration);
  assert(transitionDuration === '0s', `reduced-motion: button transition remains ${transitionDuration}`);
  await page.locator('#resetBtn').click();
  await page.waitForTimeout(30);
  assert(await page.evaluate(() => window.__artikelwerkLastScrollBehavior) === 'auto', 'reduced-motion: programmatic navigation still requested smooth scrolling');
  finishErrors();
  await context.close();
}

// Windows-style forced colors must preserve a visible keyboard focus indicator and distinct answer borders.
{
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 }, forcedColors: 'active' });
  const page = await context.newPage();
  const finishErrors = await collectErrors(page, 'forced-colors');
  await page.goto(baseURL, { waitUntil: 'networkidle' });
  assert(await page.evaluate(() => matchMedia('(forced-colors: active)').matches), 'forced-colors: media mode is not active');
  await assertFocusRing(page, '#openPracticeBtn', 'forced-colors');
  await page.locator('#openPracticeBtn').click();
  const borderStyle = await page.locator('.answer-btn').first().evaluate(el => getComputedStyle(el).borderStyle);
  assert(borderStyle !== 'none', 'forced-colors: answer controls lost their structural border');
  finishErrors();
  await context.close();
}

await browser.close();
console.log('UI4 motion, accessibility, and responsive-finish tests passed.');
''', encoding="utf-8")

print("Applied UI4 motion, interaction-state, accessibility, responsive, documentation, and test changes.")
