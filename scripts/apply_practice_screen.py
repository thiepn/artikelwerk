#!/usr/bin/env python3
"""Apply Artikelwerk's dedicated no-scroll practice-screen release patch."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 1:
        return text.replace(old, new, 1)
    if count == 0 and label == "practice keyboard scope":
        listener = '      document.addEventListener("keydown",e=>{'
        listener_position = text.find(listener)
        input_marker = '        if(e.target.matches('
        input_position = text.find(input_marker, listener_position)
        active_marker = '        if(!DOM.$("#practiceView")?.classList.contains("active")) return;'
        if listener_position >= 0 and input_position >= 0 and active_marker in text:
            text = text[:input_position] + '        if(PracticeScreen.handleKeydown(e)) return;\n' + text[input_position:]
            return text.replace(active_marker, '        if(!PracticeScreen.isOpen()) return;', 1)
    raise ValueError(f"{label}: expected exactly one match, found {count}")


PRACTICE_CSS = r'''

  /* V1.1 dedicated practice screen: fixed viewport, stable feedback, zero page movement. */
  body.practice-open{overflow:hidden;overscroll-behavior:none}
  .practice-launch-panel{display:flex;align-items:center;justify-content:space-between;gap:22px;padding:20px 22px;margin-bottom:14px}
  .practice-launch-copy{min-width:0}
  .practice-launch-eyebrow{display:block;margin-bottom:4px;color:var(--accent);font-size:.72rem;font-weight:900;letter-spacing:.09em;text-transform:uppercase}
  .practice-launch-panel h2{margin:0 0 4px;font-size:1.18rem;letter-spacing:-.02em}
  .practice-launch-panel p{margin:0;color:var(--muted);font-size:.86rem}
  .practice-launch-btn{flex:0 0 auto;min-width:190px}

  .practice-screen[hidden]{display:none!important}
  .practice-screen{position:fixed;inset:0;z-index:90;width:100vw;height:100dvh;background:var(--bg);overflow:hidden;overscroll-behavior:none;padding-top:env(safe-area-inset-top);padding-right:env(safe-area-inset-right);padding-bottom:env(safe-area-inset-bottom);padding-left:env(safe-area-inset-left)}
  .practice-screen-shell{width:min(100%,1120px);height:100%;margin:0 auto;padding:10px 14px 12px;display:grid;grid-template-rows:auto minmax(0,1fr);gap:8px}
  .practice-screen-header{min-height:52px;display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:12px;padding:4px 2px}
  .practice-close-btn,.practice-translation-btn{min-height:44px;border:1px solid var(--border);border-radius:11px;background:var(--surface);color:var(--text);font:inherit;font-weight:850;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;gap:7px;padding:8px 12px}
  .practice-close-btn:hover,.practice-translation-btn:hover{background:var(--surface-2);border-color:var(--border-strong)}
  .practice-translation-btn[aria-expanded="true"]{border-color:var(--accent);background:var(--accent-soft);color:var(--accent-dark)}
  .practice-translation-btn>span:first-child{font-size:.72rem;letter-spacing:.06em}
  .practice-screen-heading{min-width:0;text-align:center;display:flex;flex-direction:column;line-height:1.15}
  .practice-screen-heading strong{font-size:.95rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .practice-screen-heading span{margin-top:4px;color:var(--muted);font-size:.74rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .practice-screen-body{min-height:0;display:grid;grid-template-rows:auto minmax(0,1fr);gap:6px}
  .practice-screen .session-bar{min-height:24px;margin:0;padding:0 4px;align-items:center}
  .practice-screen .session-metrics{gap:16px}
  .practice-screen .quiz-card{box-sizing:border-box;width:100%;max-width:100%;min-width:0;height:100%;min-height:0;margin:0;padding:clamp(14px,2.3vw,28px);border-radius:16px;overflow:hidden;display:block}
  .practice-screen #quizContent{box-sizing:border-box;width:100%;max-width:100%;min-width:0;height:100%;min-height:0;overflow:hidden;display:grid;grid-template-rows:auto minmax(88px,1fr) auto}
  .practice-screen #quizContent>div:last-child{min-height:0;display:flex;flex-direction:column;justify-content:flex-end}
  .practice-screen .quiz-top{min-height:25px}
  .practice-screen .question-wrap{box-sizing:border-box;width:100%;max-width:100%;min-width:0;min-height:0;overflow:hidden;padding:clamp(12px,3vh,30px) 0 clamp(8px,2vh,18px);display:flex;flex-direction:column;justify-content:center}
  .practice-screen .noun{font-size:clamp(2.2rem,7vw,5rem)}
  .practice-screen .quiz-card.format-context .noun{font-size:clamp(1.25rem,3.3vw,2.45rem);line-height:1.28}
  .translation-hint{align-self:center;width:min(100%,calc(100vw - 36px),700px);max-width:calc(100vw - 36px);min-width:0;box-sizing:border-box;overflow:hidden;min-height:38px;margin:7px auto 0;padding:7px 12px;border:1px solid transparent;border-radius:10px;color:var(--muted);font-size:.86rem;line-height:1.25;text-align:center;visibility:hidden;opacity:0;display:flex;align-items:center;justify-content:center;gap:8px;transition:opacity .12s ease}
  .translation-hint.show{visibility:visible;opacity:1;border-color:var(--border);background:var(--surface-2)}
  .translation-hint .translation-label{flex:0 0 auto;color:var(--accent);font-size:.68rem;font-weight:900;letter-spacing:.08em;text-transform:uppercase}
  .translation-hint #translationText{min-width:0;color:var(--text);font-weight:800;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .translation-hint.is-fallback #translationLabel::after{content:""}
  .practice-screen .confidence-capture{margin-bottom:9px}
  .practice-screen .unknown-row{margin-top:8px}
  .practice-screen .feedback{max-width:none;margin:8px 0 0;padding-top:8px}
  .practice-screen .feedback-title{margin:0;font-size:1rem;line-height:1.2}
  .practice-screen .feedback-word{margin-top:2px;font-size:1.12rem;line-height:1.2}
  .practice-screen #feedbackRule,.practice-screen #feedbackExample{margin:4px 0 0;font-size:.82rem;line-height:1.32;display:-webkit-box;-webkit-box-orient:vertical;overflow:hidden}
  .practice-screen #feedbackRule{-webkit-line-clamp:2}
  .practice-screen #feedbackExample{-webkit-line-clamp:2}
  .practice-screen .feedback-more{margin-top:6px;border-top:1px solid var(--border)}
  .practice-screen .feedback-more summary{min-height:30px;display:flex;align-items:center;cursor:pointer;color:var(--muted);font-size:.74rem;font-weight:800;list-style:none}
  .practice-screen .feedback-more summary::-webkit-details-marker{display:none}
  .practice-screen .feedback-more summary::after{content:"+";margin-left:6px;color:var(--accent)}
  .practice-screen .feedback-more[open] summary::after{content:"−"}
  .practice-screen .feedback-more-body{max-height:min(20vh,150px);overflow:auto;overscroll-behavior:contain;padding:4px 4px 2px;font-size:.76rem;line-height:1.35}
  .practice-screen .feedback-more-body p{margin:4px 0}
  .practice-screen .next-row{margin-top:7px;padding-top:7px;gap:10px}
  .practice-screen .quiz-card.has-feedback .confidence-capture,.practice-screen .quiz-card.has-feedback .unknown-row{display:none}
  .practice-screen .quiz-card.has-feedback .answer-btn{min-height:44px;padding-block:8px}
  .practice-screen .quiz-card.has-feedback .production-entry{margin-top:0}
  .practice-screen .empty-state{height:100%;place-content:center}

  @media(max-width:700px){
    .practice-launch-panel{align-items:stretch;flex-direction:column;padding:16px}
    .practice-launch-btn{width:100%;min-width:0}
    .practice-screen-shell{padding:6px 8px 8px;gap:4px}
    .practice-screen-header{min-height:48px;gap:7px;padding:2px 0}
    .practice-close-btn,.practice-translation-btn{min-width:44px;padding:6px 9px}
    .practice-close-btn span,.practice-translation-label{display:none}
    .practice-screen-heading strong{font-size:.88rem}
    .practice-screen-heading span{font-size:.68rem}
    .practice-screen .session-bar{padding-inline:2px;align-items:center;flex-direction:row;gap:5px;font-size:.74rem}
    .practice-screen .session-metrics{width:100%;justify-content:space-between;gap:5px}
    .practice-screen .quiz-card{padding:11px 10px;border-radius:13px}
    .practice-screen #quizContent{grid-template-rows:auto minmax(82px,1fr) auto}
    .practice-screen .quiz-top{align-items:center}
    .practice-screen .question-wrap{padding:8px 0 7px}
    .practice-screen .noun{font-size:clamp(1.95rem,11vw,3.35rem);line-height:1.02}
    .practice-screen .quiz-card.format-context .noun{font-size:clamp(1.08rem,5.1vw,1.65rem);line-height:1.3}
    .translation-hint{min-height:34px;margin-top:5px;padding:6px 8px;font-size:.79rem}
    .practice-screen .confidence-capture{gap:5px;margin-bottom:7px;flex-wrap:nowrap}
    .practice-screen .confidence-capture>span{display:none}
    .practice-screen .confidence-btn{min-height:38px;padding:5px 8px;font-size:.76rem;flex:1}
    .practice-screen .answers{gap:7px}
    .practice-screen .answer-btn{min-height:52px;padding:12px 5px;font-size:.94rem}
    .practice-screen .unknown-row{margin-top:6px}
    .practice-screen .unknown-word-btn{min-height:38px;padding-block:6px;font-size:.68rem}
    .practice-screen .production-entry{flex-direction:row;gap:7px}
    .practice-screen .production-entry input{min-height:44px;padding:10px 11px}
    .practice-screen .production-entry .primary-btn{width:auto;min-width:78px;padding-inline:12px}
    .practice-screen .production-status{margin-top:4px;font-size:.72rem;min-height:1em}
    .practice-screen .feedback{margin-top:6px;padding-top:6px}
    .practice-screen .feedback-title{font-size:.9rem}
    .practice-screen .feedback-word{font-size:1rem}
    .practice-screen #feedbackRule,.practice-screen #feedbackExample{font-size:.76rem;line-height:1.25}
    .practice-screen #feedbackRule{-webkit-line-clamp:2}
    .practice-screen #feedbackExample{-webkit-line-clamp:1}
    .practice-screen .next-row{align-items:center;flex-direction:row;margin-top:5px;padding-top:5px}
    .practice-screen .next-row .shortcut{display:none}
    .practice-screen .next-row .primary-btn{width:auto;min-width:96px;margin-left:auto}
    .practice-screen .vocab-learning-actions{gap:7px;margin-top:7px;flex-wrap:nowrap}
    .practice-screen .vocab-learning-actions button{min-height:40px;padding:7px 9px;font-size:.74rem;flex:1}
  }

  @media(max-height:720px){
    .practice-screen .quiz-top{min-height:20px}
    .practice-screen .question-wrap{padding:5px 0}
    .practice-screen .confidence-capture{display:none}
    .practice-screen .translation-hint{min-height:30px;margin-top:3px;padding-block:4px}
    .practice-screen #feedbackRule{-webkit-line-clamp:1}
    .practice-screen #feedbackExample{-webkit-line-clamp:1}
    .practice-screen .feedback-more{display:none}
  }

  @media(max-height:610px){
    .practice-screen .quiz-top{display:none}
    .practice-screen .session-bar{font-size:.68rem}
    .practice-screen .noun{font-size:clamp(1.75rem,9vh,2.8rem)}
    .practice-screen .translation-hint{font-size:.72rem}
    .practice-screen #feedbackRule{display:none}
  }
'''


TRANSLATION_MODEL = r'''

  const TranslationModel = {
    data:Object.freeze(window.ARTIKELWERK_TRANSLATIONS||{}),
    fallbackIds:new Set(window.ARTIKELWERK_TRANSLATION_FALLBACKS||[]),
    text(word,sense=null){
      if(!word) return "Meaning unavailable";
      const active=sense||MeaningGenderModel.activeSense(word);
      if(MeaningGenderModel.isMeaningDependent(word) && active?.gloss) return active.gloss;
      const stored=this.data[word.id];
      if(typeof stored==="string" && stored.trim()) return stored.trim();
      return String(word.group||"meaning unavailable").replace(/-/g," ");
    },
    isFallback(word,sense=null){
      if(!word || (MeaningGenderModel.isMeaningDependent(word) && (sense||MeaningGenderModel.activeSense(word))?.gloss)) return false;
      return this.fallbackIds.has(word.id) || !this.data[word.id];
    },
    label(word,sense=null){ return this.isFallback(word,sense)?"English cue":"English"; }
  };
'''


PRACTICE_SCREEN_MODEL = r'''

  const PracticeScreen = {
    returnFocus:null,
    element(){ return DOM.$("#practiceScreen"); },
    isOpen(){ return Boolean(this.element() && !this.element().hidden); },
    isTouchLike(){ return Boolean(navigator.maxTouchPoints>0 || window.matchMedia?.("(pointer: coarse)").matches); },
    open(){
      const screen=this.element();
      if(!screen) return;
      this.returnFocus=(typeof HTMLElement!=="undefined" && document.activeElement instanceof HTMLElement)?document.activeElement:DOM.$("#openPracticeBtn");
      screen.hidden=false;
      screen.setAttribute("aria-hidden","false");
      document.body.classList.add("practice-open");
      this.updateSubtitle();
      requestAnimationFrame(()=>DOM.$("#nounPrompt")?.focus({preventScroll:true}));
    },
    close({restoreFocus=true}={}){
      const screen=this.element();
      if(!screen || screen.hidden) return;
      screen.hidden=true;
      screen.setAttribute("aria-hidden","true");
      document.body.classList.remove("practice-open");
      if(restoreFocus){
        const target=this.returnFocus?.isConnected?this.returnFocus:DOM.$("#openPracticeBtn");
        requestAnimationFrame(()=>target?.focus?.({preventScroll:true}));
      }
      this.returnFocus=null;
    },
    updateSubtitle(){
      const subtitle=DOM.$("#practiceScreenSubtitle");
      if(!subtitle) return;
      const mode=Runtime.session?.mode||DOM.$("#modeSelect")?.value||"practice";
      const format=QuestionFormatModel.sessionFormat(Runtime.session);
      subtitle.textContent=mode==="unknownWords"
        ? "Review the meaning, then mark the word known or keep learning"
        : format==="production"
          ? "Type the full article and noun"
          : "Tap an article to answer";
    },
    handleKeydown(event){
      if(!this.isOpen()) return false;
      if(event.key==="Escape"){
        event.preventDefault();
        this.close();
        return true;
      }
      if(event.key!=="Tab") return false;
      const items=[...this.element().querySelectorAll('button:not([disabled]),input:not([disabled]),select:not([disabled]),[tabindex]:not([tabindex="-1"])')]
        .filter(item=>!item.hidden && item.offsetParent!==null);
      if(!items.length){ event.preventDefault(); return true; }
      const first=items[0],last=items[items.length-1];
      if(event.shiftKey && document.activeElement===first){ event.preventDefault(); last.focus({preventScroll:true}); return true; }
      if(!event.shiftKey && document.activeElement===last){ event.preventDefault(); first.focus({preventScroll:true}); return true; }
      return false;
    }
  };
'''


def patch(source: str) -> str:
    if "V1.1 dedicated practice screen" in source:
        return source

    source = replace_once(source, 'const APP_VERSION = "1.0.0";', 'const APP_VERSION = "1.1.0";', "version bump")
    source = replace_once(source, "\n</style>", PRACTICE_CSS + "\n</style>", "practice CSS")
    source = replace_once(source, "\n<script>\n(() => {", "\n<script src=\"translations.js\"></script>\n<script>\n(() => {", "translation data script")

    source = replace_once(
        source,
        '    <section class="view active" id="practiceView" role="tabpanel" aria-labelledby="tabPractice" aria-hidden="false">\n      <div class="panel controls">',
        '''    <section class="view active" id="practiceView" role="tabpanel" aria-labelledby="tabPractice" aria-hidden="false">
      <div class="panel practice-launch-panel">
        <div class="practice-launch-copy">
          <span class="practice-launch-eyebrow">Dedicated practice</span>
          <h2>Practice without scrolling</h2>
          <p>Questions, English meaning, feedback, and the next action remain in one fixed screen.</p>
        </div>
        <button type="button" class="primary-btn practice-launch-btn" id="openPracticeBtn">Open practice screen</button>
      </div>

      <div class="panel controls" id="practiceSetup">''',
        "practice launch panel",
    )
    source = replace_once(source, '<button class="primary-btn" id="newSessionBtn">New session</button>', '<button class="primary-btn" id="newSessionBtn">Start new session</button>', "new session label")

    source = replace_once(
        source,
        '      <div class="session-bar">',
        '''      <section class="practice-screen" id="practiceScreen" role="dialog" aria-modal="true" aria-labelledby="practiceScreenTitle" aria-hidden="true" hidden>
        <div class="practice-screen-shell">
          <header class="practice-screen-header">
            <button type="button" class="practice-close-btn" id="closePracticeBtn" aria-label="Leave practice screen">← <span>Setup</span></button>
            <div class="practice-screen-heading">
              <strong id="practiceScreenTitle">Artikel practice</strong>
              <span id="practiceScreenSubtitle">Tap an article to answer</span>
            </div>
            <button type="button" class="practice-translation-btn" id="showTranslationBtn" aria-controls="translationHint" aria-expanded="false"><span>EN</span><span class="practice-translation-label">Meaning</span></button>
          </header>
          <div class="practice-screen-body">
      <div class="session-bar">''',
        "practice screen opening",
    )

    source = replace_once(
        source,
        '            <h2 class="noun" id="nounPrompt" tabindex="-1" lang="de"><span class="blank">___</span> Aufwand</h2>\n          </div>',
        '''            <h2 class="noun" id="nounPrompt" tabindex="-1" lang="de"><span class="blank">___</span> Aufwand</h2>
            <div class="translation-hint" id="translationHint" aria-live="polite" aria-hidden="true">
              <span class="translation-label" id="translationLabel">English</span>
              <span id="translationText"></span>
            </div>
          </div>''',
        "translation hint",
    )

    source = replace_once(
        source,
        '''            <div class="feedback" id="feedback">
              <div class="feedback-title" id="feedbackTitle"></div>
              <div class="feedback-word" id="feedbackWord" lang="de"></div>
              <p id="feedbackRule"></p>
              <p class="example" id="feedbackExample" lang="de"></p>
              <p id="contrastFeedback" class="contrast-feedback" hidden></p>
              <p id="wordFamilyFeedback" class="contrast-feedback" hidden></p>
              <p id="collocationFeedback" class="contrast-feedback" hidden></p>
              <p id="inflectionFeedback" class="contrast-feedback" hidden></p>
              <p id="variantGenderFeedback" class="contrast-feedback" hidden></p>
              <p class="muted" id="feedbackTiming"></p>
              <p class="muted" id="feedbackSchedule"></p>
              <p id="leechFeedback" class="leech-feedback" hidden></p>
              <p id="forgottenFeedback" class="forgotten-feedback" hidden></p>
              <p id="correctionPrompt" class="correction-prompt" hidden></p>
              <div class="next-row">''',
        '''            <div class="feedback" id="feedback">
              <div class="feedback-core">
                <div class="feedback-title" id="feedbackTitle"></div>
                <div class="feedback-word" id="feedbackWord" lang="de"></div>
                <p id="feedbackRule"></p>
                <p class="example" id="feedbackExample" lang="de"></p>
              </div>
              <details class="feedback-more" id="feedbackMore">
                <summary>More details</summary>
                <div class="feedback-more-body">
                  <p id="contrastFeedback" class="contrast-feedback" hidden></p>
                  <p id="wordFamilyFeedback" class="contrast-feedback" hidden></p>
                  <p id="collocationFeedback" class="contrast-feedback" hidden></p>
                  <p id="inflectionFeedback" class="contrast-feedback" hidden></p>
                  <p id="variantGenderFeedback" class="contrast-feedback" hidden></p>
                  <p class="muted" id="feedbackTiming"></p>
                  <p class="muted" id="feedbackSchedule"></p>
                  <p id="leechFeedback" class="leech-feedback" hidden></p>
                  <p id="forgottenFeedback" class="forgotten-feedback" hidden></p>
                </div>
              </details>
              <p id="correctionPrompt" class="correction-prompt" hidden></p>
              <div class="next-row">''',
        "compact feedback structure",
    )

    source = replace_once(
        source,
        '''        </div>
      </div>
    </section>

    <section class="view" id="statsView"''',
        '''        </div>
      </div>
          </div>
        </div>
      </section>
    </section>

    <section class="view" id="statsView"''',
        "practice screen closing",
    )

    source = replace_once(source, "\n  function createVocabularyEntry", TRANSLATION_MODEL + "\n\n  function createVocabularyEntry", "translation model")

    source = replace_once(
        source,
        "\n  const QuizView = {\n    showEmpty(){",
        '''
  const QuizView = {
    hideTranslation(){
      const hint=DOM.$("#translationHint");
      const button=DOM.$("#showTranslationBtn");
      if(!hint || !button) return;
      hint.classList.remove("show","is-fallback");
      hint.setAttribute("aria-hidden","true");
      DOM.$("#translationText").textContent="";
      DOM.$("#translationLabel").textContent="English";
      button.setAttribute("aria-expanded","false");
    },
    revealTranslation({announce=false}={}){
      if(!Runtime.current) return;
      const text=TranslationModel.text(Runtime.current,Runtime.currentSense);
      const fallback=TranslationModel.isFallback(Runtime.current,Runtime.currentSense);
      const label=TranslationModel.label(Runtime.current,Runtime.currentSense);
      const hint=DOM.$("#translationHint");
      DOM.$("#translationText").textContent=text;
      DOM.$("#translationLabel").textContent=label;
      hint.classList.toggle("is-fallback",fallback);
      hint.classList.add("show");
      hint.setAttribute("aria-hidden","false");
      DOM.$("#showTranslationBtn").setAttribute("aria-expanded","true");
      if(announce) AccessibilityManager.announce(`${label}: ${text}`);
    },
    showEmpty(){''',
        "quiz translation methods",
    )

    source = replace_once(
        source,
        '''      const card=DOM.$("#quizCard");
      card.classList.toggle("unknown-learning",mode==="unknownWords");''',
        '''      const card=DOM.$("#quizCard");
      card.classList.remove("has-feedback");
      DOM.$("#feedbackMore").open=false;
      this.hideTranslation();
      card.classList.toggle("unknown-learning",mode==="unknownWords");''',
        "question state reset",
    )

    source = replace_once(
        source,
        '      if(format==="production" && mode!=="unknownWords") requestAnimationFrame(()=>productionInput.focus());',
        '      if(format==="production" && mode!=="unknownWords" && !PracticeScreen.isTouchLike()) requestAnimationFrame(()=>productionInput.focus({preventScroll:true}));',
        "mobile autofocus suppression",
    )

    source = replace_once(
        source,
        '''        DOM.$("#feedbackExample").innerHTML=ExampleContextModel.feedbackHtml(word);
        DOM.$("#nextBtn").disabled=true;
      }
      this.updateSessionBar();''',
        '''        DOM.$("#feedbackExample").innerHTML=ExampleContextModel.feedbackHtml(word);
        DOM.$("#nextBtn").disabled=true;
        card.classList.add("has-feedback");
        this.revealTranslation();
      }
      PracticeScreen.updateSubtitle();
      this.updateSessionBar();''',
        "unknown-word learning translation",
    )

    source = replace_once(
        source,
        '''      DOM.$("#feedback").classList.add("show");
      DOM.$("#nextBtn").disabled=false;
      this.updateSessionBar();
      const answer=MeaningGenderModel.displayNoun(Runtime.current,Runtime.currentSense);''',
        '''      DOM.$("#feedback").classList.add("show");
      DOM.$("#nextBtn").disabled=false;
      DOM.$("#quizCard").classList.add("has-feedback");
      this.revealTranslation();
      this.updateSessionBar();
      const answer=MeaningGenderModel.displayNoun(Runtime.current,Runtime.currentSense);''',
        "feedback translation reveal",
    )

    source = replace_once(
        source,
        '''      DOM.$("#feedback").classList.add("show");
      DOM.$("#feedbackTitle").textContent="Marked as unfamiliar";''',
        '''      DOM.$("#feedback").classList.add("show");
      DOM.$("#quizCard").classList.add("has-feedback");
      QuizView.revealTranslation();
      DOM.$("#feedbackTitle").textContent="Marked as unfamiliar";''',
        "unknown marker translation reveal",
    )

    source = replace_once(source, "\n  const AccessibilityManager = {", PRACTICE_SCREEN_MODEL + "\n\n  const AccessibilityManager = {", "practice screen controller")

    source = replace_once(
        source,
        '''      const panel=DOM.$(`#${view}View`);
      if(!panel) return;''',
        '''      const panel=DOM.$(`#${view}View`);
      if(!panel) return;
      if(view!=="practice") PracticeScreen.close({restoreFocus:false});''',
        "close practice on navigation",
    )

    source = replace_once(
        source,
        '''      DOM.$("#nextBtn").addEventListener("click",()=>SessionEngine.nextQuestion());
      DOM.$("#newSessionBtn").addEventListener("click",()=>SessionEngine.start());
      DOM.$("#startReviewBtn").addEventListener("click",()=>SessionEngine.startTodayReview());''',
        '''      DOM.$("#nextBtn").addEventListener("click",()=>SessionEngine.nextQuestion());
      DOM.$("#openPracticeBtn").addEventListener("click",()=>PracticeScreen.open());
      DOM.$("#closePracticeBtn").addEventListener("click",()=>PracticeScreen.close());
      DOM.$("#showTranslationBtn").addEventListener("click",()=>QuizView.revealTranslation({announce:true}));
      DOM.$("#newSessionBtn").addEventListener("click",()=>{ SessionEngine.start(); PracticeScreen.open(); });
      DOM.$("#startReviewBtn").addEventListener("click",()=>{ SessionEngine.startTodayReview(); PracticeScreen.open(); });''',
        "practice screen events",
    )

    source = replace_once(
        source,
        '      DOM.$("#emptyPracticeBtn").addEventListener("click",()=>SessionEngine.start({mode:"practice"}));',
        '      DOM.$("#emptyPracticeBtn").addEventListener("click",()=>{ SessionEngine.start({mode:"practice"}); PracticeScreen.open(); });',
        "empty state practice open",
    )

    source = replace_once(
        source,
        '''        if(ids.length) SessionEngine.start({mode:"adaptive",reviewIds:ids});''',
        '''        if(ids.length){ SessionEngine.start({mode:"adaptive",reviewIds:ids}); PracticeScreen.open(); }''',
        "retry opens practice",
    )

    source = replace_once(
        source,
        '''        if(e.target.matches("input,select,textarea,[contenteditable=\"true\"]")) return;
        if(e.altKey || e.ctrlKey || e.metaKey) return;
        if(!DOM.$("#practiceView")?.classList.contains("active")) return;''',
        '''        if(PracticeScreen.handleKeydown(e)) return;
        if(e.target.matches("input,select,textarea,[contenteditable=\"true\"]")) return;
        if(e.altKey || e.ctrlKey || e.metaKey) return;
        if(!PracticeScreen.isOpen()) return;''',
        "practice keyboard scope",
    )

    source = replace_once(
        source,
        '''        if(e.key==="0") CoreTrainingModel.markUnknown();
        const production=QuestionFormatModel.isProduction()''',
        '''        if(e.key==="0") CoreTrainingModel.markUnknown();
        if(e.key==="t" || e.key==="T") QuizView.revealTranslation({announce:true});
        const production=QuestionFormatModel.isProduction()''',
        "translation keyboard shortcut",
    )

    source = replace_once(
        source,
        '''      const meaningGlosses=(word.meanings||[]).filter(s=>s.gloss).map(s=>`${s.articles.join("/")} — ${s.gloss}`);
      const status=ws.vocabularyStatus||"normal";''',
        '''      const meaningGlosses=(word.meanings||[]).filter(s=>s.gloss).map(s=>`${s.articles.join("/")} — ${s.gloss}`);
      const englishGloss=TranslationModel.text(word,MeaningGenderModel.activeSense(word));
      const status=ws.vocabularyStatus||"normal";''',
        "library English gloss",
    )

    source = replace_once(
        source,
        '''            <div class="detail-field"><strong>Article</strong><span>${DOM.escapeHtml(articleLabel)} ${DOM.escapeHtml(word.noun)}</span></div>
            <div class="detail-field"><strong>Gender status</strong>''',
        '''            <div class="detail-field"><strong>Article</strong><span>${DOM.escapeHtml(articleLabel)} ${DOM.escapeHtml(word.noun)}</span></div>
            <div class="detail-field"><strong>English</strong><span>${DOM.escapeHtml(englishGloss)}</span></div>
            <div class="detail-field"><strong>Gender status</strong>''',
        "library English field",
    )

    return source


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.read_text(encoding="utf-8")
    patched = patch(source)
    args.output.write_text(patched, encoding="utf-8")


if __name__ == "__main__":
    main()
