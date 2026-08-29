from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
VERIFY = ROOT / "scripts" / "verify-source.mjs"
PACKAGE = ROOT / "package.json"
CI = ROOT / ".github" / "workflows" / "ci.yml"
README = ROOT / "README.md"

html = INDEX.read_text(encoding="utf-8")
marker = "/* UI5.1 — visual acceptance fixes */"
if marker in html:
    raise SystemExit("UI5.1 already applied")

css = r'''

  /* UI5.1 — visual acceptance fixes */
  :root{--mobile-nav-reserve:104px}
  .ui3-practice .noun{font-size:var(--practice-noun-size,clamp(3.25rem,7.2vw,5.6rem));overflow-wrap:normal;word-break:normal;hyphens:none}
  .ui3-practice .noun.noun-single-line{white-space:nowrap}
  .ui3-practice .noun .sense-cue{white-space:normal}
  .ui3-practice .quiz-card.format-context .noun{white-space:normal;overflow-wrap:break-word;hyphens:auto}
  .ui3-practice .question-wrap{padding:18px 0 16px}
  .ui3-practice #quizContent{grid-template-rows:auto minmax(118px,auto) minmax(0,1fr)}
  .ui3-practice #quizContent>div:last-child{justify-content:flex-end}

  .library-mobile-filter-toggle{display:none}
  .library-primary-filter-controls{display:contents}
  .library-mobile-filter-toggle.has-active{color:var(--accent-dark);border-color:var(--accent)}

  .progress-diagnostics{margin:14px 0 0;border:0}
  .progress-diagnostics>summary{display:none}
  .progress-diagnostics-body{display:block}
  #statsView .section>p.muted{font-size:.82rem!important;line-height:1.5}

  @media(max-width:720px){
    .app{padding-bottom:0}
    main{padding-bottom:calc(var(--mobile-nav-reserve) + env(safe-area-inset-bottom))}
    .view{scroll-margin-bottom:var(--mobile-nav-reserve)}
    .app-nav{isolation:isolate}

    .ui3-practice .noun{font-size:var(--practice-noun-size,clamp(2.7rem,12vw,4.15rem))}
    .ui3-practice .question-wrap{padding:12px 0 10px}

    .library-primary-toolbar{grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center}
    .library-primary-toolbar #librarySearch{grid-column:1/2;min-height:44px}
    .library-mobile-filter-toggle{display:inline-flex;align-items:center;justify-content:center;gap:4px;min-height:44px;white-space:nowrap}
    .library-primary-filter-controls{display:none;grid-column:1/-1;grid-template-columns:1fr 1fr;gap:8px;padding-top:10px}
    .library-primary-toolbar.filters-open .library-primary-filter-controls{display:grid}
    .library-primary-filter-controls select,.library-primary-filter-controls #clearLibraryFiltersBtn{width:100%;min-height:44px}
    .library-primary-filter-controls #clearLibraryFiltersBtn{grid-column:1/-1}

    #statsView .stats-layout{gap:26px}
    #statsView .panel.section{padding:26px 0 12px}
    #statsView .section h3{font-size:1.38rem;margin-bottom:18px}
    #statsView .activity-box span,#statsView .stat-label,#statsView .progress-meta-item span{font-size:.76rem;line-height:1.35}
    .progress-diagnostics{margin-top:28px;border-top:1px solid var(--text)}
    .progress-diagnostics>summary{display:flex;align-items:center;justify-content:space-between;gap:18px;min-height:56px;padding:12px 0;cursor:pointer;list-style:none;font-size:.86rem;font-weight:700}
    .progress-diagnostics>summary::-webkit-details-marker{display:none}
    .progress-diagnostics>summary::after{content:'+';font-family:var(--font-display);font-size:1.4rem;font-weight:500;color:var(--muted)}
    .progress-diagnostics[open]>summary::after{content:'−'}
    .progress-diagnostics>summary small{display:block;margin-left:auto;color:var(--muted);font-size:.72rem;font-weight:500;text-align:right;line-height:1.35}
    .progress-diagnostics-body{padding-top:4px}
  }
  @media(max-width:520px){
    .library-primary-filter-controls{grid-template-columns:1fr}
    .library-primary-filter-controls #clearLibraryFiltersBtn{grid-column:auto}
    .progress-diagnostics>summary small{display:none}
  }
'''
if "\n</style>" not in html:
    raise SystemExit("Closing style tag missing")
