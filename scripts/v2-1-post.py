from pathlib import Path

ROOT = Path('.')
INDEX = ROOT / 'index.html'
VERIFY = ROOT / 'scripts' / 'verify-source.mjs'

html = INDEX.read_text(encoding='utf-8')
bridge_option = '<option value="bridge">Bridge · B2–C1</option>'
count = html.count(bridge_option)
if count != 3:
    raise SystemExit(f'Expected 3 Bridge selector options, found {count}')
html = html.replace(bridge_option, '<option value="bridge" disabled>Bridge · B2–C1</option>')

old_focus = '        requestAnimationFrame(()=>target?.focus?.({preventScroll:true}));'
new_focus = '        target?.focus?.({preventScroll:true});\n        requestAnimationFrame(()=>{ if(document.activeElement!==target) target?.focus?.({preventScroll:true}); });'
if old_focus not in html:
    raise SystemExit('Missing Practice focus-return anchor')
html = html.replace(old_focus, new_focus, 1)

stats_anchor = '\n\n  const DataControls = {'
stats_guard = r'''

  // Track availability is derived from installed vocabulary, not from initial markup.
  // Re-assert it after Progress renders so V2-2 can enable Bridge automatically.
  const V21StatisticsRender = StatisticsView.render.bind(StatisticsView);
  StatisticsView.render = function(...args){
    const result=V21StatisticsRender(...args);
    VocabularyTrackModel.syncAvailability();
    VocabularyTrackModel.syncSurfaceCopy();
    return result;
  };
'''
if stats_anchor not in html:
    raise SystemExit('Missing Statistics render-guard anchor')
html = html.replace(stats_anchor, stats_guard + stats_anchor, 1)

vocab_anchor = '\n\n  const CoreTrainingModel = {'
vocab_guard = r'''

  // Vocabulary is declared later than Progress, so its availability guard belongs here.
  const V21VocabularyRender = VocabularyView.render.bind(VocabularyView);
  VocabularyView.render = function(...args){
    const result=V21VocabularyRender(...args);
    VocabularyTrackModel.syncAvailability();
    return result;
  };
'''
if vocab_anchor not in html:
    raise SystemExit('Missing Vocabulary render-guard anchor')
html = html.replace(vocab_anchor, vocab_guard + vocab_anchor, 1)
INDEX.write_text(html, encoding='utf-8')

verify = VERIFY.read_text(encoding='utf-8')

old = "requireFragment(html, 'const APP_VERSION = \"1.1.0\";', 'application version 1.1.0');"
new = "requireFragment(html, 'const APP_VERSION = \"1.2.0\";', 'application version 1.2.0');\nrequireFragment(html, 'const VOCAB_SCHEMA_VERSION = 15;', 'vocabulary schema version 15');\nrequireFragment(html, 'const SCHEMA_VERSION = 10;', 'persistence schema version 10');"
if old not in verify:
    raise SystemExit('Missing V2-1 application-version verifier anchor')
verify = verify.replace(old, new, 1)

anchor = "requireFragment(html, '/* UI5 — editorial rebuild: typography and rules instead of dashboard cards */', 'UI5 editorial rebuild');"
addition = anchor + "\nrequireFragment(html, '/* V2-1 — vocabulary track architecture */', 'V2-1 vocabulary track styles');\nrequireFragment(html, 'const VOCABULARY_TRACKS = Object.freeze', 'V2-1 vocabulary track registry');\nrequireFragment(html, 'track:track===\"bridge\"?\"bridge\":\"challenge\"', 'V2-1 vocabulary row track');\nrequireFragment(html, 'aggregatesByTrack', 'V2-1 per-track aggregate storage');\nrequireFragment(html, 'id=\"vocabularyTrackSelect\"', 'V2-1 Practice vocabulary selector');\nrequireFragment(html, 'id=\"bridgeTrackBtn\"', 'V2-1 Bridge home action');\nrequireFragment(html, 'id=\"progressTrackSelect\"', 'V2-1 Progress vocabulary scope');\nrequireFragment(html, 'id=\"libraryTrackSelect\"', 'V2-1 Vocabulary scope');\nrequireFragment(html, 'target?.focus?.({preventScroll:true});', 'synchronous Practice focus restoration');\nrequireFragment(html, 'const V21StatisticsRender = StatisticsView.render.bind(StatisticsView);', 'Progress render-time track availability guard');\nrequireFragment(html, 'const V21VocabularyRender = VocabularyView.render.bind(VocabularyView);', 'Vocabulary render-time track availability guard');"
if anchor not in verify:
    raise SystemExit('Missing V2-1 UI5 verifier anchor')
verify = verify.replace(anchor, addition, 1)

VERIFY.write_text(verify, encoding='utf-8')
print('Updated V2-1 verifier, correctly placed availability guards, and Practice focus return')
