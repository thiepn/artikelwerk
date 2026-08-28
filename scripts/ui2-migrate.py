from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
VERIFY = ROOT / "scripts" / "verify-source.mjs"
PACKAGE = ROOT / "package.json"
README = ROOT / "README.md"

html = INDEX.read_text(encoding="utf-8")

header_pattern = re.compile(
    r'  <header>\n.*?  </header>\n\n  <nav class="tabs" aria-label="Main navigation" role="tablist">\n.*?  </nav>\n',
    re.S,
)
new_header = '''  <header class="app-header">
    <div class="brand">
      <div class="brand-mark" aria-hidden="true"><img src="favicon.svg" alt="" width="40" height="40"></div>
      <div class="brand-copy"><h1>Artikelwerk</h1><p>German noun gender · C1/C2</p></div>
    </div>

    <nav class="tabs app-nav" aria-label="Main navigation" role="tablist">
      <button type="button" class="tab active" id="tabPractice" data-view="practice" role="tab" aria-selected="true" aria-controls="practiceView" tabindex="0">
        <span class="nav-icon" aria-hidden="true"><svg viewBox="0 0 24 24" focusable="false"><path d="M8 5.5v13l10-6.5z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg></span>
        <span class="nav-label">Practice</span>
      </button>
      <button type="button" class="tab" id="tabStats" data-view="stats" role="tab" aria-selected="false" aria-controls="statsView" tabindex="-1">
        <span class="nav-icon" aria-hidden="true"><svg viewBox="0 0 24 24" focusable="false"><path d="M5 18v-5M12 18V7M19 18v-9" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M4 20h16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></span>
        <span class="nav-label">Progress</span>
      </button>
      <button type="button" class="tab" id="tabLibrary" data-view="library" role="tab" aria-selected="false" aria-controls="libraryView" tabindex="-1">
        <span class="nav-icon" aria-hidden="true"><svg viewBox="0 0 24 24" focusable="false"><path d="M6.5 4.5h9a2 2 0 0 1 2 2v13h-9a2 2 0 0 1-2-2z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M8.5 8h6M8.5 11.5h5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></span>
        <span class="nav-label">Vocabulary</span>
      </button>
    </nav>

    <div class="header-actions">
      <button class="ghost-btn header-data-btn" id="resetBtn" aria-label="Open progress and backup controls">Data</button>
      <button class="icon-btn" id="themeBtn" aria-label="Switch to dark mode" title="Switch to dark mode">◐</button>
    </div>
  </header>
'''
html, header_count = header_pattern.subn(new_header, html, count=1)
if header_count != 1:
    raise SystemExit(f"UI2 header replacement expected 1 match, found {header_count}")

