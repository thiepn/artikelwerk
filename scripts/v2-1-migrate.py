from pathlib import Path

ROOT = Path('.')
INDEX = ROOT / 'index.html'

def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Missing V2-1 anchor: {label}')
    return text.replace(old, new, 1)

html = INDEX.read_text(encoding='utf-8')
if '/* V2-1 — vocabulary track architecture */' in html:
    raise SystemExit('V2-1 already applied')

html = replace_once(html, 'const APP_VERSION = "1.1.0";', 'const APP_VERSION = "1.2.0";', 'app version')
html = replace_once(html, 'const VOCAB_SCHEMA_VERSION = 14;', 'const VOCAB_SCHEMA_VERSION = 15;', 'vocabulary schema version')
html = replace_once(html, 'const SCHEMA_VERSION = 9;', 'const SCHEMA_VERSION = 10;', 'state schema version')

old_sig = 'function createVocabularyEntry([id,noun,article,level,rule,example,group,coverageTier="full-depth",expansionPhase=null]){'
new_sig = 'function createVocabularyEntry([id,noun,article,level,rule,example,group,coverageTier="full-depth",expansionPhase=null,track="challenge"]){'
html = replace_once(html, old_sig, new_sig, 'vocabulary factory signature')
html = replace_once(html, '      lexicalSchemaVersion:VOCAB_SCHEMA_VERSION,\n      id,\n      noun,', '      lexicalSchemaVersion:VOCAB_SCHEMA_VERSION,\n      track:track==="bridge"?"bridge":"challenge",\n      id,\n      noun,', 'vocabulary track property')

