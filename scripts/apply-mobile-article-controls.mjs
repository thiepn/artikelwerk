import { readFile, writeFile } from 'node:fs/promises';

const path='index.html';
let source=await readFile(path,'utf8');

function replaceOnce(needle,replacement,label){
  const first=source.indexOf(needle);
  if(first<0) throw new Error(`Missing patch marker: ${label}`);
  if(source.indexOf(needle,first+needle.length)>=0) throw new Error(`Patch marker is not unique: ${label}`);
  source=source.slice(0,first)+replacement+source.slice(first+needle.length);
}

const css=String.raw`

  /* Mobile article-control preferences: Standard (default), Bottom Bar, Stacked. */
  #settingsBtn svg{display:block;width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
  .settings-modal{max-width:580px}
  .settings-modal-head{display:flex;align-items:flex-start;justify-content:space-between;gap:18px;margin-bottom:20px}
  .settings-modal-head h2{margin:0 0 5px}
  .settings-modal-head p{margin:0;font-size:.86rem;line-height:1.5}
  .settings-section h3{margin:0 0 5px;font-size:.94rem}
  .settings-section>p{margin:0 0 13px;font-size:.82rem;line-height:1.5}
  .article-layout-options{display:grid;gap:8px}
  .article-layout-choice{display:grid;grid-template-columns:auto minmax(0,1fr);align-items:start;gap:11px;min-height:58px;padding:12px 13px;border:1px solid var(--border);border-radius:var(--radius-sm);background:var(--surface);cursor:pointer;transition:background .12s ease,border-color .12s ease,box-shadow .12s ease}
  .article-layout-choice:hover{background:var(--surface-2);border-color:var(--border-strong)}
  .article-layout-choice:has(input:checked){border-color:var(--accent);background:var(--accent-soft);box-shadow:inset 3px 0 0 var(--accent)}
  .article-layout-choice input{width:18px;height:18px;margin:2px 0 0;accent-color:var(--accent)}
  .article-layout-copy{display:grid;gap:3px;min-width:0}
  .article-layout-copy strong{font-size:.9rem}
  .article-layout-copy small{color:var(--muted);font-size:.76rem;line-height:1.4}
  .settings-footnote{margin:14px 0 0!important;font-size:.75rem!important}

  .practice-screen[data-article-controls="bottom-bar"] #quizContent,
  .practice-screen[data-article-controls="stacked"] #quizContent{overflow-y:auto;overscroll-behavior:contain;scrollbar-gutter:stable}

  .practice-screen[data-article-controls="bottom-bar"] .answers{
    position:fixed;z-index:96;
    left:max(8px,env(safe-area-inset-left));right:max(8px,env(safe-area-inset-right));bottom:max(8px,env(safe-area-inset-bottom));
    width:auto;max-width:760px;margin-inline:auto;padding:6px;
    grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;
    border:1px solid var(--border);border-radius:12px;background:color-mix(in srgb,var(--surface) 94%,transparent);
    box-shadow:0 -8px 28px rgba(20,27,40,.12);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)
  }
  [data-theme="dark"] .practice-screen[data-article-controls="bottom-bar"] .answers{box-shadow:0 -8px 28px rgba(0,0,0,.3)}
  .practice-screen[data-article-controls="bottom-bar"] .answer-btn{min-height:56px;padding:9px 7px;touch-action:manipulation}
  .practice-screen[data-article-controls="bottom-bar"] .quiz-card:not(.format-production):not(.unknown-learning) #quizContent>div:last-child{padding-bottom:78px}
  .practice-screen[data-article-controls="bottom-bar"] .quiz-card.has-feedback:not(.format-production):not(.unknown-learning) #quizContent>div:last-child{padding-bottom:72px}

  .practice-screen[data-article-controls="stacked"] .answers{grid-template-columns:1fr;gap:7px;max-width:560px;margin:10px auto 0}
  .practice-screen[data-article-controls="stacked"] .answer-btn{min-height:54px;padding:9px 12px;touch-action:manipulation}

  @media(max-width:700px){
    .settings-modal{width:100%}
    .practice-screen[data-article-controls="bottom-bar"] .answers{left:max(6px,env(safe-area-inset-left));right:max(6px,env(safe-area-inset-right));bottom:max(6px,env(safe-area-inset-bottom));border-radius:10px;padding:5px}
    .practice-screen[data-article-controls="bottom-bar"] .answer-btn{min-height:54px}
    .practice-screen[data-article-controls="stacked"] .answers{max-width:none;width:100%;gap:6px;margin-top:8px}
    .practice-screen[data-article-controls="stacked"] .answer-btn{min-height:52px}
  }
`;
replaceOnce('\n</style>\n</head>',`${css}\n</style>\n</head>`,'style closing tag');