practice_pattern = re.compile(
    r'(    <section class="view active" id="practiceView" role="tabpanel" aria-labelledby="tabPractice" aria-hidden="false">\n).*?(      <section class="practice-screen" id="practiceScreen")',
    re.S,
)
practice_home = '''    <section class="view active" id="practiceView" role="tabpanel" aria-labelledby="tabPractice" aria-hidden="false">
      <section class="panel practice-hero" aria-labelledby="practiceHeroTitle">
        <div class="practice-hero-main">
          <span class="section-kicker">Focused practice</span>
          <h2 id="practiceHeroTitle">Make German articles automatic.</h2>
          <p>Train difficult C1/C2 nouns in a dedicated screen where the word, English meaning, answer choices, and feedback stay in one place.</p>
          <div class="practice-hero-actions">
            <button type="button" class="primary-btn practice-hero-btn" id="openPracticeBtn">Start practice</button>
            <span class="practice-hero-note">Uses your session settings below.</span>
          </div>
        </div>
        <div class="practice-hero-articles" aria-hidden="true">
          <span>der</span><span>die</span><span>das</span>
        </div>
      </section>

      <div class="practice-support-grid">
        <section class="panel review-queue-panel" aria-labelledby="reviewQueueHeading">
          <div class="review-queue-head">
            <div class="review-queue-title">
              <span class="section-kicker">Spaced repetition</span>
              <h2 id="reviewQueueHeading">Today's review</h2>
              <p id="reviewQueueSummary">Building your SRS queue…</p>
            </div>
            <button class="primary-btn review-btn" id="startReviewBtn">Review due words</button>
          </div>
          <div class="queue-counters" aria-label="Review queue status">
            <div class="queue-stat is-urgent"><strong id="queueOverdue">0</strong><span>Overdue</span></div>
            <div class="queue-stat is-due"><strong id="queueDue">0</strong><span>Due now</span></div>
            <div class="queue-stat"><strong id="queueNew">0</strong><span>New</span></div>
            <div class="queue-stat"><strong id="queueLearning">0</strong><span>Learning</span></div>
            <div class="queue-stat"><strong id="queueRelearning">0</strong><span>Relearning</span></div>
            <div class="queue-stat" hidden><strong id="queueMastered">0</strong><span>Mastered</span></div>
            <div class="queue-stat"><strong id="queueLeeches">0</strong><span>Stubborn</span></div>
          </div>
        </section>

        <section class="panel practice-setup-panel" aria-labelledby="practiceSetupHeading">
          <div class="practice-setup-head">
            <span class="section-kicker">Session setup</span>
            <h2 id="practiceSetupHeading">Choose how to practice</h2>
            <p>Keep the defaults for a quick session, or adjust the mode, format, level, and length.</p>
          </div>
          <div class="controls" id="practiceSetup">
            <div class="control">
              <label for="modeSelect">Mode</label>
              <select id="modeSelect">
                <option value="practice">Practice</option>
                <option value="review">Today's Review</option>
                <option value="adaptive">Adaptive (SRS)</option>
                <option value="mistakes">Mistakes</option>
                <option value="weak">Weak Words</option>
                <option value="random">Random</option>
                <option value="timed">Timed Challenge (60s)</option>
                <option value="unknownWords">Unknown Words</option>
              </select>
            </div>
            <div class="control" id="formatControl">
              <label for="formatSelect">Question format</label>
              <select id="formatSelect">
                <option value="standard">Standard</option>
                <option value="context">Context</option>
                <option value="production">Production</option>
              </select>
            </div>
            <div class="control">
              <label for="difficultySelect">Difficulty</label>
              <select id="difficultySelect">
                <option value="all">All advanced levels</option>
                <option value="1">Level 1 — Advanced</option>
                <option value="2">Level 2 — Difficult</option>
                <option value="3">Level 3 — Very Difficult</option>
              </select>
            </div>
            <div class="control" id="sessionControl">
              <label for="sessionSelect">Session</label>
              <select id="sessionSelect">
                <option value="10">10 questions</option>
                <option value="20" selected>20 questions</option>
                <option value="50">50 questions</option>
                <option value="100">100 questions</option>
                <option value="endless">Endless</option>
              </select>
            </div>
            <div class="control practice-setup-action">
              <button class="primary-btn" id="newSessionBtn">Start with these settings</button>
            </div>
          </div>
        </section>
      </div>

      <section class="practice-screen" id="practiceScreen'''
html, practice_count = practice_pattern.subn(practice_home, html, count=1)
if practice_count != 1:
    raise SystemExit(f"UI2 practice hierarchy replacement expected 1 match, found {practice_count}")

stats_open = '    <section class="view" id="statsView" role="tabpanel" aria-labelledby="tabStats" aria-hidden="true">\n'
stats_heading = stats_open + '''      <div class="view-heading">
        <span class="section-kicker">Progress</span>
        <h2>Your learning picture</h2>
        <p>See what is due, where article recall is improving, and which words need another pass.</p>
      </div>
'''
if stats_open not in html:
    raise SystemExit("Could not locate stats view for UI2 heading")
html = html.replace(stats_open, stats_heading, 1)

