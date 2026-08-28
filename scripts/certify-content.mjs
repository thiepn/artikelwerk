import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const rootDir=dirname(dirname(fileURLToPath(import.meta.url)));
const html=await readFile(join(rootDir,'index.html'),'utf8');
const translationsSource=await readFile(join(rootDir,'translations.js'),'utf8');
const provenance=JSON.parse(await readFile(join(rootDir,'content','provenance.json'),'utf8'));
const ambiguous=JSON.parse(await readFile(join(rootDir,'content','ambiguous-gender-review.json'),'utf8'));
const examplesReview=JSON.parse(await readFile(join(rootDir,'content','example-review.json'),'utf8'));
const inflectionReview=JSON.parse(await readFile(join(rootDir,'content','inflection-review.json'),'utf8'));
function fail(message){throw new Error(message);}
function parseVocabulary(source){const valid=new Set(['der','die','das']);const rows=[];for(const line of source.split(/\r?\n/)){const value=line.trim();if(!value.startsWith('[\"')||!value.endsWith('],'))continue;try{const row=JSON.parse(value.slice(0,-1));if(Array.isArray(row)&&row.length>=7&&valid.has(row[2])&&Number.isInteger(row[3]))rows.push(row);}catch{}}return rows;}
const vocabulary=parseVocabulary(html);
if(vocabulary.length!==1000)fail(`Expected 1000 vocabulary entries, found ${vocabulary.length}`);
const ids=new Set(vocabulary.map(row=>row[0]));
if(ids.size!==1000)fail('Vocabulary ids are not unique.');
const context={window:{}};vm.runInNewContext(translationsSource,context,{filename:'translations.js'});
const globals=context.window;
const translations=globals.ARTIKELWERK_TRANSLATIONS||{};const runtimeProvenance=globals.ARTIKELWERK_TRANSLATION_PROVENANCE||{};
if(Object.keys(translations).length!==1000)fail('Certified translation map must contain 1000 entries.');
if(Object.keys(runtimeProvenance).length!==1000)fail('Runtime provenance map must contain 1000 entries.');
if((globals.ARTIKELWERK_TRANSLATION_FALLBACKS||[]).length!==0)fail('Runtime topic-label fallbacks must be empty.');
if(globals.ARTIKELWERK_CONTENT_CERTIFICATION?.reviewStatus!=='certified')fail('Runtime content certification marker is missing.');
for(const id of ids){if(typeof translations[id]!=='string'||!translations[id].trim())fail(`Missing certified gloss for ${id}`);if(runtimeProvenance[id]?.reviewStatus!=='release-reviewed')fail(`Unreviewed runtime gloss: ${id}`);if(provenance.entries?.[id]?.reviewStatus!=='release-reviewed')fail(`Missing formal provenance: ${id}`);}
if(Object.keys(provenance.entries||{}).length!==1000||provenance.counts?.uncertified!==0)fail('Formal provenance coverage is incomplete.');
const requiredOverrides=["handlungsansatz","kompetenzprofil","bewertungsansatz","interpretationsansatz","deutungsansatz","analyseansatz","forschungsansatz","grundbedarf","handlungsdruck","methodenmix","mitteleinsatz","normenkonflikt","regelungsbedarf","themenspektrum","anforderungsniveau","aussagekriterium","erkenntnispotenzial","erkenntnisziel","erkenntnisniveau","erkenntnismodell","zielmodell","zielprinzip"];for(const id of requiredOverrides){if(provenance.entries[id]?.sourceKind!=='editorial-certification')fail(`Editorial certification override missing for ${id}`);}
if(/\b(?:Der|Die|Das) \{noun\}/.test(html))fail('Hard-coded generated-example articles remain.');
if(html.includes('Hinweiss'))fail('Invalid genitive Hinweiss remains.');
if(!html.includes('\"genitive\":\"Hinweises\"'))fail('Corrected genitive Hinweises is missing.');
if(!html.includes('provenance:Object.freeze(window.ARTIKELWERK_TRANSLATION_PROVENANCE||{})'))fail('Translation certification gate is missing.');
if(html.includes('return String(word.group||\"meaning unavailable\").replace(/-/g,\" ")'))fail('Unreviewed semantic-group fallback remains in runtime.');
const senseKeys=new Set(globals.ARTIKELWERK_SENSE_CERTIFICATION||[]);for(const key of ['erbe:inheritance','erbe:heir','mangel:deficiency','mangel:mangle-machine'])if(!senseKeys.has(key))fail(`Missing reviewed sense gate: ${key}`);
const ambiguityExpectations=[['primat','current-gender-variant'],['dossier','historical-gender-variant'],['erbe','meaning-dependent-gender'],['mangel','meaning-dependent-gender']];for(const [id,type] of ambiguityExpectations){if(ambiguous.entries?.[id]?.type!==type||ambiguous.entries[id].reviewStatus!=='externally-verified')fail(`Ambiguous-gender review missing for ${id}`);}
if(ambiguous.entries.primat.acceptedArticles.join('/')!=='der/das')fail('Primat current articles must be der/das.');
if(ambiguous.entries.dossier.acceptedArticles.join('/')!=='das')fail('Dossier current article must be das.');
if(inflectionReview.externallyVerified?.hinweis?.genitive!=='Hinweises')fail('Hinweis inflection review is missing.');
const marker='  const EXAMPLE_CONTEXT_META = ';const start=html.indexOf(marker);const end=html.indexOf('\n\n  function exampleMetadataFor',start);if(start<0||end<0)fail('Could not extract example context metadata.');const expression=html.slice(start+marker.length,end).trim().replace(/;$/,'');const meta=vm.runInNewContext(`(${expression})`);
const wrongArticles={der:['Die','Das'],die:['Der','Das'],das:['Der','Die']};let generatedCount=0;for(const [id,noun,article,,,original,group] of vocabulary){if(!original.includes(noun))fail(`Core example does not contain noun for ${id}`);for(const wrong of wrongArticles[article])if(original.includes(`${wrong} ${noun}`))fail(`Wrong core-example article for ${id}: ${wrong}`);const term=`${article} ${noun}`;const termCap=term.charAt(0).toLocaleUpperCase('de-DE')+term.slice(1);const templates=meta.templates[group]||['In der Diskussion spielte {term} eine wichtige Rolle.','Im Bericht wurde deutlich, warum {term} für die Einordnung relevant war.'];for(const template of templates){const rendered=template.replaceAll('{noun}',noun).replaceAll('{term_cap}',termCap).replaceAll('{term}',term);generatedCount++;if(/\{(?:noun|term|term_cap)\}/.test(rendered))fail(`Unresolved example token for ${id}`);for(const wrong of wrongArticles[article])if(rendered.includes(`${wrong} ${noun}`))fail(`Wrong generated-example article for ${id}: ${rendered}`);}}
if(generatedCount!==2000)fail(`Expected 2000 generated context examples, validated ${generatedCount}`);if(examplesReview.totalRuntimeExamples!==3000)fail('Example review summary must certify 3000 runtime examples.');
console.log(`Content certification passed: 1000 reviewed glosses, 3000 validated examples, 4 externally verified ambiguous-gender entries.`);