html = html.replace("\n</style>", "\n" + css + "\n</style>", 1)

old = '''      <div class="panel library-toolbar library-primary-toolbar library-filter-bar">\n        <input type="search" id="librarySearch" placeholder="Search nouns…" aria-label="Search nouns" />\n        <select id="articleFilter" aria-label="Filter by article">\n          <option value="all">All articles</option><option value="der">der</option><option value="die">die</option><option value="das">das</option>\n        </select>'''
new = '''      <div class="panel library-toolbar library-primary-toolbar library-filter-bar">\n        <input type="search" id="librarySearch" placeholder="Search nouns…" aria-label="Search nouns" />\n        <button type="button" class="ghost-btn library-mobile-filter-toggle" id="libraryMobileFilterToggle" aria-expanded="false" aria-controls="libraryPrimaryFilterControls">Filters <span id="libraryPrimaryFilterCount" aria-hidden="true"></span></button>\n        <div class="library-primary-filter-controls" id="libraryPrimaryFilterControls">\n        <select id="articleFilter" aria-label="Filter by article">\n          <option value="all">All articles</option><option value="der">der</option><option value="die">die</option><option value="das">das</option>\n        </select>'''
if old not in html:
    raise SystemExit("Vocabulary primary-filter start anchor missing")
html = html.replace(old, new, 1)

old = '''        <button type="button" class="ghost-btn" id="clearLibraryFiltersBtn">Clear filters</button>\n      </div>\n\n      <details class="panel library-advanced"'''
new = '''        <button type="button" class="ghost-btn" id="clearLibraryFiltersBtn">Clear filters</button>\n        </div>\n      </div>\n\n      <details class="panel library-advanced"'''
if old not in html:
    raise SystemExit("Vocabulary primary-filter end anchor missing")
html = html.replace(old, new, 1)

anchor = '''      <div class="panel section" style="margin-top:14px">\n        <h3>Response speed</h3>'''
if anchor not in html:
    raise SystemExit("Progress diagnostics start anchor missing")
html = html.replace(anchor, '''      <details class="progress-diagnostics" id="progressDiagnostics" open>\n        <summary><span>More learning diagnostics</span><small>Speed, confusion patterns, stubborn words</small></summary>\n        <div class="progress-diagnostics-body">\n      <div class="panel section" style="margin-top:14px">\n        <h3>Response speed</h3>''', 1)

anchor = '''      <div class="panel section" id="dataControlsPanel" style="margin-top:14px" tabindex="-1">'''
if anchor not in html:
    raise SystemExit("Progress diagnostics end anchor missing")
html = html.replace(anchor, '''        </div>\n      </details>\n\n      <div class="panel section" id="dataControlsPanel" style="margin-top:14px" tabindex="-1">''', 1)

anchor = '''    showEmpty(){\n      TimingAnalytics.clearQuestion();'''
if anchor not in html:
    raise SystemExit("QuizView method anchor missing")