library_open = '    <section class="view" id="libraryView" role="tabpanel" aria-labelledby="tabLibrary" aria-hidden="true">\n'
library_heading = library_open + '''      <div class="view-heading">
        <span class="section-kicker">Vocabulary</span>
        <h2>Your reviewed noun library</h2>
        <p>Browse 1,000 advanced nouns with certified English glosses, article guidance, examples, and learning status.</p>
      </div>
'''
if library_open not in html:
    raise SystemExit("Could not locate library view for UI2 heading")
html = html.replace(library_open, library_heading, 1)

css_marker = '\n\n  /* V1.1 dedicated practice screen: fixed viewport, stable feedback, zero page movement. */'
ui2_css = r'''

  /* UI2 app shell, navigation, and main-screen hierarchy */
  .app{max-width:1200px;padding:0 24px 40px}
  .app-header{position:sticky;top:0;z-index:40;display:grid;grid-template-columns:minmax(210px,1fr) auto minmax(210px,1fr);align-items:center;gap:22px;min-height:72px;margin:0 0 30px;background:var(--bg);border-bottom:1px solid var(--border)}
  .app-header .brand{justify-self:start;min-width:0}
  .brand-copy{min-width:0}
  .app-header .header-actions{justify-self:end}
  .app-nav{align-self:stretch;justify-self:center;display:flex;align-items:stretch;gap:4px;margin:0;padding:0;border:0;background:transparent;overflow:visible;box-shadow:none;scrollbar-width:none}
  .app-nav::-webkit-scrollbar{display:none}
  .app-nav .tab{position:relative;display:flex;align-items:center;justify-content:center;gap:7px;min-height:72px;padding:0 14px;border:0;background:transparent;color:var(--muted);border-radius:0;box-shadow:none;font-size:.86rem;font-weight:720}
  .app-nav .tab::after{content:"";position:absolute;left:13px;right:13px;bottom:-1px;height:2px;background:transparent}
  .app-nav .tab:hover{color:var(--text)}
  .app-nav .tab.active,.app-nav .tab[aria-selected="true"]{background:transparent;color:var(--text);box-shadow:none}
  .app-nav .tab.active::after,.app-nav .tab[aria-selected="true"]::after{background:var(--accent)}
  .nav-icon{display:grid;place-items:center;width:19px;height:19px;flex:0 0 auto}
  .nav-icon svg{display:block;width:19px;height:19px}
  .nav-label{line-height:1}
  .view-heading{max-width:700px;margin:0 0 20px}
  .view-heading h2{margin:3px 0 5px;font-size:clamp(1.45rem,2.6vw,1.9rem);line-height:1.15;letter-spacing:-.035em;font-weight:790}
  .view-heading p{margin:0;color:var(--muted);font-size:.91rem;line-height:1.55}
  .section-kicker{display:block;color:var(--accent);font-size:.69rem;font-weight:820;letter-spacing:.085em;text-transform:uppercase}

  .practice-hero{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:28px;margin-bottom:14px;padding:28px 30px;box-shadow:none}
  .practice-hero-main{max-width:700px}
  .practice-hero h2{max-width:620px;margin:5px 0 9px;font-size:clamp(1.75rem,3vw,2.35rem);line-height:1.08;letter-spacing:-.045em;font-weight:800}
  .practice-hero p{max-width:670px;margin:0;color:var(--muted);font-size:.93rem;line-height:1.55}
  .practice-hero-actions{display:flex;align-items:center;gap:13px;margin-top:20px;flex-wrap:wrap}
  .practice-hero-btn{min-width:170px;min-height:48px;padding-inline:20px}
  .practice-hero-note{color:var(--muted);font-size:.78rem}
  .practice-hero-articles{display:grid;grid-template-columns:repeat(3,auto);gap:7px;align-self:center}
  .practice-hero-articles span{display:grid;place-items:center;min-width:54px;height:42px;padding:0 12px;border:1px solid var(--border);border-radius:var(--radius-sm);background:var(--surface-2);color:var(--text-soft);font-size:.88rem;font-weight:800;letter-spacing:.01em}
  .practice-hero-articles span:first-child{border-color:color-mix(in srgb,var(--accent) 45%,var(--border));color:var(--accent-dark);background:var(--accent-soft)}
  .practice-support-grid{display:grid;grid-template-columns:minmax(0,.92fr) minmax(0,1.08fr);gap:14px;align-items:start}
  .practice-support-grid .review-queue-panel{margin:0;padding:20px;box-shadow:none}
  .practice-support-grid .review-queue-head{align-items:stretch;flex-direction:column;gap:14px;margin-bottom:16px}
  .practice-support-grid .review-queue-title h2,.practice-setup-head h2{margin:3px 0 5px;font-size:1.08rem;letter-spacing:-.02em}
  .practice-support-grid .review-queue-title p,.practice-setup-head p{margin:0;color:var(--muted);font-size:.82rem;line-height:1.45}
  .practice-support-grid .review-btn{width:100%;min-height:44px}
  .practice-support-grid .queue-counters{grid-template-columns:repeat(3,minmax(0,1fr));gap:7px}
  .practice-support-grid .queue-stat{padding:9px 10px;background:var(--surface-2);border-radius:var(--radius-sm)}
  .practice-support-grid .queue-stat strong{font-size:1.05rem}
  .practice-support-grid .queue-stat span{font-size:.64rem;letter-spacing:.035em}
  .practice-setup-panel{padding:20px;box-shadow:none}
  .practice-setup-panel .controls{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:16px 0 0;padding:0;border:0;background:transparent;box-shadow:none}
  .practice-setup-panel .practice-setup-action{grid-column:1/-1;margin-top:2px}
  .practice-setup-panel #newSessionBtn{width:100%}

  @media(max-width:940px) and (min-width:721px){
    .app-header{grid-template-columns:1fr auto;gap:10px;min-height:auto;padding-top:10px}
    .app-header .app-nav{grid-column:1/-1;grid-row:2;justify-self:start;width:100%;min-height:48px}
    .app-nav .tab{min-height:48px;padding:0 13px}
    .practice-support-grid{grid-template-columns:1fr}
    .practice-setup-panel .controls{grid-template-columns:repeat(4,minmax(0,1fr))}
    .practice-setup-panel .practice-setup-action{grid-column:1/-1}
  }

  @media(max-width:720px){
    html{scroll-padding-top:72px}
    .app{padding:0 14px calc(86px + env(safe-area-inset-bottom))}
    .app-header{position:sticky;top:0;z-index:60;grid-template-columns:minmax(0,1fr) auto;gap:10px;min-height:62px;margin:0 -14px 20px;padding:0 14px;background:var(--bg);border-bottom:1px solid var(--border)}
    .app-header .brand-mark{width:36px;height:36px}
    .app-header .brand p{display:none}
    .app-header .header-actions{margin-left:0}
    .app-header .header-data-btn{min-width:44px;padding-inline:10px;font-size:.78rem}
    .app-nav{position:fixed;left:0;right:0;bottom:0;top:auto;z-index:70;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));width:100%;min-height:64px;margin:0;padding:0 8px env(safe-area-inset-bottom);background:var(--surface);border:0;border-top:1px solid var(--border);border-radius:0;box-shadow:0 -4px 18px rgba(28,36,33,.055);overflow:visible}
    [data-theme="dark"] .app-nav{box-shadow:0 -4px 18px rgba(0,0,0,.18)}
    .app-nav .tab{flex-direction:column;gap:3px;min-height:63px;padding:7px 4px 6px;font-size:.68rem;line-height:1;color:var(--muted)}
    .app-nav .tab::after{left:24%;right:24%;top:-1px;bottom:auto;height:2px}
    .app-nav .tab.active,.app-nav .tab[aria-selected="true"]{color:var(--accent-dark);background:transparent}
    .nav-icon,.nav-icon svg{width:20px;height:20px}
    body.practice-open .app-nav{visibility:hidden}
    .view-heading{margin-bottom:16px}
    .view-heading h2{font-size:1.5rem}
    .practice-hero{grid-template-columns:1fr;gap:18px;padding:22px 20px;margin-bottom:12px}
    .practice-hero h2{font-size:clamp(1.7rem,8vw,2.05rem)}
    .practice-hero-actions{align-items:stretch;flex-direction:column;margin-top:18px}
    .practice-hero-btn{width:100%}
    .practice-hero-note{text-align:center}
    .practice-hero-articles{grid-template-columns:repeat(3,1fr);width:100%}
    .practice-hero-articles span{min-width:0;width:100%}
    .practice-support-grid{grid-template-columns:1fr;gap:12px}
    .practice-support-grid .review-queue-panel,.practice-setup-panel{padding:16px}
    .practice-support-grid .queue-counters{grid-template-columns:repeat(3,minmax(0,1fr))}
    .practice-setup-panel .controls{grid-template-columns:1fr 1fr}
  }

  @media(max-width:520px){
    .practice-support-grid .queue-counters{grid-template-columns:repeat(2,minmax(0,1fr))}
    .practice-setup-panel .controls{grid-template-columns:1fr}
    .practice-setup-panel .practice-setup-action{grid-column:auto}
  }
'''
if css_marker not in html:
    raise SystemExit("Could not locate dedicated-practice CSS marker for UI2")
