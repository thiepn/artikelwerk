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
INDEX.write_text(html, encoding='utf-8')

verify = VERIFY.read_text(encoding='utf-8')

old = "requireFragment(html, 'const APP_VERSION = \"1.1.0\";', 'application version 1.1.0');"
new = "requireFragment(html, 'const APP_VERSION = \"1.2.0\";', 'application version 1.2.0');\nrequireFragment(html, 'const VOCAB_SCHEMA_VERSION = 15;', 'vocabulary schema version 15');\nrequireFragment(html, 'const SCHEMA_VERSION = 10;', 'persistence schema version 10');"
if old not in verify:
    raise SystemExit('Missing V2-1 application-version verifier anchor')
verify = verify.replace(old, new, 1)

anchor = "requireFragment(html, '/* UI5 — editorial rebuild: typography and rules instead of dashboard cards */', 'UI5 editorial rebuild');"
addition = anchor + "\nrequireFragment(html, '/* V2-1 — vocabulary track architecture */', 'V2-1 vocabulary track styles');\nrequireFragment(html, 'const VOCABULARY_TRACKS = Object.freeze', 'V2-1 vocabulary track registry');\nrequireFragment(html, 'track:track===\"bridge\"?\"bridge\":\"challenge\"', 'V2-1 vocabulary row track');\nrequireFragment(html, 'aggregatesByTrack', 'V2-1 per-track aggregate storage');\nrequireFragment(html, 'id=\"vocabularyTrackSelect\"', 'V2-1 Practice vocabulary selector');\nrequireFragment(html, 'id=\"bridgeTrackBtn\"', 'V2-1 Bridge home action');\nrequireFragment(html, 'id=\"progressTrackSelect\"', 'V2-1 Progress vocabulary scope');\nrequireFragment(html, 'id=\"libraryTrackSelect\"', 'V2-1 Vocabulary scope');\nrequireFragment(html, 'target?.focus?.({preventScroll:true});', 'synchronous Practice focus restoration');"
if anchor not in verify:
    raise SystemExit('Missing V2-1 UI5 verifier anchor')
verify = verify.replace(anchor, addition, 1)

VERIFY.write_text(verify, encoding='utf-8')
print('Updated V2-1 source verifier, Bridge availability, and Practice focus return')