track_model = r'''

  // V2-1: Challenge remains the default corpus. Bridge is automatically enabled as soon as
  // V2-2 adds entries whose final tuple field is "bridge".
  const VOCABULARY_TRACKS = Object.freeze({
    challenge:Object.freeze({
      id:"challenge",label:"Challenge",band:"C1–C2",description:"Advanced and difficult noun gender",availableLabel:"advanced C1/C2 nouns",
      difficulty:Object.freeze({all:"All advanced levels",1:"Level 1 — Advanced",2:"Level 2 — Difficult",3:"Level 3 — Very Difficult"})
    }),
    bridge:Object.freeze({
      id:"bridge",label:"Bridge",band:"B2–C1",description:"Intermediate to advanced-intermediate noun gender",availableLabel:"B2–C1 nouns",
      difficulty:Object.freeze({all:"All B2–C1 levels",1:"Level 1 — Intermediate",2:"Level 2 — Upper Intermediate",3:"Level 3 — Advanced"})
    })
  });
  const DEFAULT_VOCABULARY_TRACK = "challenge";

  const VocabularyTrackModel = {
    ids:Object.freeze(["challenge","bridge"]),
    normalize(value){ return this.ids.includes(value)?value:DEFAULT_VOCABULARY_TRACK; },
    meta(track){ return VOCABULARY_TRACKS[this.normalize(track)]; },
    wordTrack(word){ return this.normalize(word?.track); },
    words(track){
      const id=this.normalize(track);
      return VOCAB.filter(word=>this.wordTrack(word)===id);
    },
    count(track){ return this.words(track).length; },
    hasWords(track){ return this.count(track)>0; },
    selected(){
      const control=typeof DOM!=="undefined"?DOM.$("#vocabularyTrackSelect"):null;
      const candidate=control?.value || Runtime.state?.settings?.vocabularyTrack || DEFAULT_VOCABULARY_TRACK;
      const normalized=this.normalize(candidate);
      return this.hasWords(normalized)?normalized:DEFAULT_VOCABULARY_TRACK;
    },
    resolveScope(scope="current"){
      if(scope==="all") return "all";
      if(scope==="current") return this.selected();
      return this.normalize(scope);
    },
    wordsForScope(scope="current"){
      const resolved=this.resolveScope(scope);
      return resolved==="all"?[...VOCAB]:this.words(resolved);
    },
    scopeLabel(scope="current"){
      const resolved=this.resolveScope(scope);
      return resolved==="all"?"All vocabulary":`${this.meta(resolved).label} · ${this.meta(resolved).band}`;
    },
    levelLabel(track,level){ return this.meta(track).difficulty[String(level)] || `Level ${level}`; },
    levelLabelForScope(scope,level){
      const resolved=this.resolveScope(scope);
      return resolved==="all"?`Level ${level}`:this.levelLabel(resolved,level);
    },
    aggregateForScope(scope="current"){
      const empty={answers:0,correct:0,currentStreak:0,bestStreak:0};
      if(!Runtime.state) return empty;
      const resolved=this.resolveScope(scope);
      if(resolved==="all") return Runtime.state.aggregates||empty;
      return Runtime.state.aggregatesByTrack?.[resolved]||empty;
    },
    ensureAggregate(track){
      const id=this.normalize(track);
      Runtime.state.aggregatesByTrack ||= {};
      Runtime.state.aggregatesByTrack[id] ||= {answers:0,correct:0,currentStreak:0,bestStreak:0};
      return Runtime.state.aggregatesByTrack[id];
    },
    difficultyOptions(track=this.selected()){
      const meta=this.meta(track);
      return ["all","1","2","3"].map(value=>({value,label:meta.difficulty[value]}));
    },
    syncDifficultyOptions({preserve=true}={}){
      const select=DOM.$("#difficultySelect");
      if(!select) return;
      const previous=preserve?select.value:"all";
      select.innerHTML=this.difficultyOptions().map(item=>`<option value="${item.value}">${item.label}</option>`).join("");
      select.value=["all","1","2","3"].includes(previous)?previous:"all";
    },
    syncLibraryLevelOptions(){
      const select=DOM.$("#levelFilter");
      if(!select) return;
      const previous=select.value||"all";
      const scope=DOM.$("#libraryTrackSelect")?.value||"current";
      const resolved=this.resolveScope(scope);
      const labels=resolved==="all" ? {all:"All levels",1:"Level 1",2:"Level 2",3:"Level 3"} : this.meta(resolved).difficulty;
      select.innerHTML=["all","1","2","3"].map(value=>`<option value="${value}">${labels[value]}</option>`).join("");
      select.value=["all","1","2","3"].includes(previous)?previous:"all";
    },
    syncAvailability(){
      const bridgeCount=this.count("bridge");
      for(const id of ["vocabularyTrackSelect","progressTrackSelect","libraryTrackSelect"]){
        const select=DOM.$(`#${id}`);
        const option=select?.querySelector('option[value="bridge"]');
        if(option){
          option.disabled=bridgeCount===0;
          option.textContent=bridgeCount?`Bridge · B2–C1 (${bridgeCount.toLocaleString()})`:`Bridge · B2–C1 (corpus not installed)`;
        }
      }
      const bridgeButton=DOM.$("#bridgeTrackBtn");
      if(bridgeButton){
        bridgeButton.disabled=bridgeCount===0;
        bridgeButton.setAttribute("aria-disabled",bridgeCount===0?"true":"false");
      }
      const note=DOM.$("#bridgeTrackNote");
      if(note) note.textContent=bridgeCount ? `${bridgeCount.toLocaleString()} intermediate and upper-intermediate nouns are ready.` : "Bridge is wired into the app; its 1,000-word B2–C1 corpus is added in V2-2.";
    },
    syncSurfaceCopy(){
      const track=this.selected();
      const meta=this.meta(track);
      const count=this.count(track);
      const kicker=DOM.$("#practiceTrackKicker");
      if(kicker) kicker.textContent=`${meta.label} · ${meta.band} noun gender`;
      const note=DOM.$("#currentTrackNote");
      if(note) note.textContent=`${meta.label} is selected · ${count.toLocaleString()} ${meta.availableLabel}.`;
      const help=DOM.$("#vocabularyTrackHelp");
      if(help) help.textContent=track==="challenge" ? "Default track · the original 1,000 difficult nouns." : "Optional track · intermediate and upper-intermediate vocabulary.";
      const libraryIntro=DOM.$("#libraryIntro");
      if(libraryIntro){
        const scope=DOM.$("#libraryTrackSelect")?.value||"current";
        const words=this.wordsForScope(scope);
        libraryIntro.textContent=`${words.length.toLocaleString()} installed nouns in ${this.scopeLabel(scope)}, with English meanings, examples, grammar notes, and learning status.`;
      }
      const progressMeta=DOM.$("#progressTrackMeta");
      if(progressMeta){
        const scope=DOM.$("#progressTrackSelect")?.value||"current";
        progressMeta.textContent=`${this.scopeLabel(scope)} · ${this.wordsForScope(scope).length.toLocaleString()} installed nouns`;
      }
    },
    init(){
      const saved=this.normalize(Runtime.state?.settings?.vocabularyTrack);
      const active=this.hasWords(saved)?saved:DEFAULT_VOCABULARY_TRACK;
      const select=DOM.$("#vocabularyTrackSelect");
      if(select) select.value=active;
      Runtime.state.settings ||= {};
      Runtime.state.settings.vocabularyTrack=active;
      this.syncAvailability();
      this.syncDifficultyOptions({preserve:true});
      this.syncLibraryLevelOptions();
      this.syncSurfaceCopy();
    },
    select(track,{persist=true,announce=true}={}){
      const id=this.normalize(track);
      if(!this.hasWords(id)){
        if(announce) AccessibilityManager.announce(`${this.meta(id).label} vocabulary is not installed yet.`);
        return false;
      }
      const select=DOM.$("#vocabularyTrackSelect");
      if(select) select.value=id;
      Runtime.state.settings ||= {};
      Runtime.state.settings.vocabularyTrack=id;
      this.syncDifficultyOptions({preserve:false});
      this.syncLibraryLevelOptions();
      this.syncAvailability();
      this.syncSurfaceCopy();
      if(persist) ProgressStore.save();
      if(announce) AccessibilityManager.announce(`${this.meta(id).label} vocabulary selected.`);
      return true;
    }
  };
'''
html = replace_once(html, '   ].map(createVocabularyEntry);\n\n  const FrequencyModel = {', '   ].map(createVocabularyEntry);' + track_model + '\n\n  const FrequencyModel = {', 'track model insertion')