html = html.replace(anchor, '''    fitNounPrompt(){\n      const el=DOM.$("#nounPrompt");\n      const wrap=DOM.$("#questionWrap");\n      if(!el || !wrap || !PracticeScreen.isOpen()) return;\n      const context=DOM.$("#quizCard")?.classList.contains("format-context");\n      el.classList.toggle("noun-single-line",!context);\n      el.style.removeProperty("--practice-noun-size");\n      if(context) return;\n      requestAnimationFrame(()=>{\n        if(!el.isConnected || !PracticeScreen.isOpen()) return;\n        const available=Math.max(120,wrap.clientWidth-4);\n        const mobile=window.innerWidth<=720;\n        let low=mobile?25:38;\n        let high=mobile?68:90;\n        const fits=size=>{ el.style.setProperty("--practice-noun-size",`${size}px`); return el.scrollWidth<=available+1; };\n        if(fits(high)) return;\n        while(high-low>1){\n          const mid=Math.floor((low+high)/2);\n          if(fits(mid)) low=mid; else high=mid;\n        }\n        fits(low);\n      });\n    },\n    showEmpty(){\n      TimingAnalytics.clearQuestion();''', 1)

anchor = '''      DOM.$("#nounPrompt").innerHTML=prompt.html;\n      DOM.$("#modeBadge").textContent'''
if anchor not in html:
    raise SystemExit("Noun render anchor missing")
html = html.replace(anchor, '''      DOM.$("#nounPrompt").innerHTML=prompt.html;\n      this.fitNounPrompt();\n      DOM.$("#modeBadge").textContent''', 1)

anchor = '''      this.updateSubtitle();\n      requestAnimationFrame(()=>DOM.$("#nounPrompt")?.focus({preventScroll:true}));'''
if anchor not in html:
    raise SystemExit("Practice open focus anchor missing")
html = html.replace(anchor, '''      this.updateSubtitle();\n      requestAnimationFrame(()=>{ QuizView.fitNounPrompt(); DOM.$("#nounPrompt")?.focus({preventScroll:true}); });''', 1)

anchor = '''    render(){\n      const f=this.filterValues();'''
if anchor not in html:
    raise SystemExit("Vocabulary render anchor missing")
html = html.replace(anchor, '''    primaryFilterIds:["articleFilter","levelFilter","vocabularyStatusFilter","masteryFilter","variantGenderFilter"],\n    syncPrimaryFilterUI(){\n      const count=this.primaryFilterIds.filter(id=>(DOM.$("#"+id)?.value||"all")!=="all").length;\n      const toggle=DOM.$("#libraryMobileFilterToggle");\n      const label=DOM.$("#libraryPrimaryFilterCount");\n      if(label) label.textContent=count?`(${count})`:"";\n      if(toggle) toggle.classList.toggle("has-active",count>0);\n    },\n    togglePrimaryFilters(force=null){\n      const toolbar=DOM.$(".library-primary-toolbar");\n      const toggle=DOM.$("#libraryMobileFilterToggle");\n      if(!toolbar || !toggle) return;\n      const next=force==null?!toolbar.classList.contains("filters-open"):Boolean(force);\n      toolbar.classList.toggle("filters-open",next);\n      toggle.setAttribute("aria-expanded",next?"true":"false");\n    },\n    render(){\n      const f=this.filterValues();\n      this.syncPrimaryFilterUI();''', 1)

anchor = '''      this.render();\n    }\n  };\n\n  const CoreTrainingModel'''
if anchor not in html:
    raise SystemExit("Vocabulary clear-filter anchor missing")
html = html.replace(anchor, '''      this.togglePrimaryFilters(false);\n      this.render();\n    }\n  };\n\n  const CoreTrainingModel''', 1)

anchor = '''      DOM.$("#clearLibraryFiltersBtn").addEventListener("click",()=>VocabularyView.clearFilters());'''
if anchor not in html:
    raise SystemExit("Filter event anchor missing")
html = html.replace(anchor, '''      DOM.$("#clearLibraryFiltersBtn").addEventListener("click",()=>VocabularyView.clearFilters());\n      DOM.$("#libraryMobileFilterToggle").addEventListener("click",()=>VocabularyView.togglePrimaryFilters());''', 1)

anchor = '''      document.addEventListener("keydown",e=>{'''
if anchor not in html:
    raise SystemExit("Global keyboard anchor missing")