const headerNeedle='      <button class="ghost-btn header-data-btn" id="resetBtn" aria-label="Open progress and backup controls">Data</button>\n      <button class="icon-btn" id="themeBtn" aria-label="Switch to dark mode" aria-pressed="false" title="Switch to dark mode">◐</button>';
const headerReplacement='      <button class="ghost-btn header-data-btn" id="resetBtn" aria-label="Open progress and backup controls">Data</button>\n      <button class="icon-btn" id="settingsBtn" aria-label="Open settings" title="Settings"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h10M18 7h2M4 17h2M10 17h10M14 4v6M6 14v6"/></svg></button>\n      <button class="icon-btn" id="themeBtn" aria-label="Switch to dark mode" aria-pressed="false" title="Switch to dark mode">◐</button>';
replaceOnce(headerNeedle,headerReplacement,'header actions');

const settingsModal=String.raw`<div class="modal-backdrop" id="settingsModal" role="dialog" aria-modal="true" aria-labelledby="settingsTitle" aria-describedby="settingsDescription" aria-hidden="true">
  <div class="modal settings-modal">
    <div class="settings-modal-head">
      <div>
        <h2 id="settingsTitle" tabindex="-1">Settings</h2>
        <p id="settingsDescription">Adjust how Artikelwerk behaves on this device.</p>
      </div>
      <button type="button" class="icon-btn" id="settingsCloseBtn" aria-label="Close settings">×</button>
    </div>
    <section class="settings-section" aria-labelledby="articleControlsHeading">
      <h3 id="articleControlsHeading">Article controls</h3>
      <p>Choose where <strong>der</strong>, <strong>die</strong>, and <strong>das</strong> appear during practice.</p>
      <div class="article-layout-options" role="radiogroup" aria-labelledby="articleControlsHeading">
        <label class="article-layout-choice">
          <input type="radio" name="articleControlsLayout" value="standard">
          <span class="article-layout-copy"><strong>Standard</strong><small>Keep the current three-button row. This remains the default.</small></span>
        </label>
        <label class="article-layout-choice">
          <input type="radio" name="articleControlsLayout" value="bottom-bar">
          <span class="article-layout-copy"><strong>Bottom Bar</strong><small>Pin all three article buttons to a thumb-reachable bar at the bottom of the practice screen.</small></span>
        </label>
        <label class="article-layout-choice">
          <input type="radio" name="articleControlsLayout" value="stacked">
          <span class="article-layout-copy"><strong>Stacked</strong><small>Place der, die, and das in three full-width rows near the bottom for easy left- or right-handed tapping.</small></span>
        </label>
      </div>
      <p class="muted settings-footnote" id="articleControlsStatus" aria-live="polite">Standard controls selected.</p>
    </section>
  </div>
</div>

`;
replaceOnce('<div class="modal-backdrop" id="summaryModal"',settingsModal+'<div class="modal-backdrop" id="summaryModal"','settings modal anchor');

