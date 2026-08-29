#!/usr/bin/env python3
from pathlib import Path

path=Path('index.html')
s=path.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    count=s.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 anchor, found {count}')
    s=s.replace(old,new,1)

# A newly queued miss must become unresolved again, even if an earlier retry of the same
# word/sense had already been recovered in this session.
replace_once(
'''      const key=senseId?`${wordId}::${senseId}`:wordId;\n      const wasQueued=session.shortRetries.has(key);''',
'''      const key=senseId?`${wordId}::${senseId}`:wordId;\n      session.resolvedRetries?.delete(key);\n      const wasQueued=session.shortRetries.has(key);''',
'queueShortRetry resolution reset')

# Reset the terminal action whenever a new question is rendered.
replace_once(
'''      DOM.$("#nextBtn").disabled=true;\n      DOM.$$(".answer-btn").forEach(b=>b.className="answer-btn");''',
'''      DOM.$("#nextBtn").disabled=true;\n      DOM.$("#nextBtn").textContent="Next";\n      DOM.$("#nextBtn").setAttribute("aria-label","Next question");\n      DOM.$$(".answer-btn").forEach(b=>b.className="answer-btn");''',
'question Next reset')

# Unknown-word handling can also complete a finite session.
replace_once(
'''      QuizView.updateSessionBar();\n      ReviewQueueView.render();\n      AccessibilityManager.announce(`${MeaningGenderModel.displayNoun(Runtime.current,Runtime.currentSense)} marked unfamiliar. This does not count as an article error.`);''',
'''      QuizView.updateSessionBar();\n      SessionEngine.syncNextAction();\n      ReviewQueueView.render();\n      AccessibilityManager.announce(`${MeaningGenderModel.displayNoun(Runtime.current,Runtime.currentSense)} marked unfamiliar. This does not count as an article error.`);''',
'markUnknown terminal action')

# Track recovered delayed retries separately from the historical mistake map. The mistake
# remains visible in the summary, while final checks only contain unresolved misses.
s=s.replace('mistakes:new Map(),shortRetries:new Map(),','mistakes:new Map(),shortRetries:new Map(),resolvedRetries:new Set(),')
if s.count('resolvedRetries:new Set()')!=2:
    raise SystemExit(f'session resolvedRetries: expected 2 initializers, found {s.count("resolvedRetries:new Set()")}' )

# Add terminal/final-check helpers and make the final queue exclude successfully recovered retries.
replace_once(
'''    nextFinalCheckOrEnd(){\n      const session=Runtime.session;\n      if(!session || session.mode==="timed") return this.end();\n      if(!session.finalCheckQueue){\n        const senseKeys=[...(session.senseMistakes||new Map()).keys()];\n        const senseWordIds=new Set(senseKeys.map(key=>key.split("::")[0]));\n        const ordinary=[...session.mistakes.keys()].filter(id=>!senseWordIds.has(id)).map(id=>({wordId:id,senseId:null}));\n        const sensed=senseKeys.map(key=>{ const [wordId,senseId]=key.split("::"); return {wordId,senseId}; });\n        session.finalCheckQueue=[...ordinary,...sensed];\n        session.finalCheckCursor=0;\n      }''',
'''    finalCheckItems(session=Runtime.session){\n      if(!session) return [];\n      const resolved=session.resolvedRetries||new Set();\n      const senseKeys=[...(session.senseMistakes||new Map()).keys()];\n      const senseWordIds=new Set(senseKeys.map(key=>key.split("::")[0]));\n      const ordinary=[...session.mistakes.keys()]\n        .filter(id=>!senseWordIds.has(id) && !resolved.has(id))\n        .map(id=>({wordId:id,senseId:null}));\n      const sensed=senseKeys\n        .filter(key=>!resolved.has(key))\n        .map(key=>{ const [wordId,senseId]=key.split("::"); return {wordId,senseId}; });\n      return [...ordinary,...sensed];\n    },\n    hasPendingFinalChecks(session=Runtime.session){\n      if(!session) return false;\n      if(session.finalCheckQueue) return session.finalCheckCursor<session.finalCheckQueue.length;\n      return this.finalCheckItems(session).length>0;\n    },\n    isFinishReady(){\n      const session=Runtime.session;\n      if(!session || !Runtime.answered || Runtime.correctionPending || session.mode==="timed") return false;\n      if(Runtime.questionKind==="finalCheck") return Boolean(session.finalCheckQueue) && session.finalCheckCursor>=session.finalCheckQueue.length;\n      if(!Number.isFinite(session.target) || session.completed<session.target) return false;\n      if(session.shortRetries.size) return false;\n      return !this.hasPendingFinalChecks(session);\n    },\n    syncNextAction(){\n      const button=DOM.$("#nextBtn");\n      if(!button) return;\n      const finish=this.isFinishReady();\n      button.textContent=finish?"Finish":"Next";\n      button.setAttribute("aria-label",finish?"Finish session":"Next question");\n    },\n    advance(){\n      if(this.isFinishReady()) return this.end();\n      return this.nextQuestion();\n    },\n    nextFinalCheckOrEnd(){\n      const session=Runtime.session;\n      if(!session || session.mode==="timed") return this.end();\n      if(!session.finalCheckQueue){\n        session.finalCheckQueue=this.finalCheckItems(session);\n        session.finalCheckCursor=0;\n      }''',
'final-check queue and terminal helpers')