html = html.replace(css_marker, ui2_css + css_marker, 1)

# Remove now-unused dedicated-launch CSS rules from the legacy practice block.
html = re.sub(r'\n  \.practice-launch-panel\{[^\n]*\}\n  \.practice-launch-copy\{[^\n]*\}\n  \.practice-launch-eyebrow\{[^\n]*\}\n  \.practice-launch-panel h2\{[^\n]*\}\n  \.practice-launch-panel p\{[^\n]*\}\n  \.practice-launch-btn\{[^\n]*\}\n', '\n', html, count=1)
html = html.replace('    .practice-launch-panel{align-items:stretch;flex-direction:column;padding:16px}\n    .practice-launch-btn{width:100%;min-width:0}\n', '', 1)

INDEX.write_text(html, encoding="utf-8")

verify = VERIFY.read_text(encoding="utf-8")
anchor = "requireFragment(html, '<title>Artikelwerk', 'application title');\n"
checks = """requireFragment(html, 'class=\"app-header\"', 'UI2 integrated application header');
requireFragment(html, 'class=\"tabs app-nav\"', 'UI2 primary navigation');
requireFragment(html, '<span class=\"nav-label\">Progress</span>', 'learner-facing Progress navigation label');
requireFragment(html, 'class=\"panel practice-hero\"', 'UI2 practice hero');
requireFragment(html, 'class=\"practice-support-grid\"', 'UI2 supporting practice hierarchy');
requireFragment(html, 'id=\"practiceSetupHeading\"', 'UI2 session setup heading');
requireFragment(html, 'Your learning picture', 'progress view heading');
requireFragment(html, 'Your reviewed noun library', 'vocabulary view heading');
requireFragment(html, 'position:fixed;left:0;right:0;bottom:0;top:auto;z-index:70', 'mobile bottom navigation');
requireFragment(html, 'grid-template-columns:minmax(210px,1fr) auto minmax(210px,1fr)', 'desktop shell layout');
"""
if checks not in verify:
    if anchor not in verify:
        raise SystemExit("Could not locate verification insertion anchor")
    verify = verify.replace(anchor, anchor + checks, 1)
