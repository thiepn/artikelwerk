import assert from "node:assert/strict";
import fs from "node:fs/promises";
import { chromium } from "playwright";

const BASE_URL = process.env.ARTIKELWERK_URL || "http://127.0.0.1:4173";
const artifactDir = "test-artifacts";
await fs.mkdir(artifactDir, { recursive: true });

function collectErrors(page) {
  const errors = [];
  page.on("pageerror", error => errors.push(`pageerror: ${error.message}`));
  page.on("console", message => { if (message.type() === "error") errors.push(`console: ${message.text()}`); });
  return errors;
}

async function assertNoDocumentOverflow(page, label) {
  const dims = await page.evaluate(() => ({ width: document.documentElement.clientWidth, scrollWidth: document.documentElement.scrollWidth }));
  assert.ok(dims.scrollWidth <= dims.width + 1, `${label} has document-level horizontal overflow: ${dims.scrollWidth} > ${dims.width}`);
}

async function assertInsideViewport(page, selector, label) {
  const box = await page.locator(selector).boundingBox();
  assert.ok(box, `${label} missing bounding box`);
  const viewport = page.viewportSize();
  assert.ok(viewport, "viewport unavailable");
  assert.ok(box.x >= -1 && box.y >= -1, `${label} starts outside viewport`);
  assert.ok(box.x + box.width <= viewport.width + 1, `${label} exceeds viewport width`);
  assert.ok(box.y + box.height <= viewport.height + 1, `${label} exceeds viewport height`);
}

async function desktopCase(browser) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  const errors = collectErrors(page);
  await page.goto(BASE_URL, { waitUntil: "networkidle" });

  await page.locator("#openPracticeBtn").click();
  await page.locator("#practiceScreen").waitFor({ state: "visible" });
  assert.equal(await page.locator("#practiceScreen").evaluate(el => el.classList.contains("ui3-practice")), true, "practice surface must carry UI3 marker");
  assert.equal(await page.locator(".answer-btn .answer-key").count(), 3, "all article controls need keyboard-number cells");
  assert.equal(await page.locator(".answer-btn .answer-article").count(), 3, "all article controls need article labels");
  await page.locator(".answer-btn").first().click();
  await page.locator("#feedback.show").waitFor({ state: "visible" });
  await assertInsideViewport(page, "#feedback", "practice feedback");
  await assertInsideViewport(page, "#nextBtn", "practice next action");
  await page.locator("#closePracticeBtn").click();

  await page.locator("#tabStats").click();
  await page.locator(".progress-overview").waitFor({ state: "visible" });
  assert.equal(await page.locator(".progress-overview .stat-card").count(), 10, "all ten legacy metric surfaces must remain represented");
  assert.equal(await page.locator(".progress-primary #statAccuracy").count(), 1, "accuracy must be the primary progress metric");
  assert.equal(await page.locator(".progress-meta #statMedianTime").count(), 1, "median response must remain available as a secondary metric");
  await assertNoDocumentOverflow(page, "desktop progress surface");

  await page.locator("#tabLibrary").click();
  await page.locator(".library-filter-bar").waitFor({ state: "visible" });
  assert.equal(await page.locator("#advancedLibraryFilters summary").textContent(), "Advanced filters", "advanced-filter disclosure copy");
  await page.locator(".library-details-btn").first().click();
  await page.locator("#wordDetailModal.show").waitFor({ state: "visible" });
  const layers = await page.evaluate(() => ({
    modal: Number.parseInt(getComputedStyle(document.querySelector("#wordDetailModal")).zIndex || "0", 10),
    header: Number.parseInt(getComputedStyle(document.querySelector(".app-header")).zIndex || "0", 10),
  }));
  assert.ok(layers.modal > layers.header, `word detail modal must sit above app chrome: ${layers.modal} <= ${layers.header}`);
  await page.locator("#wordDetailCloseBtn").click();
  await assertNoDocumentOverflow(page, "desktop vocabulary surface");

  await page.screenshot({ path: `${artifactDir}/ui3-desktop-1440x900.png`, fullPage: false });
  assert.deepEqual(errors, [], "desktop UI3 browser errors");
  await context.close();
}

async function mobileCase(browser, width, height) {
  const context = await browser.newContext({ viewport: { width, height }, isMobile: true, hasTouch: true, deviceScaleFactor: 1 });
  const page = await context.newPage();
  const errors = collectErrors(page);
  await page.goto(BASE_URL, { waitUntil: "networkidle" });
  await assertNoDocumentOverflow(page, `mobile home ${width}x${height}`);

  await page.locator("#openPracticeBtn").click();
  await page.locator("#practiceScreen").waitFor({ state: "visible" });
  await assertInsideViewport(page, ".answer-btn:first-child", "first polished answer");
  await assertInsideViewport(page, ".answer-btn:last-child", "last polished answer");
  await page.locator("#unknownWordBtn").click();
  await page.locator("#feedback.show").waitFor({ state: "visible" });
  await assertInsideViewport(page, "#nextBtn", "mobile feedback next action");
  await page.locator("#closePracticeBtn").click();

  await page.locator("#tabStats").click();
  await page.locator(".progress-overview").waitFor({ state: "visible" });
  await assertNoDocumentOverflow(page, `mobile progress ${width}x${height}`);
  const progressWidth = await page.locator(".progress-overview").evaluate(el => el.getBoundingClientRect().width);
  assert.ok(progressWidth <= width, "progress overview must fit mobile viewport");

  await page.locator("#tabLibrary").click();
  await page.locator("#librarySearch").waitFor({ state: "visible" });
  await assertInsideViewport(page, "#librarySearch", "mobile vocabulary search");
  await assertNoDocumentOverflow(page, `mobile vocabulary ${width}x${height}`);
  await page.locator(".library-details-btn").first().click();
  await page.locator("#wordDetailModal.show").waitFor({ state: "visible" });
  await assertInsideViewport(page, "#wordDetailCloseBtn", "mobile word-detail close");
  await page.locator("#wordDetailCloseBtn").click();

  await page.screenshot({ path: `${artifactDir}/ui3-mobile-${width}x${height}.png`, fullPage: false });
  assert.deepEqual(errors, [], `mobile UI3 browser errors at ${width}x${height}`);
  await context.close();
}

const browser = await chromium.launch({ headless: true });
try {
  await desktopCase(browser);
  await mobileCase(browser, 360, 740);
  await mobileCase(browser, 390, 844);
  await mobileCase(browser, 412, 915);
  console.log("UI3 practice, vocabulary, and progress surface tests passed.");
} finally {
  await browser.close();
}
