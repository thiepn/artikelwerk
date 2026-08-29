import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';

const baseURL = process.env.ARTIKELWERK_URL || 'http://127.0.0.1:4173';
const evidenceDir = 'test-artifacts/ui5-1';
await mkdir(evidenceDir, { recursive: true });

const assert = (condition, message) => { if (!condition) throw new Error(message); };
const collectErrors = page => {
  const errors = [];
  page.on('pageerror', error => errors.push(`pageerror: ${error.message}`));
  page.on('console', message => { if (message.type() === 'error') errors.push(`console: ${message.text()}`); });
  return errors;
};

async function forceLongNoun(page) {
  await page.locator('#nounPrompt').evaluate(el => {
    el.innerHTML = '<span class="blank">___</span> Untersuchungsgegenstand';
  });
  await page.evaluate(() => window.dispatchEvent(new Event('resize')));
  await page.waitForTimeout(80);
  return page.locator('#nounPrompt').evaluate(el => {
    const node = [...el.childNodes].find(item => item.nodeType === Node.TEXT_NODE && item.textContent.trim());
    const range = document.createRange();
    if (node) range.selectNodeContents(node);
    const style = getComputedStyle(el);
    return {
      scrollWidth: el.scrollWidth,
      clientWidth: el.clientWidth,
      rectCount: node ? range.getClientRects().length : 0,
      fontSize: parseFloat(style.fontSize),
      whiteSpace: style.whiteSpace,
      overflowWrap: style.overflowWrap,
    };
  });
}

async function desktopCase(browser) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  const errors = collectErrors(page);
  await page.goto(baseURL, { waitUntil: 'networkidle' });

  await page.locator('#openPracticeBtn').click();
  await page.locator('#practiceScreen:not([hidden])').waitFor({ state: 'visible' });
  const noun = await forceLongNoun(page);
  assert(noun.rectCount === 1, `desktop: long German noun wrapped into ${noun.rectCount} fragments`);
  assert(noun.scrollWidth <= noun.clientWidth + 1, `desktop: long noun overflows ${noun.scrollWidth} > ${noun.clientWidth}`);
  assert(noun.whiteSpace === 'nowrap', `desktop: standard noun prompt is not single-line (${noun.whiteSpace})`);
  assert(noun.overflowWrap !== 'anywhere', 'desktop: arbitrary mid-word wrapping is still enabled');
  assert(noun.fontSize >= 38 && noun.fontSize <= 90, `desktop: fitted noun size ${noun.fontSize}px is outside the accepted range`);
  const questionPadding = await page.locator('#questionWrap').evaluate(el => {
    const style = getComputedStyle(el);
    return { top: parseFloat(style.paddingTop), bottom: parseFloat(style.paddingBottom) };
  });
  assert(questionPadding.top <= 18 && questionPadding.bottom <= 16, `desktop: Practice vertical rhythm remains too loose (${questionPadding.top}/${questionPadding.bottom})`);
  await page.screenshot({ path: `${evidenceDir}/desktop-practice-long-noun.png`, fullPage: false });
  await page.keyboard.press('Escape');

  await page.locator('#tabStats').click();
  const diagnostics = page.locator('#progressDiagnostics');
  assert(await diagnostics.getAttribute('open') !== null, 'desktop: learning diagnostics should remain expanded');
  assert(await diagnostics.locator('summary').evaluate(el => getComputedStyle(el).display) === 'none', 'desktop: mobile diagnostics summary should be hidden');
  await page.screenshot({ path: `${evidenceDir}/desktop-progress.png`, fullPage: true });

  await page.locator('#tabLibrary').click();
  assert(await page.locator('#libraryMobileFilterToggle').isHidden(), 'desktop: mobile filter disclosure is visible');
  assert(await page.locator('#articleFilter').isVisible(), 'desktop: primary vocabulary filters should remain directly visible');
  await page.screenshot({ path: `${evidenceDir}/desktop-vocabulary.png`, fullPage: false });

  assert(errors.length === 0, `desktop browser errors: ${errors.join(' | ')}`);
  await context.close();
}

