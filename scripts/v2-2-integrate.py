#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path('.')


def replace_once(text,old,new,label):
    if old not in text:
        raise SystemExit(f'Missing V2-2 integration anchor: {label}')
    return text.replace(old,new,1)

# index.html — load checked-in Bridge assets and append them through the existing vocabulary factory.
index=ROOT/'index.html'
html=index.read_text(encoding='utf-8')
html=replace_once(html,
    '<meta name="description" content="A focused C1/C2 German noun-gender trainer with adaptive review, contextual practice, and productive recall." />',
    '<meta name="description" content="A focused B2–C2 German noun-gender trainer with Challenge and Bridge vocabulary tracks, adaptive review, and productive recall." />',
    'meta description')
html=replace_once(html,'<title>Artikelwerk — C1/C2 German Article Trainer</title>','<title>Artikelwerk — B2–C2 German Article Trainer</title>','title')
html=replace_once(html,
    '<script src="translations.js"></script>\n<script>',
    '<script src="translations.js"></script>\n<script src="bridge-translations.js"></script>\n<script src="bridge-corpus.js"></script>\n<script>',
    'Bridge script loading')
html=replace_once(html,'const APP_VERSION = "1.2.0";','const APP_VERSION = "1.3.0";','app version')
html=replace_once(html,'const VOCAB_SCHEMA_VERSION = 15;','const VOCAB_SCHEMA_VERSION = 16;','vocabulary schema')

old_translation='''  const TranslationModel = {
    data:Object.freeze(window.ARTIKELWERK_TRANSLATIONS||{}),
    provenance:Object.freeze(window.ARTIKELWERK_TRANSLATION_PROVENANCE||{}),
    fallbackIds:new Set(window.ARTIKELWERK_TRANSLATION_FALLBACKS||[]),
    senseCertification:new Set(window.ARTIKELWERK_SENSE_CERTIFICATION||[]),
    text(word,sense=null){
      if(!word) return "English gloss unavailable";
      const active=sense||MeaningGenderModel.activeSense(word);
      if(MeaningGenderModel.isMeaningDependent(word) && active?.gloss){
        return this.senseCertification.has(`${word.id}:${active.id}`) ? active.gloss : "English gloss unavailable";
      }
      const stored=this.data[word.id];
      const review=this.provenance[word.id];
      if(review?.reviewStatus==="release-reviewed" && typeof stored==="string" && stored.trim()) return stored.trim();
      return "English gloss unavailable";
    },
    isFallback(word,sense=null){
      if(!word) return true;
      const active=sense||MeaningGenderModel.activeSense(word);
      if(MeaningGenderModel.isMeaningDependent(word) && active?.gloss) return !this.senseCertification.has(`${word.id}:${active.id}`);
      return this.fallbackIds.has(word.id) || this.provenance[word.id]?.reviewStatus!=="release-reviewed" || !this.data[word.id];
    },
    label(word,sense=null){ return this.isFallback(word,sense)?"English unavailable":"English"; }
  };'''
new_translation='''  const TranslationModel = {
    data:Object.freeze(window.ARTIKELWERK_TRANSLATIONS||{}),
    provenance:Object.freeze(window.ARTIKELWERK_TRANSLATION_PROVENANCE||{}),
    fallbackIds:new Set(window.ARTIKELWERK_TRANSLATION_FALLBACKS||[]),
    senseCertification:new Set(window.ARTIKELWERK_SENSE_CERTIFICATION||[]),
    certifiedReview(review){ return ["release-reviewed","source-certified"].includes(review?.reviewStatus); },
    text(word,sense=null){
      if(!word) return "English gloss unavailable";
      const active=sense||MeaningGenderModel.activeSense(word);
      if(MeaningGenderModel.isMeaningDependent(word) && active?.gloss){
        return this.senseCertification.has(`${word.id}:${active.id}`) ? active.gloss : "English gloss unavailable";
      }
      const stored=this.data[word.id];
      const review=this.provenance[word.id];
      if(this.certifiedReview(review) && typeof stored==="string" && stored.trim()) return stored.trim();
      return "English gloss unavailable";
    },
    isFallback(word,sense=null){
      if(!word) return true;
      const active=sense||MeaningGenderModel.activeSense(word);
      if(MeaningGenderModel.isMeaningDependent(word) && active?.gloss) return !this.senseCertification.has(`${word.id}:${active.id}`);
      return this.fallbackIds.has(word.id) || !this.certifiedReview(this.provenance[word.id]) || !this.data[word.id];
    },
    label(word,sense=null){ return this.isFallback(word,sense)?"English unavailable":"English"; }
  };'''
