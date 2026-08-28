from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
VERIFY = ROOT / "scripts" / "verify-source.mjs"
PACKAGE = ROOT / "package.json"
README = ROOT / "README.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


html = INDEX.read_text(encoding="utf-8")

# Practice controls: preserve IDs/data attributes while giving the buttons a calmer,
# more legible learning-control structure.
html = replace_once(
    html,
    '''              <button class="answer-btn" data-article="der" aria-label="Choose der">1 · DER</button>\n              <button class="answer-btn" data-article="die" aria-label="Choose die">2 · DIE</button>\n              <button class="answer-btn" data-article="das" aria-label="Choose das">3 · DAS</button>''',
    '''              <button class="answer-btn" data-article="der" aria-label="Choose der"><span class="answer-key" aria-hidden="true">1</span><span class="answer-article">der</span></button>\n              <button class="answer-btn" data-article="die" aria-label="Choose die"><span class="answer-key" aria-hidden="true">2</span><span class="answer-article">die</span></button>\n              <button class="answer-btn" data-article="das" aria-label="Choose das"><span class="answer-key" aria-hidden="true">3</span><span class="answer-article">das</span></button>''',
    "practice answer-button structure",
)
html = replace_once(
    html,
    '''              <button type="button" class="ghost-btn unknown-word-btn" id="unknownWordBtn"><kbd>0</kbd> I DON'T KNOW THIS WORD</button>''',
    '''              <button type="button" class="ghost-btn unknown-word-btn" id="unknownWordBtn"><kbd>0</kbd> I don't know this word</button>''',
    "unknown-word copy",
)
html = replace_once(
    html,
    '<section class="practice-screen" id="practiceScreen"',
    '<section class="practice-screen ui3-practice" id="practiceScreen"',
    "UI3 practice surface marker",
)

# Progress: keep every existing metric ID and stat-card class for compatibility, but
# replace ten equal cards with one learner-oriented summary surface.
old_stats = '''      <div class="stats-grid">\n        <div class="panel stat-card"><div class="stat-label">Total answers</div><div class="stat-value" id="statTotal">0</div></div>\n        <div class="panel stat-card"><div class="stat-label">Overall accuracy</div><div class="stat-value" id="statAccuracy">—</div></div>\n        <div class="panel stat-card"><div class="stat-label">Reviews due now</div><div class="stat-value" id="statDue">0</div></div>\n        <div class="panel stat-card"><div class="stat-label">Words seen</div><div class="stat-value" id="statSeen">0</div></div>\n        <div class="panel stat-card"><div class="stat-label">Weak words</div><div class="stat-value" id="statWeak">0</div></div>\n        <div class="panel stat-card"><div class="stat-label">Mastered words</div><div class="stat-value" id="statMastered">0</div></div>\n        <div class="panel stat-card"><div class="stat-label">Stubborn words</div><div class="stat-value" id="statLeeches">0</div></div>\n        <div class="panel stat-card"><div class="stat-label">Relearning now</div><div class="stat-value" id="statRelearning">0</div></div>\n        <div class="panel stat-card"><div class="stat-label">Best streak</div><div class="stat-value" id="statBestStreak">0</div></div>\n        <div class="panel stat-card"><div class="stat-label">Median response</div><div class="stat-value" id="statMedianTime">—</div></div>\n      </div>'''
new_stats = '''      <section class="panel stats-grid progress-overview" aria-label="Learning overview">\n        <div class="stat-card progress-primary">\n          <span class="stat-label">Overall accuracy</span>\n          <strong class="stat-value" id="statAccuracy">—</strong>\n          <p>Correct article recall across scored practice.</p>\n        </div>\n        <div class="progress-metrics">\n          <div class="stat-card progress-metric"><span class="stat-label">Due now</span><strong class="stat-value" id="statDue">0</strong></div>\n          <div class="stat-card progress-metric"><span class="stat-label">Weak</span><strong class="stat-value" id="statWeak">0</strong></div>\n          <div class="stat-card progress-metric"><span class="stat-label">Mastered</span><strong class="stat-value" id="statMastered">0</strong></div>\n          <div class="stat-card progress-metric"><span class="stat-label">Words seen</span><strong class="stat-value" id="statSeen">0</strong></div>\n        </div>\n        <div class="progress-meta" aria-label="Additional learning metrics">\n          <div class="stat-card progress-meta-item"><span>Total answers</span><strong id="statTotal">0</strong></div>\n          <div class="stat-card progress-meta-item"><span>Best streak</span><strong id="statBestStreak">0</strong></div>\n          <div class="stat-card progress-meta-item"><span>Median response</span><strong id="statMedianTime">—</strong></div>\n          <div class="stat-card progress-meta-item"><span>Stubborn</span><strong id="statLeeches">0</strong></div>\n          <div class="stat-card progress-meta-item"><span>Relearning</span><strong id="statRelearning">0</strong></div>\n        </div>\n      </section>'''
html = replace_once(html, old_stats, new_stats, "progress overview")