aggregate_by_track = r'''
    repairAggregatesByTrack(raw,wordProgress,globalAggregates,issues){
      const source=this.isPlainObject(raw)?raw:{};
      if(raw!=null && !this.isPlainObject(raw)) issues.push("aggregatesByTrack: replaced invalid object");
      const result={};
      for(const track of VocabularyTrackModel.ids){
        const ids=new Set(VocabularyTrackModel.words(track).map(word=>word.id));
        let detailedAttempts=0,detailedCorrect=0;
        for(const [id,ws] of Object.entries(wordProgress)){
          if(!ids.has(id)) continue;
          detailedAttempts+=this.nonNegativeInt(ws.attempts);
          detailedCorrect+=this.nonNegativeInt(ws.correct);
        }
        const rawBucket=this.isPlainObject(source[track])?source[track]:(track==="challenge"?globalAggregates:{});
        let answers=Math.max(this.nonNegativeInt(rawBucket.answers),detailedAttempts);
        let correct=Math.min(answers,Math.max(this.nonNegativeInt(rawBucket.correct),detailedCorrect));
        let currentStreak=Math.min(this.nonNegativeInt(rawBucket.currentStreak),correct);
        let bestStreak=Math.min(Math.max(this.nonNegativeInt(rawBucket.bestStreak),currentStreak),correct);
        result[track]={answers,correct,currentStreak,bestStreak};
      }
      return result;
    },
'''
html = replace_once(html, '    repairSummaries(raw,issues){', aggregate_by_track + '    repairSummaries(raw,issues){', 'track aggregate validator')

old_repair_current = r'''repairCurrent(data){
      if(!this.isPlainObject(data)) return {fatal:true,state:null,issues:["root: state is not an object"]};
      if(data.schemaVersion !== SCHEMA_VERSION) return {fatal:true,state:null,issues:[`root: expected schema v${SCHEMA_VERSION}`]};
      const issues=[];
      const base=StateSchema.create({now:Date.now()});
      const wordProgress=this.repairWordProgress(data.wordProgress,issues);
      const reviewEvents=this.repairReviewEvents(data.reviewEvents,issues);
      const state={
        schemaVersion:SCHEMA_VERSION,
        meta:this.repairMeta(data.meta,base,issues),
        user:this.plainObject(data.user,"user",issues),
        wordProgress,
        aggregates:this.repairAggregates(data.aggregates,wordProgress,issues),
        sessions:{
          summaries:this.repairSummaries(data?.sessions?.summaries,issues),
          history:this.objectArray(data?.sessions?.history,"sessions.history",issues)
        },
        reviewEvents,
        settings:this.plainObject(data.settings,"settings",issues),
        customWords:this.objectArray(data.customWords,"customWords",issues),
        suspendedWords:this.stringArray(data.suspendedWords,"suspendedWords",issues)
      };
      if(!this.isPlainObject(data.sessions) && data.sessions != null) issues.push("sessions: replaced invalid object");
      return {fatal:false,state,issues,repaired:issues.length>0};
    }'''
new_repair_current = r'''repairCurrent(data){
      if(!this.isPlainObject(data)) return {fatal:true,state:null,issues:["root: state is not an object"]};
      if(data.schemaVersion !== SCHEMA_VERSION) return {fatal:true,state:null,issues:[`root: expected schema v${SCHEMA_VERSION}`]};
      const issues=[];
      const base=StateSchema.create({now:Date.now()});
      const wordProgress=this.repairWordProgress(data.wordProgress,issues);
      const reviewEvents=this.repairReviewEvents(data.reviewEvents,issues);
      const aggregates=this.repairAggregates(data.aggregates,wordProgress,issues);
      const settings={...this.plainObject(data.settings,"settings",issues)};
      settings.vocabularyTrack=VocabularyTrackModel.normalize(settings.vocabularyTrack);
      const state={
        schemaVersion:SCHEMA_VERSION,
        meta:this.repairMeta(data.meta,base,issues),
        user:this.plainObject(data.user,"user",issues),
        wordProgress,
        aggregates,
        aggregatesByTrack:this.repairAggregatesByTrack(data.aggregatesByTrack,wordProgress,aggregates,issues),
        sessions:{
          summaries:this.repairSummaries(data?.sessions?.summaries,issues),
          history:this.objectArray(data?.sessions?.history,"sessions.history",issues)
        },
        reviewEvents,
        settings,
        customWords:this.objectArray(data.customWords,"customWords",issues),
        suspendedWords:this.stringArray(data.suspendedWords,"suspendedWords",issues)
      };
      if(!this.isPlainObject(data.sessions) && data.sessions != null) issues.push("sessions: replaced invalid object");
      return {fatal:false,state,issues,repaired:issues.length>0};
    }'''
html = replace_once(html, old_repair_current, new_repair_current, 'repairCurrent v10')

html = replace_once(html, '        aggregates:{answers:0,correct:0,currentStreak:0,bestStreak:0},\n        sessions:{summaries:{},history:[]},\n        reviewEvents:[],\n        settings:{},', '        aggregates:{answers:0,correct:0,currentStreak:0,bestStreak:0},\n        aggregatesByTrack:{challenge:{answers:0,correct:0,currentStreak:0,bestStreak:0},bridge:{answers:0,correct:0,currentStreak:0,bestStreak:0}},\n        sessions:{summaries:{},history:[]},\n        reviewEvents:[],\n        settings:{vocabularyTrack:DEFAULT_VOCABULARY_TRACK},', 'default v10 track state')