html=replace_once(html,old_translation,new_translation,'TranslationModel certification status')
html=replace_once(html,
    'function createVocabularyEntry([id,noun,article,level,rule,example,group,coverageTier="full-depth",expansionPhase=null,track="challenge"]){',
    'function createVocabularyEntry([id,noun,article,level,rule,example,group,coverageTier="full-depth",expansionPhase=null,track="challenge",sourceMeta=null]){',
    'vocabulary factory source metadata')
html=replace_once(html,
    '      frequency:frequencyMetadataFor(id,level),',
    '      frequency:sourceMeta?.frequencyRank ? {band:level===1?"frequent":level===2?"common":"less-common",rank:sourceMeta.frequencyRank,source:"V2-2 wordhoard v0.1.0 frequency rank"} : frequencyMetadataFor(id,level),',
    'Bridge frequency metadata')
html=replace_once(html,
    '      source:{kind:"core",status:coverageTier==="full-depth"?"curated":"curated-expansion",...(expansionPhase?{phase:expansionPhase}:{})},\n      contentCertification:window.ARTIKELWERK_TRANSLATION_PROVENANCE?.[id]||null',
    '      source:track==="bridge" ? {kind:"bridge",status:"source-certified",phase:expansionPhase||"V2-2",evidence:sourceMeta||null} : {kind:"core",status:coverageTier==="full-depth"?"curated":"curated-expansion",...(expansionPhase?{phase:expansionPhase}:{})},\n      sourceEvidence:sourceMeta||null,\n      contentCertification:window.ARTIKELWERK_TRANSLATION_PROVENANCE?.[id]||null',
    'Bridge source metadata')
html=replace_once(html,
    '   ].map(createVocabularyEntry);\n\n  // V2-1: Challenge remains the default corpus.',
    '   ].map(createVocabularyEntry);\n\n  const BRIDGE_CORPUS = Array.isArray(window.ARTIKELWERK_BRIDGE_CORPUS) ? window.ARTIKELWERK_BRIDGE_CORPUS : [];\n  VOCAB.push(...BRIDGE_CORPUS.map(createVocabularyEntry));\n\n  // V2-1: Challenge remains the default corpus.',
    'Bridge corpus append')
index.write_text(html,encoding='utf-8')