html = html.replace(anchor, '''      window.addEventListener("resize",()=>QuizView.fitNounPrompt(),{passive:true});\n      document.addEventListener("keydown",e=>{''', 1)

anchor = '''      AppUI.bindEvents();\n      ReviewQueueView.render();'''
if anchor not in html:
    raise SystemExit("App init anchor missing")
html = html.replace(anchor, '''      AppUI.bindEvents();\n      if(window.innerWidth<=720){ const diagnostics=DOM.$("#progressDiagnostics"); if(diagnostics) diagnostics.open=false; }\n      ReviewQueueView.render();''', 1)

INDEX.write_text(html, encoding="utf-8")

verify = VERIFY.read_text(encoding="utf-8")
anchor = "requireFragment(html, '.article-chip{min-width:0;padding:0;border:0', 'UI5 typographic article labels');\n"
checks = """requireFragment(html, '/* UI5.1 — visual acceptance fixes */', 'UI5.1 visual acceptance contract');
requireFragment(html, 'fitNounPrompt(){', 'dynamic German-compound fitting');
requireFragment(html, 'noun-single-line', 'single-line standard noun prompt');
requireFragment(html, '--mobile-nav-reserve:104px', 'mobile navigation exclusion zone');
requireFragment(html, 'id=\"libraryMobileFilterToggle\"', 'mobile Vocabulary filter disclosure');
requireFragment(html, 'id=\"progressDiagnostics\"', 'mobile Progress diagnostics disclosure');
"""
if anchor not in verify:
    raise SystemExit("UI5 verifier anchor missing")
verify = verify.replace(anchor, anchor + checks, 1)
doc_anchor = "try { await access(join(rootDir, 'docs', 'ui5-editorial-rebuild.md')); }\ncatch { fail('Missing UI5 editorial rebuild specification.'); }\n"
doc_check = "try { await access(join(rootDir, 'docs', 'ui5-1-visual-acceptance.md')); }\ncatch { fail('Missing UI5.1 visual acceptance specification.'); }\n"
if doc_anchor not in verify:
    raise SystemExit("UI5 doc verifier anchor missing")
verify = verify.replace(doc_anchor, doc_anchor + doc_check, 1)
VERIFY.write_text(verify, encoding="utf-8")

package = json.loads(PACKAGE.read_text(encoding="utf-8"))
package["scripts"]["test:visual-acceptance-browser"] = "node tests/visual-acceptance.mjs"
PACKAGE.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")

ci = CI.read_text(encoding="utf-8")
ci = ci.replace("name: Source, certified content, deterministic build, and editorial UI", "name: Source, certified content, deterministic build, and visual acceptance")
ci = ci.replace("Verify source, content certification, editorial surfaces, accessibility, and deterministic artifact", "Verify source, content certification, visual-acceptance surfaces, accessibility, and deterministic artifact")
ci = ci.replace("Run full browser and editorial certification", "Run full browser, editorial, and visual-acceptance certification")
needle = "          ARTIKELWERK_URL=http://127.0.0.1:4173 npm run test:editorial-browser\n"
if needle not in ci:
    raise SystemExit("Permanent CI editorial suite anchor missing")
ci = ci.replace(needle, needle + "          ARTIKELWERK_URL=http://127.0.0.1:4173 npm run test:visual-acceptance-browser\n", 1)
CI.write_text(ci, encoding="utf-8")

README.write_text(
    README.read_text(encoding="utf-8").rstrip()
    + "\n\n## UI5.1 visual acceptance fixes\n\nUI5.1 keeps the editorial UI5 direction while fixing the release-gate defects found in rendered acceptance review: dynamic fitting for long German compounds, mobile bottom-navigation clearance, compact mobile Vocabulary filters, a calmer mobile Progress hierarchy, and tighter desktop Practice spacing. See `docs/ui5-1-visual-acceptance.md`.\n",
    encoding="utf-8",
)

print("Applied UI5.1 visual acceptance fixes")
