import assert from "node:assert/strict";
import fs from "node:fs/promises";
import { chromium } from "playwright";

const BASE_URL = process.env.ARTIKELWERK_URL || "http://127.0.0.1:4173";
const screenshotDir = "test-artifacts";
await fs.mkdir(screenshotDir, { recursive: true });

function within(value, minimum, maximum, message) {
  assert.ok(value >= minimum && value <= maximum, `${message}: ${value} not in [${minimum}, ${maximum}]`);
}

async function assertVisibleInsideViewport(page, selector, label) {
  const box = await page.locator(selector).boundingBox();
  assert.ok(box, `${label} has no bounding box`);
  const viewport = page.viewportSize();
  assert.ok(viewport, "viewport unavailable");
  assert.ok(box.x >= -1, `${label} extends left of viewport`);
  assert.ok(box.y >= -1, `${label} extends above viewport`);
  assert.ok(box.x + box.width <= viewport.width + 1, `${label} extends right of viewport`);
  assert.ok(box.y + box.height <= viewport.height + 1, `${label} extends below viewport`);
}

async function runMobileCase(browser, width, height) {
  const context = await browser.newContext({
    viewport: { width, height },
    isMobile: true,
    hasTouch: true,
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (error) => errors.push(`pageerror: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(`console: ${message.text()}`);
  });

  await page.goto(BASE_URL, { waitUntil: "networkidle" });
  await page.locator("#openPracticeBtn").waitFor({ state: "visible" });
  assert.equal(await page.locator("#practiceScreen").isHidden(), true, "practice screen must not cover setup on initial load");

  const initialScroll = await page.evaluate(() => window.scrollY);
  await page.locator("#openPracticeBtn").click();
  await page.locator("#practiceScreen").waitFor({ state: "visible" });

  const opened = await page.evaluate(() => {
    const screen = document.querySelector("#practiceScreen");
    const rect = screen.getBoundingClientRect();
    return {
      scrollY: window.scrollY,
      bodyOverflow: getComputedStyle(document.body).overflow,
      screenTop: rect.top,
      screenLeft: rect.left,
      screenWidth: rect.width,
      screenHeight: rect.height,
      clientHeight: screen.clientHeight,
      scrollHeight: screen.scrollHeight,
    };
  });
  assert.equal(opened.scrollY, initialScroll, "opening practice must not move page scroll position");
  assert.equal(opened.bodyOverflow, "hidden", "background page must be scroll-locked");
  within(opened.screenTop, -0.5, 0.5, "practice screen top");
  within(opened.screenLeft, -0.5, 0.5, "practice screen left");
  within(opened.screenWidth, width - 1, width + 1, "practice screen width");
  within(opened.screenHeight, height - 1, height + 1, "practice screen height");
  assert.equal(opened.scrollHeight, opened.clientHeight, "practice screen itself must not scroll");

  await assertVisibleInsideViewport(page, "#closePracticeBtn", "close button");
  await assertVisibleInsideViewport(page, "#showTranslationBtn", "English meaning button");
  await assertVisibleInsideViewport(page, ".answer-btn:first-child", "first article button");

  await page.locator("#showTranslationBtn").click();
  await page.locator("#translationHint.show").waitFor({ state: "visible" });
  const translation = (await page.locator("#translationText").textContent())?.trim();
  assert.ok(translation && translation.length >= 2, "English translation must be populated inside the practice screen");
  await assertVisibleInsideViewport(page, "#translationHint", "English translation");

  const beforeUnknown = await page.evaluate(() => ({ y: window.scrollY, offset: window.visualViewport?.offsetTop || 0 }));
  await page.locator("#unknownWordBtn").click();
  await page.locator("#feedback.show").waitFor({ state: "visible" });
  const afterUnknown = await page.evaluate(() => ({ y: window.scrollY, offset: window.visualViewport?.offsetTop || 0 }));
  assert.deepEqual(afterUnknown, beforeUnknown, "revealing vocabulary feedback must not move the viewport");
  await assertVisibleInsideViewport(page, "#feedbackTitle", "feedback title");
  await assertVisibleInsideViewport(page, "#nextBtn", "next button");

  await page.locator("#nextBtn").click();
  await page.locator("#feedback:not(.show)").waitFor({ state: "attached" });
  assert.equal(await page.locator("#translationHint").getAttribute("aria-hidden"), "true", "next question must reset the translation reveal");

  for (let cycle = 0; cycle < 4; cycle += 1) {
    const before = await page.evaluate(() => ({ y: window.scrollY, offset: window.visualViewport?.offsetTop || 0 }));
    await page.locator(".answer-btn").first().click();
    await page.locator("#feedback.show").waitFor({ state: "visible" });
    const after = await page.evaluate(() => ({ y: window.scrollY, offset: window.visualViewport?.offsetTop || 0 }));
    assert.deepEqual(after, before, `answer ${cycle + 1} must not move the viewport`);
    await assertVisibleInsideViewport(page, "#translationHint", `translation after answer ${cycle + 1}`);
    await assertVisibleInsideViewport(page, "#nextBtn", `next button after answer ${cycle + 1}`);

    if (await page.locator("#nextBtn").isDisabled()) {
      await page.locator(".answer-btn.correct").click();
      assert.equal(await page.locator("#nextBtn").isEnabled(), true, "corrective answer must enable Next");
    }
    await page.locator("#nextBtn").click();
  }

  await page.locator("#closePracticeBtn").click();
  await page.locator("#practiceScreen").waitFor({ state: "hidden" });
  assert.equal(await page.evaluate(() => document.body.classList.contains("practice-open")), false, "closing must unlock the page");

  await page.locator("#formatSelect").selectOption("production");
  await page.locator("#openPracticeBtn").click();
  await page.locator("#productionInput").waitFor({ state: "visible" });
  assert.equal(await page.evaluate(() => document.activeElement?.id), "nounPrompt", "mobile production mode must not summon the keyboard automatically");
  await assertVisibleInsideViewport(page, "#productionInput", "production input");

  await page.screenshot({ path: `${screenshotDir}/practice-${width}x${height}.png`, fullPage: false });
  assert.deepEqual(errors, [], `browser errors at ${width}x${height}`);
  await context.close();
}

async function runDesktopCase(browser) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
  await page.goto(BASE_URL, { waitUntil: "networkidle" });
  await page.locator("#newSessionBtn").click();
  await page.locator("#practiceScreen").waitFor({ state: "visible" });
  await assertVisibleInsideViewport(page, "#quizCard", "desktop quiz card");
  await page.keyboard.press("T");
  await page.locator("#translationHint.show").waitFor({ state: "visible" });
  await page.keyboard.press("Escape");
  await page.locator("#practiceScreen").waitFor({ state: "hidden" });
  assert.deepEqual(errors, [], "desktop browser errors");
  await context.close();
}

const browser = await chromium.launch({ headless: true });
try {
  await runMobileCase(browser, 360, 740);
  await runMobileCase(browser, 390, 844);
  await runMobileCase(browser, 412, 915);
  await runDesktopCase(browser);
  console.log("Dedicated practice-screen tests passed.");
} finally {
  await browser.close();
}