# package.json
package_path=ROOT/'package.json'
package=json.loads(package_path.read_text(encoding='utf-8'))
package['version']='1.3.0'
package['description']='German noun-gender trainer with 1,000-word Challenge C1/C2 and 1,000-word Bridge B2/C1 tracks'
scripts=package['scripts']
scripts['certify:bridge']='node scripts/certify-bridge.mjs'
scripts['test:bridge-browser']='node tests/bridge-corpus.mjs'
scripts['ci:static']='npm run check && npm run certify:content && npm run certify:bridge && npm run build && npm run test:build'
package_path.write_text(json.dumps(package,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

# Deterministic build: include the separate Bridge data/license/audit assets.
build_path=ROOT/'scripts'/'build.mjs'
build=build_path.read_text(encoding='utf-8')
build=replace_once(build,
    "  ['translations.js', 'translations.js'],\n  ['THIRD_PARTY_NOTICES.md', 'THIRD_PARTY_NOTICES.md'],",
    "  ['translations.js', 'translations.js'],\n  ['bridge-translations.js', 'bridge-translations.js'],\n  ['bridge-corpus.js', 'bridge-corpus.js'],\n  ['THIRD_PARTY_NOTICES.md', 'THIRD_PARTY_NOTICES.md'],",
    'build Bridge runtime assets')
build=replace_once(build,
    "  ['LICENSES/GPL-3.0.txt', 'LICENSES/GPL-3.0.txt'],",
    "  ['LICENSES/GPL-3.0.txt', 'LICENSES/GPL-3.0.txt'],\n  ['LICENSES/CC-BY-SA-4.0.txt', 'LICENSES/CC-BY-SA-4.0.txt'],",
    'build Bridge license')
build=replace_once(build,
    "  ['content/inflection-review.json', 'content/inflection-review.json'],",
    "  ['content/inflection-review.json', 'content/inflection-review.json'],\n  ['content/bridge-provenance.json', 'content/bridge-provenance.json'],\n  ['content/bridge-corpus-report.json', 'content/bridge-corpus-report.json'],\n  ['docs/v2-2-bridge-corpus.md', 'docs/v2-2-bridge-corpus.md'],",
    'build Bridge evidence')
build_path.write_text(build,encoding='utf-8')

# Source verifier keeps Challenge's inline 1,000-row proof and adds explicit Bridge runtime invariants.
verify_path=ROOT/'scripts'/'verify-source.mjs'
verify=verify_path.read_text(encoding='utf-8')
verify=replace_once(verify,
    "requireFragment(html, '<script src=\"translations.js\"></script>', 'local translation asset');",
    "requireFragment(html, '<script src=\"translations.js\"></script>', 'Challenge local translation asset');\nrequireFragment(html, '<script src=\"bridge-translations.js\"></script>', 'Bridge local translation asset');\nrequireFragment(html, '<script src=\"bridge-corpus.js\"></script>', 'Bridge local corpus asset');\nrequireFragment(html, 'VOCAB.push(...BRIDGE_CORPUS.map(createVocabularyEntry));', 'Bridge corpus runtime integration');\nrequireFragment(html, 'certifiedReview(review){ return [\"release-reviewed\",\"source-certified\"].includes(review?.reviewStatus); }', 'dual content certification status');",
    'verifier Bridge scripts')
verify=replace_once(verify,"requireFragment(html, 'const APP_VERSION = \"1.2.0\";', 'application version 1.2.0');","requireFragment(html, 'const APP_VERSION = \"1.3.0\";', 'application version 1.3.0');",'verifier app version')
verify=replace_once(verify,"requireFragment(html, 'const VOCAB_SCHEMA_VERSION = 15;', 'vocabulary schema version 15');","requireFragment(html, 'const VOCAB_SCHEMA_VERSION = 16;', 'vocabulary schema version 16');",'verifier vocab schema')
verify=replace_once(verify,
    "if (JSON.stringify(externalScripts) !== JSON.stringify(['translations.js'])) {",
    "if (JSON.stringify(externalScripts) !== JSON.stringify(['translations.js','bridge-translations.js','bridge-corpus.js'])) {",
    'external script allowlist')
verify=replace_once(verify,
    "if (vocabulary.length !== 1000) fail(`Expected exactly 1000 vocabulary entries, found ${vocabulary.length}.`);",
    "if (vocabulary.length !== 1000) fail(`Expected exactly 1000 inline Challenge vocabulary entries, found ${vocabulary.length}.`);",
    'Challenge wording')
verify=replace_once(verify,
    "console.log(`Source verification passed: ${vocabulary.length} nouns, ${translationIds.length} local glosses, ${staticIds.length} static ids.`);",
    "for (const relativePath of ['bridge-corpus.js','bridge-translations.js','content/bridge-provenance.json','content/bridge-corpus-report.json','docs/v2-2-bridge-corpus.md','LICENSES/CC-BY-SA-4.0.txt']) { try { await access(join(rootDir, relativePath)); } catch { fail(`Missing V2-2 Bridge asset: ${relativePath}`); } }\nconsole.log(`Source verification passed: ${vocabulary.length} Challenge nouns + certified Bridge assets, ${translationIds.length} Challenge glosses, ${staticIds.length} static ids.`);",
    'Bridge asset presence')
verify_path.write_text(verify,encoding='utf-8')

# V2-1 compatibility suite: architecture remains, but Bridge is now installed/enabled.
tracks_path=ROOT/'tests'/'vocabulary-tracks.mjs'
tracks=tracks_path.read_text(encoding='utf-8')
tracks=tracks.replace("assert.equal(await optionDisabled(page,'#vocabularyTrackSelect option[value=\"bridge\"]'),true,`${profile.name}: empty Bridge option should be disabled`);","assert.equal(await optionDisabled(page,'#vocabularyTrackSelect option[value=\"bridge\"]'),false,`${profile.name}: installed Bridge option should be enabled`);")
tracks=tracks.replace("assert.equal(await page.locator('#bridgeTrackBtn').isDisabled(),true,`${profile.name}: empty Bridge CTA should be disabled`);","assert.equal(await page.locator('#bridgeTrackBtn').isDisabled(),false,`${profile.name}: installed Bridge CTA should be enabled`);")
tracks=tracks.replace("assert.match((await page.locator('#bridgeTrackNote').textContent())||'',/V2-2|corpus/i,`${profile.name}: Bridge readiness note missing`);","assert.match((await page.locator('#bridgeTrackNote').textContent())||'',/1,000.*ready|1,000.*intermediate/i,`${profile.name}: installed Bridge readiness note missing`);")
tracks=tracks.replace("assert.equal(await optionDisabled(page,'#progressTrackSelect option[value=\"bridge\"]'),true,`${profile.name}: empty Bridge Progress scope should be disabled`);","assert.equal(await optionDisabled(page,'#progressTrackSelect option[value=\"bridge\"]'),false,`${profile.name}: installed Bridge Progress scope should be enabled`);")
tracks=tracks.replace("/All vocabulary.*1,000/i,`${profile.name}: All Progress scope metadata is wrong`","/All vocabulary.*2,000/i,`${profile.name}: All Progress scope metadata is wrong`")
tracks=tracks.replace("assert.equal(await optionDisabled(page,'#libraryTrackSelect option[value=\"bridge\"]'),true,`${profile.name}: empty Bridge library scope should be disabled`);","assert.equal(await optionDisabled(page,'#libraryTrackSelect option[value=\"bridge\"]'),false,`${profile.name}: installed Bridge library scope should be enabled`);")
tracks=tracks.replace("/1000 of 1000 nouns.*All vocabulary/i,`${profile.name}: All library scope is wrong`","/2000 of 2000 nouns.*All vocabulary/i,`${profile.name}: All library scope is wrong`")
tracks_path.write_text(tracks,encoding='utf-8')

# README
readme_path=ROOT/'README.md'
readme=readme_path.read_text(encoding='utf-8')
old_tracks='''## Vocabulary tracks

- **Challenge · C1–C2** — the original 1,000 difficult nouns. Challenge remains the default practice experience.
- **Bridge · B2–C1** — the optional intermediate/upper-intermediate track. V2-1 provides its complete Practice/Progress/Vocabulary architecture, but the track remains unavailable until the 1,000-word Bridge corpus is installed in V2-2.
- Existing progress is preserved as Challenge progress. Global totals remain available through the All-vocabulary Progress scope.
- No easier placeholder nouns or duplicated Challenge nouns are used to simulate Bridge availability.

See `docs/v2-1-vocabulary-tracks.md` for the architecture and persistence contract.'''
new_tracks='''## Vocabulary tracks

- **Challenge · C1–C2** — the original 1,000 difficult nouns. Challenge remains the default practice experience.
- **Bridge · B2–C1** — 1,000 additional intermediate-to-advanced nouns: 400 Intermediate, 350 Upper Intermediate, and 250 Advanced.
- Bridge difficulty is source-informed and editorially screened. Its B2/C1 labels are targeting estimates, not official Goethe list membership.
- Existing progress remains Challenge progress; Bridge starts independently, while **All vocabulary** reports across all 2,000 installed nouns.
- Challenge and Bridge have zero noun/ID overlap.

See `docs/v2-1-vocabulary-tracks.md` for the architecture/persistence contract and `docs/v2-2-bridge-corpus.md` for corpus construction, sources, screening, and licensing.'''
readme=replace_once(readme,old_tracks,new_tracks,'README vocabulary tracks')
readme=replace_once(readme,
    '`index.html` is the single human-readable application source and the file served by the current GitHub Pages configuration. `translations.js` is the checked-in local English-gloss dataset used by that application.',
    '`index.html` is the single human-readable application source and the file served by the current GitHub Pages configuration. Challenge glosses remain in `translations.js`; the checked-in Bridge corpus and glosses live in the separate `bridge-corpus.js` and `bridge-translations.js` assets.',
    'README canonical source')
readme=replace_once(readme,
    'translations.js                    local English-gloss dataset\n',
    'translations.js                    Challenge English-gloss dataset\nbridge-corpus.js                    1,000-row Bridge vocabulary asset\nbridge-translations.js              Bridge English gloss + provenance runtime asset\n',
    'README layout')
readme=replace_once(readme,
    'See `THIRD_PARTY_NOTICES.md` and `LICENSES/GPL-3.0.txt` for the FreeDict-derived English-gloss subset.',
    'See `THIRD_PARTY_NOTICES.md`, `LICENSES/GPL-3.0.txt`, and `LICENSES/CC-BY-SA-4.0.txt`. Challenge and Bridge data licenses are documented separately.',
    'README licensing')
readme=replace_once(readme,
    '- `translations.js` is the runtime-certified local gloss asset.\n- `content/provenance.json` records source kind and review state for all currently installed nouns.',
    '- `translations.js` is the release-reviewed Challenge gloss asset; `bridge-translations.js` is the source-certified Bridge gloss asset.\n- `content/provenance.json` retains the 1,000-word Challenge provenance; `content/bridge-provenance.json` independently records all 1,000 Bridge entries.',
    'README content certification')
readme=replace_once(readme,
    '- `scripts/certify-content.mjs` exhaustively validates translation, provenance, example, ambiguity, and targeted inflection invariants.',
    '- `scripts/certify-content.mjs` preserves the mature Challenge certification. `scripts/certify-bridge.mjs` separately certifies the 1,000-row Bridge split, source evidence, translations, licensing, examples, and zero overlap.',
    'README certifier')
readme_path.write_text(readme,encoding='utf-8')

# Third-party notices
notice_path=ROOT/'THIRD_PARTY_NOTICES.md'
notice=notice_path.read_text(encoding='utf-8')
bridge_notice='''

## Bridge vocabulary dataset — wordhoard + German Wiktionary

`bridge-corpus.js`, `bridge-translations.js`, and `content/bridge-provenance.json` contain the V2-2 Bridge vocabulary dataset. These Bridge data assets are distributed under **Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA-4.0)**; a copy is included at `LICENSES/CC-BY-SA-4.0.txt`.

Bridge candidate selection, frequency ranks, German noun gender, and German CEFR estimates derive from **wordhoard v0.1.0 (2026-07-16)** by Nathan Mathias, available from `https://github.com/natema/wordhoard`. The pinned release archive has SHA-256 `83837efd46241e7226fc6daaa9d0cc81b57bf746434b8c539049c660d98ba761`. wordhoard combines openly licensed lexical sources with OpenSubtitles-derived frequency evidence; its German CEFR estimates use Goethe A1–B1 material only as upstream calibration and do not redistribute Goethe list content.

Bridge English translations and an independent gender/common-noun cross-check derive from **German Wiktionary** through the `de-wiktionary-parser` extraction pinned to commit `73075bb76c9261c44923f4909858586b261bfd83` (`de_noun_entries_with_translations.zip`, Git blob `a56efcb80b64433107ec1f376b933c572f2427c9`). German Wiktionary content is available under CC-BY-SA and GFDL terms; Artikelwerk's Bridge data distribution uses CC-BY-SA-4.0.

Artikelwerk modifies and filters the upstream material by removing Challenge overlaps, names/special-name-only entries, ambiguous/multi-gender items, malformed/noisy/basic candidates, and by assigning the final Bridge learning tiers. Generated learner examples and article-guidance text are Artikelwerk additions. See `docs/v2-2-bridge-corpus.md` for the full construction method and modification record.
'''
if '## Bridge vocabulary dataset' not in notice:
    notice=notice.rstrip()+bridge_notice+'\n'
notice_path.write_text(notice,encoding='utf-8')

# Permanent read-only CI: certify Bridge and run the ninth browser suite.
ci_path=ROOT/'.github'/'workflows'/'ci.yml'
ci=ci_path.read_text(encoding='utf-8')
ci=replace_once(ci,
    'name: Source, certified content, deterministic build, visual acceptance, and vocabulary tracks',
    'name: Source, 2,000-word content, deterministic build, visual acceptance, and vocabulary tracks',
    'CI job name')
ci=replace_once(ci,
    'run: python -m py_compile scripts/generate_translations.py scripts/generate_translations_v2.py',
    'run: python -m py_compile scripts/generate_translations.py scripts/generate_translations_v2.py scripts/generate_bridge_corpus.py scripts/refine_bridge_corpus.py',
    'CI Python generators')
ci=replace_once(ci,
    'ARTIKELWERK_URL=http://127.0.0.1:4173 npm run test:tracks-browser\n',
    'ARTIKELWERK_URL=http://127.0.0.1:4173 npm run test:tracks-browser\n          ARTIKELWERK_URL=http://127.0.0.1:4173 npm run test:bridge-browser\n',
    'CI Bridge browser suite')
ci_path.write_text(ci,encoding='utf-8')

print('Applied V2-2 runtime integration and permanent certification wiring')