# A correct delayed retry resolves the matching word/sense for this session. A failed retry
# remains unresolved even after the required unscored correction, so it still receives one
# final check.
replace_once(
'''      if(reinforcement){\n        Runtime.answered=true;\n        const bucket=kind==="finalCheck"?"final":"short";\n        Runtime.session.reinforcement[`${bucket}${expectedCorrect?"Correct":"Wrong"}`]++;\n        QuizView.renderFeedback(article,expectedCorrect,responseTimeMs,{reinforcement:true,kind});\n        if(!expectedCorrect){\n          Runtime.correctionPending={wordId:Runtime.current.id,kind};\n          Runtime.answered=false;\n          QuizView.requireCorrection();\n        }\n        return;\n      }''',
'''      if(reinforcement){\n        Runtime.answered=true;\n        const bucket=kind==="finalCheck"?"final":"short";\n        Runtime.session.reinforcement[`${bucket}${expectedCorrect?"Correct":"Wrong"}`]++;\n        if(kind==="shortRetry"){\n          const retryKey=MeaningGenderModel.isMeaningDependent(Runtime.current) && Runtime.currentSense\n            ? `${Runtime.current.id}::${Runtime.currentSense.id}`\n            : Runtime.current.id;\n          if(expectedCorrect) Runtime.session.resolvedRetries.add(retryKey);\n          else Runtime.session.resolvedRetries.delete(retryKey);\n        }\n        QuizView.renderFeedback(article,expectedCorrect,responseTimeMs,{reinforcement:true,kind});\n        if(!expectedCorrect){\n          Runtime.correctionPending={wordId:Runtime.current.id,kind};\n          Runtime.answered=false;\n          QuizView.requireCorrection();\n        }\n        this.syncNextAction();\n        return;\n      }''',
'reinforcement resolution')

# Correction completion must refresh Finish/Next semantics after Runtime.answered changes.
replace_once(
'''        if(corrected){\n          Runtime.correctionPending=null;\n          Runtime.answered=true;\n        }\n        return;''',
'''        if(corrected){\n          Runtime.correctionPending=null;\n          Runtime.answered=true;\n          this.syncNextAction();\n        }\n        return;''',
'correction terminal sync')

# Normal answers can end an all-correct finite session.
replace_once(
'''      if(!correct && Runtime.session.mode!=="timed"){\n        Runtime.correctionPending={wordId:Runtime.current.id,kind:"normal"};\n        Runtime.answered=false;\n        QuizView.requireCorrection();\n      }\n      ReviewQueueView.render();''',
'''      if(!correct && Runtime.session.mode!=="timed"){\n        Runtime.correctionPending={wordId:Runtime.current.id,kind:"normal"};\n        Runtime.answered=false;\n        QuizView.requireCorrection();\n      }\n      this.syncNextAction();\n      ReviewQueueView.render();''',
'normal terminal sync')

# The old end() opened a modal underneath the still-visible fullscreen Practice layer. Close
# Practice first so the summary is actually visible and its focus trap is the active surface.
replace_once(
'''      DOM.$("#retryMistakesBtn").dataset.ids = [...new Set(mistakeItems.map(x=>x.w.id))].join(",");\n      AccessibilityManager.openModal(DOM.$("#summaryModal"),DOM.$("#summaryTitle"));''',
'''      DOM.$("#retryMistakesBtn").dataset.ids = [...new Set(mistakeItems.map(x=>x.w.id))].join(",");\n      PracticeScreen.close();\n      AccessibilityManager.openModal(DOM.$("#summaryModal"),DOM.$("#summaryTitle"));''',
'end Practice before summary')

# Mouse and keyboard use the same terminal-aware action.
replace_once(
'''      DOM.$("#nextBtn").addEventListener("click",()=>SessionEngine.nextQuestion());''',
'''      DOM.$("#nextBtn").addEventListener("click",()=>SessionEngine.advance());''',
'Next click advance')
replace_once(
'''        if(e.key==="Enter" && Runtime.answered) SessionEngine.nextQuestion();''',
'''        if(e.key==="Enter" && Runtime.answered) SessionEngine.advance();''',
'Enter advance')

path.write_text(s,encoding='utf-8')
print('Applied session finish/repeat fix.')
