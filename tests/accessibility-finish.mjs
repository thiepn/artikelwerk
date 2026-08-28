import { chromium } from 'playwright';
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
  assert(await page.locator('.app-header').evaluate(el => el.inert === true), `${profile.name}: app chrome is not inert behind fullscreen practice`);
  assert(await page.locator('.practice-hero').evaluate(el => el.inert === true), `${profile.name}: practice setup remains interactive behind fullscreen practice`);
  assert(await page.evaluate(() => document.activeElement?.id) === 'nounPrompt', `${profile.name}: practice did not focus the exercise prompt`);
  await assertTarget(page, '#closePracticeBtn', `${profile.name} practice`);
  await assertTarget(page, '#showTranslationBtn', `${profile.name} practice`);
  await assertTarget(page, '.answer-btn[data-article="der"]', `${profile.name} practice`);
  await page.keyboard.press('Escape');
  assert(await page.locator('.app-header').evaluate(el => el.inert === false), `${profile.name}: app chrome remained inert after practice close`);
  assert(await page.locator('.practice-hero').evaluate(el => el.inert === false), `${profile.name}: practice setup remained inert after practice close`);
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
  await page.locator('.answer-btn').first().click();
  const correct = page.locator('.answer-btn.correct').first();
  await correct.waitFor({ state: 'visible' });
  const correctBorder = await correct.evaluate(el => getComputedStyle(el).borderStyle);
  assert(correctBorder === 'double', `forced-colors: correct state is not structurally distinct (border-style ${correctBorder})`);
  finishErrors();
  await context.close();
}

await browser.close();
console.log('UI4 motion, accessibility, and responsive-finish tests passed.');