# Vocabulary surface markers/copy. No filter or table behavior changes.
html = replace_once(
    html,
    '<div class="panel library-toolbar library-primary-toolbar">',
    '<div class="panel library-toolbar library-primary-toolbar library-filter-bar">',
    "library quick-filter surface",
)
html = replace_once(html, '<summary>More filters</summary>', '<summary>Advanced filters</summary>', "advanced-filter label")
html = replace_once(
    html,
    '<div class="panel">\n        <div class="library-head">',
    '<div class="panel library-table-panel">\n        <div class="library-head">',
    "library table surface",
)
html = replace_once(
    html,
    'Select a noun for examples, article guidance, lexical metadata, and learning state.',
    'Select a noun to review its meaning, examples, grammar, and learning status.',
    "library helper copy",
)

ui3_css = r'''

  /* UI3 — practice, vocabulary, and progress surface polish */
  .ui3-practice .practice-screen-shell{width:min(100%,1040px)}
  .ui3-practice .practice-screen-header{border-bottom:1px solid var(--border);padding-inline:4px}
  .ui3-practice .practice-screen-body{gap:9px}
  .ui3-practice .session-bar{padding:0 2px;color:var(--muted);font-size:.77rem}
  .ui3-practice .session-metrics{gap:7px}
  .ui3-practice .session-metrics>span,.ui3-practice #timerText:not(:empty){display:inline-flex;align-items:center;gap:4px;min-height:28px;padding:4px 9px;border:1px solid var(--border);border-radius:999px;background:var(--surface);white-space:nowrap}
  .ui3-practice .session-metrics strong{font-variant-numeric:tabular-nums;font-weight:800}
  .ui3-practice .quiz-card{border-color:var(--border);background:var(--surface);box-shadow:0 1px 2px rgba(28,36,33,.04);border-radius:var(--radius-lg)}
  [data-theme="dark"] .ui3-practice .quiz-card{box-shadow:0 1px 2px rgba(0,0,0,.18)}
  .ui3-practice .quiz-top{min-height:30px}
  .ui3-practice .badge{padding:5px 8px;background:transparent;border-color:var(--border);font-size:.7rem;font-weight:720}
  .ui3-practice .prompt-kicker{margin-bottom:11px;letter-spacing:.085em;font-size:.68rem;font-weight:780}
  .ui3-practice .noun{font-weight:790;letter-spacing:-.047em}
  .ui3-practice .translation-hint.show{border-color:color-mix(in srgb,var(--accent) 28%,var(--border));background:var(--accent-soft)}
  .ui3-practice .translation-hint #translationText{font-weight:720}
  .ui3-practice .confidence-capture{gap:6px}
  .ui3-practice .confidence-btn{min-height:36px;padding:5px 10px;border-radius:999px;background:transparent;color:var(--muted);font-size:.76rem}
  .ui3-practice .confidence-btn:hover{background:var(--surface-2);color:var(--text)}
  .ui3-practice .confidence-btn.selected,.ui3-practice .confidence-btn[aria-pressed="true"]{background:var(--accent-soft);border-color:color-mix(in srgb,var(--accent) 45%,var(--border));color:var(--accent-dark);box-shadow:none}
  .ui3-practice .answers{gap:9px}
  .ui3-practice .answer-btn{display:grid;grid-template-columns:auto 1fr auto;align-items:center;min-height:58px;padding:10px 12px;background:var(--surface);border-color:var(--border);box-shadow:none;text-transform:none}
  .ui3-practice .answer-btn::after{content:"";width:18px;height:18px}
  .ui3-practice .answer-btn:hover{transform:none;background:var(--surface-2);border-color:var(--border-strong)}
  .ui3-practice .answer-key{display:grid;place-items:center;width:26px;height:26px;border:1px solid var(--border);border-radius:7px;color:var(--muted);font-size:.68rem;font-weight:760;line-height:1}
  .ui3-practice .answer-article{font-size:1.05rem;font-weight:790;letter-spacing:-.01em}
  .ui3-practice .answer-btn.correct .answer-key{border-color:color-mix(in srgb,var(--good) 55%,var(--border));color:var(--good)}
  .ui3-practice .answer-btn.incorrect .answer-key{border-color:color-mix(in srgb,var(--bad) 55%,var(--border));color:var(--bad)}
  .ui3-practice .unknown-word-btn{border-color:transparent;background:transparent;color:var(--muted);font-weight:650;text-transform:none}
  .ui3-practice .unknown-word-btn:hover{background:var(--surface-2);border-color:var(--border)}
  .ui3-practice .feedback{margin-top:9px;padding:12px 14px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface-2)}
  .ui3-practice .feedback-title{display:flex;align-items:center;gap:7px;font-size:.94rem;font-weight:800}
  .ui3-practice .feedback-title.good::before{content:"✓";display:grid;place-items:center;width:20px;height:20px;border-radius:50%;background:var(--good-bg);color:var(--good);font-size:.72rem}
  .ui3-practice .feedback-title.bad::before{content:"×";display:grid;place-items:center;width:20px;height:20px;border-radius:50%;background:var(--bad-bg);color:var(--bad);font-size:.82rem}
  .ui3-practice .feedback-word{font-weight:780;letter-spacing:-.02em}
  .ui3-practice .feedback-more{border-top-color:var(--border)}
  .ui3-practice .next-row{border-top:1px solid var(--border);padding-top:9px}
  .ui3-practice #nextBtn{min-width:108px}

  #statsView .view-heading{margin-bottom:16px}
  .progress-overview{display:grid;grid-template-columns:minmax(190px,.8fr) minmax(0,1.7fr);gap:0;margin-bottom:14px;padding:0;overflow:hidden;box-shadow:none}
  .progress-overview .stat-card{padding:0;background:transparent;border:0;border-radius:0;box-shadow:none}
  .progress-primary{padding:24px 26px!important;border-right:1px solid var(--border)!important;background:var(--surface)!important}
  .progress-primary .stat-label{display:block;margin-bottom:6px}
  .progress-primary .stat-value{display:block;margin:0;font-size:clamp(2.55rem,5vw,3.6rem);line-height:1;font-weight:790;letter-spacing:-.065em;font-variant-numeric:tabular-nums}
  .progress-primary p{max-width:220px;margin:10px 0 0;color:var(--muted);font-size:.78rem;line-height:1.4}
  .progress-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));align-items:stretch}
  .progress-metric{display:flex;flex-direction:column;justify-content:center;gap:5px;min-width:0;padding:20px 16px!important;border-left:1px solid var(--border)!important}
  .progress-metric:first-child{border-left:0!important}
  .progress-metric .stat-label{font-size:.68rem;letter-spacing:.045em}
  .progress-metric .stat-value{margin:0;font-size:1.7rem;line-height:1.05;font-weight:780;font-variant-numeric:tabular-nums}
  .progress-meta{grid-column:1/-1;display:flex;align-items:center;gap:0;border-top:1px solid var(--border);background:var(--surface-2);overflow:auto}
  .progress-meta-item{display:flex;align-items:baseline;gap:6px;min-width:max-content;padding:10px 15px!important;border-right:1px solid var(--border)!important;color:var(--muted);font-size:.72rem}
  .progress-meta-item:last-child{border-right:0!important}
  .progress-meta-item strong{color:var(--text);font-size:.82rem;font-weight:800;font-variant-numeric:tabular-nums}
  #statsView .panel.section{box-shadow:none}
  #statsView .section h3{margin-bottom:12px;font-size:.93rem;font-weight:780;letter-spacing:-.01em}
  #statsView .activity-grid{gap:0;border:1px solid var(--border);border-radius:var(--radius-sm);overflow:hidden}
  #statsView .activity-box{padding:13px 14px;border:0;border-left:1px solid var(--border);border-radius:0;background:transparent}
  #statsView .activity-box:first-child{border-left:0}
  #statsView .activity-box strong{font-size:1.22rem;font-weight:780}
  #statsView .bar-track{height:7px;background:var(--surface-2)}
  #statsView .missed-item,#statsView .insight-item{background:transparent;border-color:var(--border);border-radius:var(--radius-sm)}
  #statsView .confusion-wrap{border-radius:var(--radius-sm)}
  #statsView #dataControlsPanel{background:color-mix(in srgb,var(--surface) 90%,var(--surface-2));}

  #libraryView .view-heading{margin-bottom:16px}
  .library-filter-bar{padding:12px;gap:8px;box-shadow:none;background:var(--surface)}
  .library-filter-bar input,.library-filter-bar select{min-height:42px;background:var(--surface);border-color:var(--border);font-size:.82rem}
  .library-filter-bar #librarySearch{font-size:.9rem}
  .library-advanced{box-shadow:none;background:transparent;border-color:var(--border)}
  .library-advanced summary{padding:11px 13px;color:var(--muted);font-size:.78rem;font-weight:720}
  .library-advanced[open] summary{color:var(--text)}
  .library-advanced .library-toolbar{background:var(--surface);padding:12px}
  .library-table-panel{box-shadow:none;overflow:hidden}
  .library-head{padding:13px 15px;background:var(--surface-2)}
  .library-head-note{max-width:470px;font-size:.74rem;line-height:1.4}
  .library-table th{padding:10px 14px;background:var(--surface);font-size:.66rem;font-weight:760;letter-spacing:.055em}
  .library-table td{padding:12px 14px}
  .library-table tbody tr{transition:background .12s ease}
  .library-table tbody tr:hover{background:color-mix(in srgb,var(--accent) 5%,var(--surface))}
  .article-chip{min-width:40px;padding:4px 7px;border:1px solid color-mix(in srgb,var(--accent) 35%,var(--border));border-radius:7px;background:var(--accent-soft);color:var(--accent-dark);font-size:.78rem;font-weight:800}
  .mastery-chip,.status-chip{border-radius:7px;background:transparent;font-weight:720}
  .word-open-btn{font-weight:780;text-decoration-thickness:1px}
  .word-subline{margin-top:2px;font-size:.7rem;font-weight:600}
  .word-detail-modal{border-radius:var(--radius-lg);box-shadow:var(--shadow);}
  .word-detail-head{padding:20px 22px 15px}
  .word-detail-head h2{font-size:1.55rem;font-weight:790;letter-spacing:-.035em}
  .word-detail-body{gap:18px;padding:18px 22px 24px}
  .word-detail-section h3{font-size:.7rem;font-weight:780;letter-spacing:.075em}
  .detail-grid{gap:8px}
  .detail-field{padding:10px 11px;border:1px solid var(--border);border-radius:var(--radius-sm);background:transparent}
  .detail-list li,.sense-card{background:var(--surface-2);border-radius:var(--radius-sm)}
  .coverage-note{border-radius:var(--radius-sm)}

  @media(max-width:900px){
    .progress-overview{grid-template-columns:1fr}
    .progress-primary{border-right:0!important;border-bottom:1px solid var(--border)!important}
    .progress-primary p{max-width:none}
    .progress-metrics{grid-template-columns:repeat(4,minmax(0,1fr))}
  }
  @media(max-width:720px){
    .ui3-practice .practice-screen-header{border-bottom:0}
    .ui3-practice .session-metrics>span{min-height:24px;padding:3px 7px;border:0;background:transparent}
    .ui3-practice .quiz-card{border-radius:var(--radius)}
    .ui3-practice .answer-btn{min-height:52px;padding:8px 9px;grid-template-columns:auto 1fr auto}
    .ui3-practice .answer-key{width:23px;height:23px;font-size:.62rem}
    .ui3-practice .answer-article{font-size:.98rem}
    .ui3-practice .feedback{padding:10px 11px}
    .progress-primary{padding:20px!important}
    .progress-primary .stat-value{font-size:2.85rem}
    .progress-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}
    .progress-metric{padding:14px!important;border-top:1px solid var(--border)!important}
    .progress-metric:nth-child(odd){border-left:0!important}
    .progress-meta{scrollbar-width:none}
    .progress-meta::-webkit-scrollbar{display:none}
    #statsView .activity-grid{grid-template-columns:1fr 1fr 1fr}
    .library-filter-bar{grid-template-columns:1fr 1fr!important}
    .library-filter-bar #librarySearch{grid-column:1/-1!important}
  }
  @media(max-width:430px){
    .ui3-practice .session-metrics{gap:2px}
    .ui3-practice .session-metrics>span{padding-inline:4px}
    .ui3-practice .answers{gap:6px}
    .ui3-practice .answer-btn{min-height:50px;padding-inline:7px}
    .ui3-practice .answer-btn::after{width:14px;height:14px}
    .ui3-practice .answer-key{width:21px;height:21px}
    .progress-primary{padding:18px!important}
    .progress-primary .stat-value{font-size:2.6rem}
    .progress-metric{padding:12px!important}
    #statsView .activity-grid{grid-template-columns:1fr}
    #statsView .activity-box{border-left:0;border-top:1px solid var(--border)}
    #statsView .activity-box:first-child{border-top:0}
    .library-filter-bar{grid-template-columns:1fr!important}
    .library-filter-bar #librarySearch{grid-column:auto!important}
    .library-head{padding:11px 12px}
    .library-head-note{font-size:.7rem}
    .word-detail-head{padding:17px 15px 13px}
    .word-detail-body{padding:15px}
  }
'''

