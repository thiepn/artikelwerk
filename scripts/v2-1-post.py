from pathlib import Path

ROOT = Path('.')
VERIFY = ROOT / 'scripts' / 'verify-source.mjs'
verify = VERIFY.read_text(encoding='utf-8')

old = "requireFragment(html, 'const APP_VERSION = \"1.1.0\";', 'application version 1.1.0');"
new = "requireFragment(html, 'const APP_VERSION = \"1.2.0\";', 'application version 1.2.0');\nrequireFragment(html, 'const VOCAB_SCHEMA_VERSION = 15;', 'vocabulary schema version 15');\nrequireFragment(html, 'const SCHEMA_VERSION = 10;', 'persistence schema version 10');"
if old not in verify:
    raise SystemExit('Missing V2-1 application-version verifier anchor')
verify = verify.replace(old, new, 1)

anchor = "requireFragment(html, '/* UI5 — editorial rebuild: typography and rules instead of dashboard cards */', 'UI5 editorial rebuild');"
addition = anchor + "\nrequireFragment(html, '/* V2-1 — vocabulary track architecture */', 'V2-1 vocabulary track styles');\nrequireFragment(html, 'const VOCABULARY_TRACKS = Object.freeze', 'V2-1 vocabulary track registry');\nrequireFragment(html, 'track:track===\"bridge\"?\"bridge\":\"challenge\"', 'V2-1 vocabulary row track');\nrequireFragment(html, 'aggregatesByTrack', 'V2-1 per-track aggregate storage');\nrequireFragment(html, 'id=\"vocabularyTrackSelect\"', 'V2-1 Practice vocabulary selector');\nrequireFragment(html, 'id=\"bridgeTrackBtn\"', 'V2-1 Bridge home action');\nrequireFragment(html, 'id=\"progressTrackSelect\"', 'V2-1 Progress vocabulary scope');\nrequireFragment(html, 'id=\"libraryTrackSelect\"', 'V2-1 Vocabulary scope');"
if anchor not in verify:
    raise SystemExit('Missing V2-1 UI5 verifier anchor')
verify = verify.replace(anchor, addition, 1)

VERIFY.write_text(verify, encoding='utf-8')
print('Updated permanent source verifier for V2-1')