migration9 = r''',
      9(data){
        const now=Date.now();
        const aggregate=data?.aggregates&&typeof data.aggregates==="object"&&!Array.isArray(data.aggregates) ? data.aggregates : {answers:0,correct:0,currentStreak:0,bestStreak:0};
        return {
          ...data,
          schemaVersion:10,
          meta:{...(data?.meta||{}),updatedAt:now,migratedFrom:data?.meta?.migratedFrom ?? 9,migratedAt:data?.meta?.migratedAt ?? now},
          aggregatesByTrack:{
            challenge:{answers:Number(aggregate.answers)||0,correct:Number(aggregate.correct)||0,currentStreak:Number(aggregate.currentStreak)||0,bestStreak:Number(aggregate.bestStreak)||0},
            bridge:{answers:0,correct:0,currentStreak:0,bestStreak:0}
          },
          settings:{...(data?.settings||{}),vocabularyTrack:VocabularyTrackModel.normalize(data?.settings?.vocabularyTrack)}
        };
      }'''
old_mig_end = r'''        return {...data,schemaVersion:9,meta:{...(data?.meta||{}),updatedAt:now,migratedFrom:data?.meta?.migratedFrom ?? 8,migratedAt:data?.meta?.migratedAt ?? now},wordProgress:migratedWords};
      }
    },'''
new_mig_end = r'''        return {...data,schemaVersion:9,meta:{...(data?.meta||{}),updatedAt:now,migratedFrom:data?.meta?.migratedFrom ?? 8,migratedAt:data?.meta?.migratedAt ?? now},wordProgress:migratedWords};
      }''' + migration9 + r'''
    },'''
html = replace_once(html, old_mig_end, new_mig_end, 'schema 9 to 10 migration')

old_hero = r'''          <span class="section-kicker">C1/C2 noun gender</span>
          <h2 id="practiceHeroTitle">Practice German articles.</h2>
          <p>One word at a time. Choose the article, check the English meaning when you need it, and keep moving.</p>
          <div class="practice-hero-actions">
            <button type="button" class="primary-btn practice-hero-btn" id="openPracticeBtn">Start practice</button>
            <span class="practice-hero-note">Uses your session settings below.</span>
          </div>'''
new_hero = r'''          <span class="section-kicker" id="practiceTrackKicker">Challenge · C1–C2 noun gender</span>
          <h2 id="practiceHeroTitle">Practice German articles.</h2>
          <p>One word at a time. Choose the article, check the English meaning when you need it, and keep moving.</p>
          <div class="practice-hero-actions">
            <button type="button" class="primary-btn practice-hero-btn" id="openPracticeBtn">Start practice</button>
            <button type="button" class="track-link-btn" id="bridgeTrackBtn" aria-describedby="bridgeTrackNote">Study B2–C1 vocabulary →</button>
            <span class="practice-hero-note" id="currentTrackNote">Challenge is selected.</span>
            <span class="practice-hero-note" id="bridgeTrackNote">Bridge is wired into the app; its corpus is added in V2-2.</span>
          </div>'''
html = replace_once(html, old_hero, new_hero, 'home track actions')

mode_control = r'''            <div class="control">
              <label for="modeSelect">Mode</label>'''
track_control = r'''            <div class="control" id="trackControl">
              <label for="vocabularyTrackSelect">Vocabulary</label>
              <select id="vocabularyTrackSelect" aria-describedby="vocabularyTrackHelp">
                <option value="challenge">Challenge · C1–C2</option>
                <option value="bridge">Bridge · B2–C1</option>
              </select>
              <small class="control-help" id="vocabularyTrackHelp">Default track · the original 1,000 difficult nouns.</small>
            </div>
            <div class="control">
              <label for="modeSelect">Mode</label>'''
html = replace_once(html, mode_control, track_control, 'session track selector')

old_stats_heading = r'''      <div class="view-heading">
        <span class="section-kicker">Learning record</span>
        <h2>Progress</h2>
        <p>Recall, review load, response speed, and the words that still need work.</p>
      </div>'''
new_stats_heading = r'''      <div class="view-heading track-aware-heading">
        <div>
          <span class="section-kicker">Learning record</span>
          <h2>Progress</h2>
          <p>Recall, review load, response speed, and the words that still need work.</p>
        </div>
        <label class="track-scope-control" for="progressTrackSelect"><span>Vocabulary</span>
          <select id="progressTrackSelect">
            <option value="current">Current track</option>
            <option value="challenge">Challenge · C1–C2</option>
            <option value="bridge">Bridge · B2–C1</option>
            <option value="all">All vocabulary</option>
          </select>
          <small id="progressTrackMeta">Challenge · C1–C2</small>
        </label>
      </div>'''
html = replace_once(html, old_stats_heading, new_stats_heading, 'progress track scope')

old_library_heading = r'''      <div class="view-heading">
        <span class="section-kicker">Reference</span>
        <h2>Vocabulary</h2>
        <p>1,000 reviewed C1/C2 nouns with English meanings, examples, grammar notes, and learning status.</p>
      </div>'''