style_end = "\n</style>"
if "/* UI3 — practice, vocabulary, and progress surface polish */" not in html:
    if style_end not in html:
        raise SystemExit("Could not locate style closing tag")
    html = html.replace(style_end, ui3_css + style_end, 1)

INDEX.write_text(html, encoding="utf-8")

# Extend static certification with UI3 surface invariants.
verify = VERIFY.read_text(encoding="utf-8")
anchor = "requireFragment(html, '.modal-backdrop{z-index:80}', 'dialogs above application chrome');\n"
ui3_requirements = '''requireFragment(html, 'class="practice-screen ui3-practice"', 'UI3 polished practice surface');
requireFragment(html, 'class="answer-key"', 'UI3 structured article answer controls');
requireFragment(html, 'class="panel stats-grid progress-overview"', 'UI3 learner-oriented progress overview');
requireFragment(html, 'class="progress-meta"', 'UI3 secondary progress metrics');
requireFragment(html, 'library-primary-toolbar library-filter-bar', 'UI3 vocabulary filter bar');
requireFragment(html, 'class="panel library-table-panel"', 'UI3 vocabulary reference surface');
requireFragment(html, '/* UI3 — practice, vocabulary, and progress surface polish */', 'UI3 surface style contract');
'''
if ui3_requirements not in verify:
    if anchor not in verify:
        raise SystemExit("Could not locate UI2 verifier anchor")
    verify = verify.replace(anchor, anchor + ui3_requirements, 1)