VERIFY.write_text(verify, encoding="utf-8")

package = json.loads(PACKAGE.read_text(encoding="utf-8"))
package["scripts"]["test:shell-browser"] = "node tests/app-shell.mjs"
PACKAGE.write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

shell_test = r'''import assert from "node:assert/strict";
import fs from "node:fs/promises";
import { chromium } from "playwright";

const BASE_URL=process.env.ARTIKELWERK_URL||"http://127.0.0.1:4173";
await fs.mkdir("test-artifacts",{recursive:true});

async function noHorizontalOverflow(page,label){
  const size=await page.evaluate(()=>({scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth}));
  assert.ok(size.scrollWidth<=size.clientWidth+1,`${label}: horizontal overflow ${size.scrollWidth} > ${size.clientWidth}`);
}

async function desktop(browser){
  const context=await browser.newContext({viewport:{width:1440,height:900}});
  const page=await context.newPage();
  const errors=[];
  page.on("pageerror",e=>errors.push(e.message));
  page.on("console",m=>{if(m.type()==="error") errors.push(m.text());});
  await page.goto(BASE_URL,{waitUntil:"networkidle"});
  assert.equal(await page.locator(".app-header .app-nav").count(),1,"desktop nav must live inside app header");
  assert.equal(await page.locator(".app-nav .tab").count(),3,"desktop shell must expose three primary destinations");
  const header=await page.locator(".app-header").boundingBox();
  const hero=await page.locator(".practice-hero").boundingBox();
  const support=await page.locator(".practice-support-grid").boundingBox();
  assert.ok(header&&hero&&support,"desktop shell boxes unavailable");
  assert.ok(hero.y>=header.y+header.height-1,"practice hero must follow app header");
  assert.ok(support.y>=hero.y+hero.height-1,"supporting practice content must follow hero");
  assert.equal(await page.locator("#openPracticeBtn").isVisible(),true,"primary practice CTA must be visible");
  await page.locator("#tabStats").click();
  await page.locator("#statsView.active").waitFor({state:"visible"});
  assert.match((await page.locator("#statsView .view-heading h2").textContent())||"",/learning picture/i);
  await page.locator("#tabLibrary").click();
  await page.locator("#libraryView.active").waitFor({state:"visible"});
  assert.match((await page.locator("#libraryView .view-heading h2").textContent())||"",/reviewed noun library/i);
  await page.locator("#tabPractice").click();
  await page.locator("#practiceView.active").waitFor({state:"visible"});
  await noHorizontalOverflow(page,"desktop");
  assert.deepEqual(errors,[],`desktop shell browser errors: ${errors.join(" | ")}`);
  await page.screenshot({path:"test-artifacts/shell-desktop-1440x900.png",fullPage:false});
  await context.close();
}

async function mobile(browser,width,height){
  const context=await browser.newContext({viewport:{width,height},isMobile:true,hasTouch:true,deviceScaleFactor:1});
  const page=await context.newPage();
  const errors=[];
  page.on("pageerror",e=>errors.push(e.message));
  page.on("console",m=>{if(m.type()==="error") errors.push(m.text());});
  await page.goto(BASE_URL,{waitUntil:"networkidle"});
  const nav=page.locator(".app-nav");
  const navBox=await nav.boundingBox();
  assert.ok(navBox,`${width}x${height}: bottom nav has no box`);
  const navPosition=await nav.evaluate(el=>getComputedStyle(el).position);
  assert.equal(navPosition,"fixed",`${width}x${height}: navigation must be fixed on mobile`);
  assert.ok(Math.abs(navBox.y+navBox.height-height)<=2,`${width}x${height}: nav must meet viewport bottom`);
  assert.equal(await page.locator(".app-header .brand").isVisible(),true,`${width}x${height}: compact top brand must remain visible`);
  assert.equal(await page.locator("#openPracticeBtn").isVisible(),true,`${width}x${height}: primary practice CTA must be visible`);
  const hero=await page.locator(".practice-hero").boundingBox();
  const support=await page.locator(".practice-support-grid").boundingBox();
  assert.ok(hero&&support&&support.y>=hero.y+hero.height-1,`${width}x${height}: practice hierarchy order is wrong`);
  for(const [tab,view] of [["#tabStats","#statsView"],["#tabLibrary","#libraryView"],["#tabPractice","#practiceView"]]){
    await page.locator(tab).click();
    await page.locator(`${view}.active`).waitFor({state:"visible"});
    const after=await nav.boundingBox();
    assert.ok(after&&Math.abs(after.y+after.height-height)<=2,`${width}x${height}: nav moved after ${tab}`);
  }
  await noHorizontalOverflow(page,`${width}x${height}`);
  assert.deepEqual(errors,[],`${width}x${height}: shell browser errors: ${errors.join(" | ")}`);
  await page.screenshot({path:`test-artifacts/shell-mobile-${width}x${height}.png`,fullPage:false});
  await context.close();
}

const browser=await chromium.launch({headless:true});
try{
  await desktop(browser);
  await mobile(browser,360,740);
  await mobile(browser,390,844);
  await mobile(browser,412,915);
  console.log("UI2 app-shell browser verification passed.");
}finally{await browser.close();}
'''
(ROOT / "tests" / "app-shell.mjs").write_text(shell_test, encoding="utf-8")