new_library_heading = r'''      <div class="view-heading track-aware-heading">
        <div>
          <span class="section-kicker">Reference</span>
          <h2>Vocabulary</h2>
          <p id="libraryIntro">1,000 installed nouns in Challenge · C1–C2, with English meanings, examples, grammar notes, and learning status.</p>
        </div>
        <label class="track-scope-control" for="libraryTrackSelect"><span>Vocabulary set</span>
          <select id="libraryTrackSelect">
            <option value="current">Current track</option>
            <option value="challenge">Challenge · C1–C2</option>
            <option value="bridge">Bridge · B2–C1</option>
            <option value="all">All vocabulary</option>
          </select>
        </label>
      </div>'''
html = replace_once(html, old_library_heading, new_library_heading, 'vocabulary track scope')
html = html.replace('These controls preserve the 1,000-word vocabulary and app itself.', 'These controls preserve the installed vocabulary and app itself.', 1)

html = replace_once(html, '    selectedDifficulty(){\n      return DOM.$("#difficultySelect")?.value||"all";\n    },\n    eligibleWords({difficulty=this.selectedDifficulty()}={}){\n      return VOCAB.filter(word=>{', '    selectedDifficulty(){\n      return DOM.$("#difficultySelect")?.value||"all";\n    },\n    selectedTrack(){ return VocabularyTrackModel.selected(); },\n    eligibleWords({difficulty=this.selectedDifficulty(),track=this.selectedTrack()}={}){\n      return VocabularyTrackModel.words(track).filter(word=>{', 'review queue track filter')
html = replace_once(html, '    build({limit=20,now=Date.now(),difficulty=this.selectedDifficulty()}={}){\n      const candidates=this.eligibleWords({difficulty})', '    build({limit=20,now=Date.now(),difficulty=this.selectedDifficulty(),track=this.selectedTrack()}={}){\n      const candidates=this.eligibleWords({difficulty,track})', 'review queue build track')
html = replace_once(html, '        difficulty,\n        builtAt:now', '        difficulty,\n        track,\n        builtAt:now', 'review queue build result')
html = replace_once(html, '      return this.build({limit:this.selectedLimit(),now,difficulty:this.selectedDifficulty()});', '      return this.build({limit:this.selectedLimit(),now,difficulty:this.selectedDifficulty(),track:this.selectedTrack()});', 'review queue preview track')
html = replace_once(html, '      let pool = VOCAB.filter(w => difficulty === "all" || String(w.level) === difficulty);', '      const track=Runtime.session?.track||VocabularyTrackModel.selected();\n      let pool = VocabularyTrackModel.words(track).filter(w => difficulty === "all" || String(w.level) === difficulty);', 'scheduler track pool')
html = replace_once(html, '    unknownItems({difficulty=DOM.$("#difficultySelect")?.value||"all"}={}){\n      const items=[];\n      for(const word of VOCAB){', '    unknownItems({difficulty=DOM.$("#difficultySelect")?.value||"all",track=Runtime.session?.track||VocabularyTrackModel.selected()}={}){\n      const items=[];\n      for(const word of VocabularyTrackModel.words(track)){', 'unknown items track')

old_score = r'''      Runtime.state.aggregates.answers++;
      Runtime.session.answers++;
      Runtime.session.completed++;
      Runtime.pendingConfidence=null;
      if(correct){
        Runtime.state.aggregates.correct++;
        Runtime.session.correct++;
        Runtime.state.aggregates.currentStreak++;
        Runtime.state.aggregates.bestStreak = Math.max(Runtime.state.aggregates.bestStreak,Runtime.state.aggregates.currentStreak);
      }else{
        Runtime.state.aggregates.currentStreak = 0;'''
new_score = r'''      Runtime.state.aggregates.answers++;
      const trackAggregate=VocabularyTrackModel.ensureAggregate(Runtime.current.track||Runtime.session?.track||VocabularyTrackModel.selected());
      trackAggregate.answers++;
      Runtime.session.answers++;
      Runtime.session.completed++;
      Runtime.pendingConfidence=null;
      if(correct){
        Runtime.state.aggregates.correct++;
        trackAggregate.correct++;
        Runtime.session.correct++;
        Runtime.state.aggregates.currentStreak++;
        Runtime.state.aggregates.bestStreak = Math.max(Runtime.state.aggregates.bestStreak,Runtime.state.aggregates.currentStreak);
        trackAggregate.currentStreak++;
        trackAggregate.bestStreak=Math.max(trackAggregate.bestStreak,trackAggregate.currentStreak);
      }else{
        Runtime.state.aggregates.currentStreak = 0;
        trackAggregate.currentStreak = 0;'''
html = replace_once(html, old_score, new_score, 'track scoring aggregate')
html = replace_once(html, '      DOM.$("#streakDisplay").textContent = Runtime.state.aggregates.currentStreak;', '      DOM.$("#streakDisplay").textContent = VocabularyTrackModel.aggregateForScope(Runtime.session?.track||"current").currentStreak;', 'track streak display')
html = replace_once(html, '      const key = `${Runtime.session.mode}:${Runtime.session.format||"standard"}:${Number.isFinite(Runtime.session.target)?Runtime.session.target:"endless"}`;', '      const key = `${Runtime.session.track||VocabularyTrackModel.selected()}:${Runtime.session.mode}:${Runtime.session.format||"standard"}:${Number.isFinite(Runtime.session.target)?Runtime.session.target:"endless"}`;', 'track session summary key')