replaceOnce('  const THEME_KEY = "artikelwerk_theme";','  const THEME_KEY = "artikelwerk_theme";\n  const ARTICLE_CONTROLS_KEY = "artikelwerk_article_controls";','article controls storage key');
replaceOnce('return [DOM.$("#wordDetailModal"),DOM.$("#summaryModal")].find(modal=>modal?.classList.contains("show"))||null;','return [DOM.$("#settingsModal"),DOM.$("#wordDetailModal"),DOM.$("#summaryModal")].find(modal=>modal?.classList.contains("show"))||null;','active modal list');

const settingsManager=String.raw`
  const SettingsManager = {
    layouts:new Set(["standard","bottom-bar","stacked"]),
    labels:{standard:"Standard", "bottom-bar":"Bottom Bar", stacked:"Stacked"},
    normalize(value){ return this.layouts.has(value)?value:"standard"; },
    current(){
      try{ return this.normalize(localStorage.getItem(ARTICLE_CONTROLS_KEY)); }
      catch{ return "standard"; }
    },
    sync(layout=this.current()){
      const value=this.normalize(layout);
      DOM.$$("input[name=\"articleControlsLayout\"]").forEach(input=>{ input.checked=input.value===value; });
      const status=DOM.$("#articleControlsStatus");
      if(status) status.textContent=this.labels[value]+" controls selected. Changes apply immediately and stay on this device.";
      return value;
    },
    apply(layout,{persist=true,announce=true}={}){
      const value=this.normalize(layout);
      const screen=DOM.$("#practiceScreen");
      if(screen) screen.dataset.articleControls=value;
      document.documentElement.dataset.articleControls=value;
      this.sync(value);
      if(persist){
        try{ localStorage.setItem(ARTICLE_CONTROLS_KEY,value); }catch{}
      }
      if(PracticeScreen.isOpen()){
        requestAnimationFrame(()=>{
          const content=DOM.$("#quizContent");
          if(content) content.scrollTop=0;
          QuizView.fitNounPrompt();
        });
      }
      if(announce) AccessibilityManager.announce(this.labels[value]+" article controls enabled.");
      return value;
    },
    init(){ this.apply(this.current(),{persist:false,announce:false}); },
    open(){
      this.sync();
      AccessibilityManager.openModal(DOM.$("#settingsModal"),DOM.$("#settingsTitle"));
    },
    close(){ AccessibilityManager.closeModal(DOM.$("#settingsModal")); }
  };

`;
replaceOnce('  const ThemeManager = {',settingsManager+'  const ThemeManager = {','settings manager anchor');

replaceOnce('      DOM.$("#resetBtn").addEventListener("click",()=>this.openDataControls());\n      DOM.$("#themeBtn").addEventListener("click",()=>ThemeManager.toggle());','      DOM.$("#resetBtn").addEventListener("click",()=>this.openDataControls());\n      DOM.$("#settingsBtn").addEventListener("click",()=>SettingsManager.open());\n      DOM.$("#settingsCloseBtn").addEventListener("click",()=>SettingsManager.close());\n      DOM.$("#settingsModal").addEventListener("click",event=>{ if(event.target===DOM.$("#settingsModal")) SettingsManager.close(); });\n      DOM.$$("input[name=\\"articleControlsLayout\\"]").forEach(input=>input.addEventListener("change",()=>{ if(input.checked) SettingsManager.apply(input.value); }));\n      DOM.$("#themeBtn").addEventListener("click",()=>ThemeManager.toggle());','settings event bindings');

replaceOnce('      ThemeManager.init();\n      VocabularyTrackModel.init();','      ThemeManager.init();\n      SettingsManager.init();\n      VocabularyTrackModel.init();','settings initialization');
replaceOnce('  const APP_VERSION = "1.2.0";','  const APP_VERSION = "1.3.0";','app version');

await writeFile(path,source,'utf8');
console.log('Applied mobile article-control settings to index.html.');