ui2_doc = '''# UI2 — App Shell, Navigation & Main-Screen Hierarchy

## Goal

Make Artikelwerk behave and read like a focused language-learning application rather than a generic analytics dashboard, without changing the learning engine or certified content.

## Application shell

### Desktop

The brand, primary navigation, and utility actions now share one integrated header. Primary destinations are:

1. **Practice** — the learning task.
2. **Progress** — learner-facing interpretation of statistics.
3. **Vocabulary** — the reviewed noun library.

The navigation uses the existing tab semantics and IDs, preserving keyboard behavior and application state.

### Mobile

Primary navigation moves to a persistent bottom bar. The compact top bar retains identity, data controls, and theme control. This separates global navigation from the learning content and avoids a sticky tab strip competing with the first practice card.

The dedicated practice dialog remains above the app shell and hides the bottom navigation while open.

## Practice hierarchy

The Practice screen now reads in this order:

1. **Primary practice hero** — one dominant Start practice action.
2. **Today's review** — due/relearning state and a direct review action.
3. **Session setup** — mode, format, difficulty, and length controls.

The setup controls remain visible and fully functional; they are visually secondary rather than hidden behind disclosure UI.

## Progress hierarchy

The Statistics destination is labeled **Progress** in navigation while retaining the existing internal view ID. A concise screen heading explains the purpose before presenting metrics.

## Vocabulary hierarchy

Vocabulary receives a screen heading before filters and tables, so search/filter controls no longer appear without context.

## Accessibility and responsive rules

- Existing `role=tablist`, `role=tab`, `aria-selected`, and `aria-controls` relationships are preserved.
- Mobile navigation retains 44px+ touch targets.
- No horizontal document overflow is allowed at certified widths.
- Dedicated practice remains a fixed no-scroll modal and remains visually above the shell.
- Navigation remains keyboard-addressable on desktop.
- No new network dependencies, icon fonts, or remote UI libraries were introduced.

## UI3 handoff

UI3 should polish the individual screens within this hierarchy: practice-card presentation, answer/feedback states, vocabulary rows/details, and progress visualizations. It should not rework the global shell again unless device testing exposes a concrete usability defect.
'''
(ROOT / "docs" / "ui2-app-shell.md").write_text(ui2_doc, encoding="utf-8")

readme = README.read_text(encoding="utf-8")
readme_append = '''

## UI2 application shell

- Desktop primary navigation is integrated into the application header.
- Mobile primary navigation uses a fixed bottom bar while practice remains a full-screen modal.
- Practice is ordered as primary action → review queue → session setup.
- `tests/app-shell.mjs` certifies shell hierarchy and navigation at desktop and mobile widths.
- See `docs/ui2-app-shell.md` for the shell contract and UI3 handoff.
'''
if "## UI2 application shell" not in readme:
    readme += readme_append
README.write_text(readme, encoding="utf-8")

print("Applied UI2 app shell, navigation, hierarchy, tests, and documentation.")