stats_start = html.index('  const StatisticsView = {')
stats_end = html.index('\n\n  const DataControls = {', stats_start)
if stats_start < 0 or stats_end < 0:
    raise SystemExit('Missing StatisticsView segment')
stats = html[stats_start:stats_end]
stats = replace_once(stats, '  const StatisticsView = {\n    relativeTime(', '  const StatisticsView = {\n    scope(){ return DOM.$("#progressTrackSelect")?.value||"current"; },\n    words(){ return VocabularyTrackModel.wordsForScope(this.scope()); },\n    aggregate(){ return VocabularyTrackModel.aggregateForScope(this.scope()); },\n    relativeTime(', 'stats scope methods')
stats = replace_once(stats, '    confidenceSummary(){\n      const levels=', '    confidenceSummary(words=this.words()){\n      const levels=', 'stats confidence signature')
stats = replace_once(stats, '      for(const word of VOCAB){', '      for(const word of words){', 'stats confidence words')
stats = replace_once(stats, '      const rows=VOCAB.map(w=>({w,s:LearningModel.getWordState(w.id)}));\n      const total=Runtime.state.aggregates.answers;', '      const words=this.words();\n      const rows=words.map(w=>({w,s:LearningModel.getWordState(w.id)}));\n      const aggregate=this.aggregate();\n      const total=aggregate.answers;', 'stats snapshot scoped rows')
stats = replace_once(stats, '      return {rows,total,accuracy:total?Math.round(Runtime.state.aggregates.correct/total*100):null,mastered,leeches,relearning,weak,seen,due,activity};', '      return {words,rows,aggregate,total,accuracy:total?Math.round(aggregate.correct/total*100):null,mastered,leeches,relearning,weak,seen,due,activity};', 'stats snapshot result')
stats = replace_once(stats, '      DOM.$("#statBestStreak").textContent=Runtime.state.aggregates.bestStreak;\n      DOM.$("#statMedianTime").textContent=TimingAnalytics.format(TimingAnalytics.globalSummary().median);', '      DOM.$("#statBestStreak").textContent=summary.aggregate.bestStreak;\n      DOM.$("#statMedianTime").textContent=TimingAnalytics.format(TimingAnalytics.globalSummary(summary.words).median);\n      const progressMeta=DOM.$("#progressTrackMeta");\n      if(progressMeta) progressMeta.textContent=`${VocabularyTrackModel.scopeLabel(this.scope())} · ${summary.words.length.toLocaleString()} installed nouns`;', 'stats aggregate header')
stats = replace_once(stats, '        for(const w of VOCAB){', '        for(const w of summary.words){', 'stats article words')
stats = replace_once(stats, '["Level 1",VOCAB.filter(w=>w.level===1)],\n        ["Level 2",VOCAB.filter(w=>w.level===2)],\n        ["Level 3",VOCAB.filter(w=>w.level===3)]', '[VocabularyTrackModel.levelLabelForScope(this.scope(),1),summary.words.filter(w=>w.level===1)],\n        [VocabularyTrackModel.levelLabelForScope(this.scope(),2),summary.words.filter(w=>w.level===2)],\n        [VocabularyTrackModel.levelLabelForScope(this.scope(),3),summary.words.filter(w=>w.level===3)]', 'stats level breakdown')
stats = replace_once(stats, '        const pct=Math.round(count/VOCAB.length*100);', '        const pct=Math.round(count/Math.max(1,summary.words.length)*100);', 'stats learning denominator')
stats = replace_once(stats, '      const confidence=this.confidenceSummary();', '      const confidence=this.confidenceSummary(summary.words);', 'stats confidence scope')
stats = replace_once(stats, '      const speed=TimingAnalytics.speedProfile();', '      const speed=TimingAnalytics.speedProfile(summary.words);', 'stats speed scope')
stats = replace_once(stats, '      const confusion=ErrorAnalytics.confusionMatrix();', '      const confusion=ErrorAnalytics.confusionMatrix(summary.words);', 'stats confusion scope')
stats = replace_once(stats, '      const diagnosis=ErrorAnalytics.interpretation();', '      const diagnosis=ErrorAnalytics.interpretation(summary.words);', 'stats diagnosis scope')
html = html[:stats_start] + stats + html[stats_end:]

