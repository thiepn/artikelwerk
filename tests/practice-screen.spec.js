const { test, expect } = require('@playwright/test');

const baseURL = process.env.ARTIKELWERK_TEST_URL || 'http://127.0.0.1:4173';
const viewports = [
  { name: 'mobile portrait', width: 390, height: 844 },
  { name: 'small mobile', width: 360, height: 640 },
  { name: 'mobile landscape', width: 844, height: 390 },
  { name: 'desktop', width: 1440, height: 900 },
];

for (const viewport of viewports) {
  test(`dedicated practice remains fixed and usable — ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });

    const pageErrors = [];
    page.on('pageerror', (error) => pageErrors.push(error.message));

    await page.route('https://api.mymemory.translated.net/**', async (route) => {
      const requestURL = new URL(route.request().url());
      const source = requestURL.searchParams.get('q') || '';
      const dictionary = {
        Haus: 'house',
        Tisch: 'table',
        Frau: 'woman',
        Kind: 'child',
      };
      const translatedText = dictionary[source] || `English: ${source}`;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ responseData: { translatedText } }),
      });
    });

    await page.goto(baseURL, { waitUntil: 'domcontentloaded' });
    const launcher = page.locator('#aw-practice-launch');
    await expect(launcher).toBeVisible({ timeout: 20_000 });

    await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
    const initialScroll = await page.evaluate(() => window.scrollY);

    await launcher.click();
    const shell = page.locator('#aw-practice-shell');
    await expect(shell).toBeVisible({ timeout: 10_000 });

    const choices = shell.locator('[data-aw-article-choice]');
    await expect(choices).toHaveCount(3, { timeout: 10_000 });

    const layout = await shell.evaluate((element) => {
      const shellRect = element.getBoundingClientRect();
      const stage = element.querySelector('.aw-practice-stage');
      const support = element.querySelector('.aw-practice-support');
      const supportRect = support.getBoundingClientRect();
      const bodyStyle = getComputedStyle(document.body);
      const htmlStyle = getComputedStyle(document.documentElement);
      return {
        shellRect: {
          left: shellRect.left,
          top: shellRect.top,
          right: shellRect.right,
          bottom: shellRect.bottom,
          width: shellRect.width,
          height: shellRect.height,
        },
        supportRect: {
          left: supportRect.left,
          top: supportRect.top,
          right: supportRect.right,
          bottom: supportRect.bottom,
        },
        bodyPosition: bodyStyle.position,
        bodyOverflow: bodyStyle.overflow,
        htmlOverflow: htmlStyle.overflow,
        shellOverflow: getComputedStyle(element).overflow,
        stageOverflow: getComputedStyle(stage).overflow,
        shellScrollHeight: element.scrollHeight,
        shellClientHeight: element.clientHeight,
        stageScrollHeight: stage.scrollHeight,
        stageClientHeight: stage.clientHeight,
      };
    });

    expect(layout.shellRect.left).toBeGreaterThanOrEqual(-1);
    expect(layout.shellRect.top).toBeGreaterThanOrEqual(-1);
    expect(layout.shellRect.right).toBeLessThanOrEqual(viewport.width + 1);
    expect(layout.shellRect.bottom).toBeLessThanOrEqual(viewport.height + 1);
    expect(layout.shellRect.width).toBeGreaterThanOrEqual(viewport.width - 2);
    expect(layout.shellRect.height).toBeGreaterThanOrEqual(viewport.height - 2);
    expect(layout.supportRect.left).toBeGreaterThanOrEqual(-1);
    expect(layout.supportRect.top).toBeGreaterThanOrEqual(-1);
    expect(layout.supportRect.right).toBeLessThanOrEqual(viewport.width + 1);
    expect(layout.supportRect.bottom).toBeLessThanOrEqual(viewport.height + 1);
    expect(layout.bodyPosition).toBe('fixed');
    expect(layout.bodyOverflow).toBe('hidden');
    expect(layout.htmlOverflow).toBe('hidden');
    expect(layout.shellOverflow).toBe('hidden');
    expect(layout.stageOverflow).toBe('hidden');
    expect(layout.shellScrollHeight).toBeLessThanOrEqual(layout.shellClientHeight + 2);
    expect(layout.stageScrollHeight).toBeLessThanOrEqual(layout.stageClientHeight + 2);

    for (let index = 0; index < 3; index += 1) {
      const box = await choices.nth(index).boundingBox();
      expect(box).not.toBeNull();
      expect(box.width).toBeGreaterThanOrEqual(44);
      expect(box.height).toBeGreaterThanOrEqual(44);
    }

    await choices.first().click();
    await page.waitForTimeout(150);
    expect(await page.evaluate(() => window.scrollY)).toBe(initialScroll);
    await expect(shell.locator('.aw-practice-translation')).not.toHaveText('');
    await expect(shell.locator('.aw-practice-explanation')).not.toHaveText('');

    await shell.locator('.aw-practice-close').click();
    await expect(shell).toBeHidden();
    expect(Math.abs((await page.evaluate(() => window.scrollY)) - initialScroll)).toBeLessThanOrEqual(2);
    expect(pageErrors).toEqual([]);
  });
}