async function mobileCase(browser, width = 390, height = 844) {
  const context = await browser.newContext({ viewport: { width, height }, isMobile: true, hasTouch: true, deviceScaleFactor: 1 });
  const page = await context.newPage();
  const errors = collectErrors(page);
  await page.goto(baseURL, { waitUntil: 'networkidle' });

  const navReserve = await page.evaluate(() => {
    const nav = document.querySelector('.app-nav').getBoundingClientRect();
    const main = getComputedStyle(document.querySelector('main'));
    return { navHeight: nav.height, mainPaddingBottom: parseFloat(main.paddingBottom) };
  });
  assert(navReserve.mainPaddingBottom >= navReserve.navHeight + 24, `mobile: bottom-nav exclusion zone ${navReserve.mainPaddingBottom}px is too small for ${navReserve.navHeight}px nav`);

  await page.locator('#openPracticeBtn').click();
  await page.locator('#practiceScreen:not([hidden])').waitFor({ state: 'visible' });
  const noun = await forceLongNoun(page);
  assert(noun.rectCount === 1, `mobile: long German noun wrapped into ${noun.rectCount} fragments`);
  assert(noun.scrollWidth <= noun.clientWidth + 1, `mobile: long noun overflows ${noun.scrollWidth} > ${noun.clientWidth}`);
  assert(noun.fontSize >= 25, `mobile: fitted noun became too small at ${noun.fontSize}px`);
  await page.screenshot({ path: `${evidenceDir}/mobile-practice-long-noun.png`, fullPage: false });
  await page.keyboard.press('Escape');

  await page.locator('#tabLibrary').click();
  const toggle = page.locator('#libraryMobileFilterToggle');
  assert(await toggle.isVisible(), 'mobile: Filters disclosure is missing');
  assert(await page.locator('#articleFilter').isHidden(), 'mobile: primary filters should be collapsed initially');
  assert(await toggle.getAttribute('aria-expanded') === 'false', 'mobile: Filters disclosure should begin collapsed');
  await page.screenshot({ path: `${evidenceDir}/mobile-vocabulary-collapsed.png`, fullPage: false });
  await toggle.click();
  assert(await page.locator('#articleFilter').isVisible(), 'mobile: Filters disclosure did not reveal article filter');
  await page.locator('#articleFilter').selectOption('die');
  await page.locator('#articleFilter').dispatchEvent('input');
  await page.waitForTimeout(20);
  assert((await page.locator('#libraryPrimaryFilterCount').textContent())?.trim() === '(1)', 'mobile: active filter count did not update');
  await page.screenshot({ path: `${evidenceDir}/mobile-vocabulary-filters.png`, fullPage: false });

  await page.locator('#tabStats').click();
  const diagnostics = page.locator('#progressDiagnostics');
  assert(await diagnostics.getAttribute('open') === null, 'mobile: lower diagnostics should begin collapsed');
  assert(await diagnostics.locator('summary').isVisible(), 'mobile: learning diagnostics disclosure is missing');
  const helperSize = await page.locator('#statsView .section > p.muted').first().evaluate(el => parseFloat(getComputedStyle(el).fontSize));
  assert(helperSize >= 13, `mobile: Progress helper text remains too small at ${helperSize}px`);
  await page.screenshot({ path: `${evidenceDir}/mobile-progress.png`, fullPage: false });

  await page.locator('#resetBtn').click();
  const resetAll = page.locator('#resetAllBtn');
  await resetAll.scrollIntoViewIfNeeded();
  await page.waitForTimeout(40);
  const clearance = await page.evaluate(() => {
    const target = document.querySelector('#resetAllBtn').getBoundingClientRect();
    const nav = document.querySelector('.app-nav').getBoundingClientRect();
    return { targetBottom: target.bottom, navTop: nav.top };
  });
  assert(clearance.targetBottom <= clearance.navTop + 1, `mobile: deep Progress control remains obscured by nav (${clearance.targetBottom} > ${clearance.navTop})`);

  assert(errors.length === 0, `mobile browser errors: ${errors.join(' | ')}`);
  await context.close();
}

const browser = await chromium.launch({ headless: true });
try {
  await desktopCase(browser);
  await mobileCase(browser);
  console.log('UI5.1 visual-acceptance fixes passed.');
} finally {
  await browser.close();
}