html = replace_once(html, '    globalSummary(){\n      return this.summarize(this.events());\n    },\n    speedProfile(){\n      const correct=this.events().filter(event=>event.correct);', '    eventsForWords(words=null){\n      if(!Array.isArray(words)) return this.events();\n      const ids=new Set(words.map(word=>word.id));\n      return this.events().filter(event=>ids.has(event.wordId));\n    },\n    globalSummary(words=null){\n      return this.summarize(this.eventsForWords(words));\n    },\n    speedProfile(words=null){\n      const correct=this.eventsForWords(words).filter(event=>event.correct);', 'timing scoped analytics')
html = replace_once(html, '    trackedWords(){\n      return VOCAB.map(word=>({word,ws:LearningModel.getWordState(word.id)}));\n    },\n    choiceTotals(){', '    trackedWords(words=VOCAB){\n      return words.map(word=>({word,ws:LearningModel.getWordState(word.id)}));\n    },\n    choiceTotals(words=VOCAB){', 'error tracked words scope')
html = replace_once(html, '      for(const {ws} of this.trackedWords()){', '      for(const {ws} of this.trackedWords(words)){', 'error choice scope')
html = replace_once(html, '    confusionMatrix(){', '    confusionMatrix(words=VOCAB){', 'confusion signature')
html = replace_once(html, '      for(const {word,ws} of this.trackedWords()){', '      for(const {word,ws} of this.trackedWords(words)){', 'confusion tracked scope')
html = replace_once(html, '    topErrorDirections(){\n      const matrix=this.confusionMatrix();', '    topErrorDirections(words=VOCAB){\n      const matrix=this.confusionMatrix(words);', 'top directions scope')
html = replace_once(html, '    interpretation(){\n      const matrix=this.confusionMatrix();', '    interpretation(words=VOCAB){\n      const matrix=this.confusionMatrix(words);', 'interpretation scope')

vocab_start = html.index('  const VocabularyView = {')
vocab_end = html.index('\n\n  const CoreTrainingModel = {', vocab_start)
if vocab_start < 0 or vocab_end < 0:
    raise SystemExit('Missing VocabularyView segment')
vocab = html[vocab_start:vocab_end]
vocab = replace_once(vocab, '        q:this.normalizeSearch(DOM.$("#librarySearch")?.value||""),article:value("articleFilter"),level:value("levelFilter"),', '        q:this.normalizeSearch(DOM.$("#librarySearch")?.value||""),track:value("libraryTrackSelect"),article:value("articleFilter"),level:value("levelFilter"),', 'library track filter value')
vocab = replace_once(vocab, '      let rows = VOCAB.filter(w=>{', '      const scopedWords=VocabularyTrackModel.wordsForScope(f.track);\n      let rows = scopedWords.filter(w=>{', 'library scoped words')
vocab = replace_once(vocab, '      DOM.$("#libraryMeta").textContent=`${rows.length} of ${VOCAB.length} nouns · ${fullDepth} full-detail · ${rows.length-fullDepth} core-detail`;', '      DOM.$("#libraryMeta").textContent=`${rows.length} of ${scopedWords.length} nouns · ${VocabularyTrackModel.scopeLabel(f.track)} · ${fullDepth} full-detail · ${rows.length-fullDepth} core-detail`;\n      const intro=DOM.$("#libraryIntro");\n      if(intro) intro.textContent=`${scopedWords.length.toLocaleString()} installed nouns in ${VocabularyTrackModel.scopeLabel(f.track)}, with English meanings, examples, grammar notes, and learning status.`;', 'library scoped metadata')
vocab = replace_once(vocab, '<td>Level ${w.level}</td>', '<td>${DOM.escapeHtml(VocabularyTrackModel.meta(w.track).label)} · Level ${w.level}</td>', 'library row track')
vocab = replace_once(vocab, '            <div class="detail-field"><strong>Article</strong><span>${DOM.escapeHtml(articleLabel)} ${DOM.escapeHtml(word.noun)}</span></div>', '            <div class="detail-field"><strong>Set</strong><span>${DOM.escapeHtml(VocabularyTrackModel.meta(word.track).label)} · ${DOM.escapeHtml(VocabularyTrackModel.meta(word.track).band)} · Level ${word.level}</span></div>\n            <div class="detail-field"><strong>Article</strong><span>${DOM.escapeHtml(articleLabel)} ${DOM.escapeHtml(word.noun)}</span></div>', 'word detail track')
html = html[:vocab_start] + vocab + html[vocab_end:]

html = replace_once(html, '    start({mode=null,reviewIds=null,orderedQueue=null,targetOverride=null} = {}){\n      this.clearTimer();\n      if(mode) DOM.$("#modeSelect").value = mode;', '    start({mode=null,reviewIds=null,orderedQueue=null,targetOverride=null,track=null} = {}){\n      this.clearTimer();\n      if(track) VocabularyTrackModel.select(track,{persist:true,announce:false});\n      if(mode) DOM.$("#modeSelect").value = mode;', 'session start track option')
html = replace_once(html, '      Runtime.session = {\n        mode:selectedMode,format:selectedFormat,target,index:0,correct:0,answers:0,completed:0,unknownCount:0,mistakes:new Map(),shortRetries:new Map(),', '      Runtime.session = {\n        track:VocabularyTrackModel.selected(),mode:selectedMode,format:selectedFormat,target,index:0,correct:0,answers:0,completed:0,unknownCount:0,mistakes:new Map(),shortRetries:new Map(),', 'session track state')
html = replace_once(html, '        Runtime.session={\n          mode:"review",format:DOM.$("#formatSelect").value,target:0,index:0,correct:0,answers:0,completed:0,unknownCount:0,mistakes:new Map(),shortRetries:new Map(),', '        Runtime.session={\n          track:built.track||VocabularyTrackModel.selected(),mode:"review",format:DOM.$("#formatSelect").value,target:0,index:0,correct:0,answers:0,completed:0,unknownCount:0,mistakes:new Map(),shortRetries:new Map(),', 'empty review session track')
html = replace_once(html, '      return this.start({mode:"review",orderedQueue:built.ids,targetOverride:built.ids.length});', '      return this.start({mode:"review",orderedQueue:built.ids,targetOverride:built.ids.length,track:built.track});', 'review session track')
html = replace_once(html, '      const mode=Runtime.session?.mode||DOM.$("#modeSelect")?.value||"practice";\n      const format=QuestionFormatModel.sessionFormat(Runtime.session);', '      const mode=Runtime.session?.mode||DOM.$("#modeSelect")?.value||"practice";\n      const track=Runtime.session?.track||VocabularyTrackModel.selected();\n      const title=DOM.$("#practiceScreenTitle");\n      if(title) title.textContent=`${VocabularyTrackModel.meta(track).label} practice`;\n      const format=QuestionFormatModel.sessionFormat(Runtime.session);', 'practice title track')