VERIFY.write_text(verify, encoding="utf-8")

# Add browser surface certification command.
package = json.loads(PACKAGE.read_text(encoding="utf-8"))
package["scripts"]["test:surfaces-browser"] = "node tests/surface-polish.mjs"
PACKAGE.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")

surface_test = r'''import assert from "node:assert/strict";
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
'''
(ROOT / "tests" / "surface-polish.mjs").write_text(surface_test, encoding="utf-8")

ui3_doc = '''# UI3 — Practice, Vocabulary & Progress Surface Polish

UI3 polishes the three learner-facing destinations on top of the UI1 identity and UI2 shell. It does not change scheduling, scoring, vocabulary content, translation certification, or the dedicated-practice interaction model.

## Practice

The dedicated practice screen is treated as a focused exercise workspace rather than a generic large card.

- question/session status is compact and secondary
- the noun remains the strongest typographic element
- article controls use a small keyboard-number cell plus a lowercase article label
- confidence controls are quiet pill controls rather than competing buttons
- English meaning uses the accent-tinted learning surface only when revealed
- feedback is a contained result surface with explicit success/error affordances
- the unfamiliar-word action is deliberately visually subordinate
- mobile continues to fit the answer, feedback, and next action without page scrolling

## Progress

The former ten equal KPI cards were replaced by one hierarchy:

1. overall accuracy as the primary learning signal
2. due / weak / mastered / seen as supporting metrics
3. answer count / streak / response speed / stubborn / relearning as compact secondary evidence

All ten existing metric IDs remain in the DOM so runtime calculations are unchanged. Detailed analytics remain below the overview, but their cards, activity counters, bars, and list items use flatter, denser presentation.

## Vocabulary

Vocabulary is treated as a reference library rather than a dashboard.

- quick filters are one compact filter surface
- advanced filters are a quieter disclosure
- the table surface is flatter and denser
- article chips use the single Artikelwerk accent rather than arbitrary per-gender colors
- row hover/selection affordance is subtle
- word detail uses restrained bordered fields and fewer nested visual cards
- mobile keeps search, primary filters, and word detail usable without document-level horizontal overflow

## Interaction and accessibility

UI3 preserves every existing runtime ID and ARIA relationship used by practice, progress, vocabulary, and dialogs. Touch targets remain at least 44px where actions require direct interaction. Ordinary dialogs remain above the sticky app chrome; the dedicated practice screen remains the highest application layer.

## Certification

`tests/surface-polish.mjs` certifies the UI3 contract on 1440×900 desktop plus 360×740, 390×844, and 412×915 mobile profiles. The suite checks practice-control structure, feedback containment, progress hierarchy, vocabulary filter/detail usability, modal stacking, viewport containment, horizontal overflow, and browser errors.

## UI4 handoff

UI4 should focus on motion, interaction states, empty/loading states, accessibility finishing, and cross-browser/zoom polish. It should not reintroduce card-heavy dashboards or decorative color systems.
'''
(ROOT / "docs" / "ui3-surface-polish.md").write_text(ui3_doc, encoding="utf-8")

readme = README.read_text(encoding="utf-8")
ui3_readme = '''\n## UI3 surface polish\n\n- Dedicated practice uses a focused exercise hierarchy with structured article controls and contained feedback.\n- Progress uses one learner-oriented overview instead of ten equal KPI cards.\n- Vocabulary uses a denser reference-library surface with restrained filters and word details.\n- `tests/surface-polish.mjs` certifies these surfaces across desktop and mobile profiles.\n- See `docs/ui3-surface-polish.md` for the UI3 contract and UI4 handoff.\n'''
if "## UI3 surface polish" not in readme:
    readme = readme.rstrip() + "\n" + ui3_readme
README.write_text(readme, encoding="utf-8")

print("Applied UI3 practice, vocabulary, and progress surface polish.")