html = replace_once(html, '      DOM.$("#difficultySelect").addEventListener("change",()=>{', '      DOM.$("#vocabularyTrackSelect").addEventListener("change",()=>{\n        const requested=DOM.$("#vocabularyTrackSelect").value;\n        if(!VocabularyTrackModel.select(requested,{persist:true})) DOM.$("#vocabularyTrackSelect").value=VocabularyTrackModel.selected();\n        ReviewQueueView.render();\n        SessionEngine.start();\n      });\n      DOM.$("#bridgeTrackBtn").addEventListener("click",()=>{\n        if(!VocabularyTrackModel.select("bridge",{persist:true})) return;\n        SessionEngine.start({track:"bridge"});\n        PracticeScreen.open();\n      });\n      DOM.$("#progressTrackSelect").addEventListener("change",()=>{ VocabularyTrackModel.syncSurfaceCopy(); StatisticsView.render(); });\n      DOM.$("#libraryTrackSelect").addEventListener("change",()=>{ VocabularyTrackModel.syncLibraryLevelOptions(); VocabularyTrackModel.syncSurfaceCopy(); VocabularyView.render(); });\n      DOM.$("#difficultySelect").addEventListener("change",()=>{', 'track event bindings')
html = replace_once(html, '      Runtime.state = ProgressStore.load();\n      ThemeManager.init();\n      AppUI.bindEvents();', '      Runtime.state = ProgressStore.load();\n      ThemeManager.init();\n      VocabularyTrackModel.init();\n      AppUI.bindEvents();', 'track initialization')
html = replace_once(html, '        if(ids.length){ SessionEngine.start({mode:"adaptive",reviewIds:ids}); PracticeScreen.open(); }', '        if(ids.length){ SessionEngine.start({mode:"adaptive",reviewIds:ids,track:Runtime.session?.track||VocabularyTrackModel.selected()}); PracticeScreen.open(); }', 'retry mistakes track')

queue_patch = r'''

  const V21ReviewQueueRender = ReviewQueueView.render.bind(ReviewQueueView);
  ReviewQueueView.render = function(now=Date.now()){
    V21ReviewQueueRender(now);
    const summary=DOM.$("#reviewQueueSummary");
    if(summary){
      const track=VocabularyTrackModel.selected();
      summary.textContent=`${VocabularyTrackModel.meta(track).label} · ${summary.textContent}`;
    }
    VocabularyTrackModel.syncSurfaceCopy();
  };
'''
html = replace_once(html, '\n\n  const ThemeManager = {', queue_patch + '\n\n  const ThemeManager = {', 'queue track render wrapper')

css = r'''

  /* V2-1 — vocabulary track architecture */
  .track-link-btn{min-height:0;padding:2px 0;border:0;border-bottom:1px solid currentColor;border-radius:0;background:transparent;color:var(--accent);font:inherit;font-weight:800;cursor:pointer}
  .track-link-btn:hover:not(:disabled){color:var(--accent-dark)}
  .track-link-btn:disabled{color:var(--muted);border-bottom-color:transparent;cursor:not-allowed;opacity:.72}
  .control-help{display:block;margin-top:6px;color:var(--muted);font-size:.78rem;line-height:1.35}
  .track-aware-heading{display:flex;align-items:end;justify-content:space-between;gap:28px}
  .track-aware-heading>div{min-width:0}
  .track-scope-control{display:grid;gap:4px;min-width:210px;color:var(--muted);font-size:.78rem;font-weight:700}
  .track-scope-control>span{letter-spacing:.02em}
  .track-scope-control select{min-width:210px;background:transparent}
  .track-scope-control small{font-weight:500;line-height:1.25}
  #trackControl{grid-column:auto}
  @media(max-width:720px){
    .track-aware-heading{display:grid;gap:14px;align-items:start}
    .track-scope-control,.track-scope-control select{min-width:0;width:100%}
    #trackControl{grid-column:1/-1}
    .practice-hero-actions{align-items:flex-start}
    #bridgeTrackNote{max-width:34rem}
  }
'''
html = replace_once(html, '\n</style>', css + '\n</style>', 'V2-1 CSS')

INDEX.write_text(html, encoding='utf-8')
print('Applied V2-1 vocabulary track architecture')
