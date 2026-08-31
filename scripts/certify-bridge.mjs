import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const root=dirname(dirname(fileURLToPath(import.meta.url)));
const read=(...parts)=>readFile(join(root,...parts),'utf8');
const fail=(message)=>{throw new Error(message);};

const html=await read('index.html');
const corpusSource=await read('bridge-corpus.js');
const translationSource=await read('bridge-translations.js');
const provenance=JSON.parse(await read('content','bridge-provenance.json'));
const report=JSON.parse(await read('content','bridge-corpus-report.json'));
const docs=await read('docs','v2-2-bridge-corpus.md');
const license=await read('LICENSES','CC-BY-SA-4.0.txt');
const generator=await read('scripts','generate_bridge_corpus.py');
const refinement=await read('scripts','refine_bridge_corpus.py');

function parseChallenge(source){
  const valid=new Set(['der','die','das']);
  const rows=[];
  for(const line of source.split(/\r?\n/)){
    const value=line.trim();
    if(!value.startsWith('["')||!value.endsWith('],')) continue;
    try{
      const row=JSON.parse(value.slice(0,-1));
      if(Array.isArray(row)&&row.length>=7&&valid.has(row[2])&&Number.isInteger(row[3])) rows.push(row);
    }catch{}
  }
  return rows;
}

const challenge=parseChallenge(html);
if(challenge.length!==1000) fail(`Expected 1000 Challenge nouns, found ${challenge.length}`);
const challengeIds=new Set(challenge.map(row=>row[0]));
const challengeNouns=new Set(challenge.map(row=>String(row[1]).toLocaleLowerCase('de-DE')));

const corpusContext={window:{}};
vm.runInNewContext(corpusSource,corpusContext,{filename:'bridge-corpus.js'});
const bridge=corpusContext.window.ARTIKELWERK_BRIDGE_CORPUS;
const meta=corpusContext.window.ARTIKELWERK_BRIDGE_CORPUS_META;
if(!Array.isArray(bridge)||bridge.length!==1000) fail(`Normal corpus must contain exactly 1000 rows; found ${bridge?.length}`);
if(meta?.count!==1000) fail('Normal corpus metadata count must be 1000.');
if(JSON.stringify(meta?.levelCounts)!==JSON.stringify({'1':400,'2':350,'3':250})) fail('Normal corpus metadata level counts are invalid.');
if(JSON.stringify(meta?.cefrEstimateCounts)!==JSON.stringify({B2:600,C1:400})) fail('Normal corpus metadata CEFR mix is invalid.');

const translationContext={window:{
  ARTIKELWERK_TRANSLATIONS:Object.freeze({}),
  ARTIKELWERK_TRANSLATION_PROVENANCE:Object.freeze({})
}};
vm.runInNewContext(translationSource,translationContext,{filename:'bridge-translations.js'});
const translations=translationContext.window.ARTIKELWERK_TRANSLATIONS||{};
const runtimeProvenance=translationContext.window.ARTIKELWERK_TRANSLATION_PROVENANCE||{};
const certification=translationContext.window.ARTIKELWERK_BRIDGE_CONTENT_CERTIFICATION||{};
if(Object.keys(translations).length!==1000) fail(`Normal translation asset must contain 1000 entries; found ${Object.keys(translations).length}`);
if(Object.keys(runtimeProvenance).length!==1000) fail('Normal runtime provenance must contain 1000 entries.');
if(certification.reviewStatus!=='source-certified'||certification.license!=='CC-BY-SA-4.0'||certification.count!==1000) fail('Normal runtime certification marker is invalid.');

const ids=new Set();
const nouns=new Set();
const levelCounts={1:0,2:0,3:0};
const cefrCounts={B2:0,C1:0};
const levelCefr={1:{B2:0,C1:0},2:{B2:0,C1:0},3:{B2:0,C1:0}};
const articleCounts={der:0,die:0,das:0};
const articleCaps={der:'Der',die:'Die',das:'Das'};
for(const row of bridge){
  if(!Array.isArray(row)||row.length<11) fail(`Normal row is missing required fields: ${JSON.stringify(row)}`);
  const [id,noun,article,level,rule,example,group,coverage,phase,track,evidence]=row;
  if(typeof id!=='string'||!/^[a-z0-9][a-z0-9-]*$/.test(id)) fail(`Invalid Normal id: ${String(id)}`);
  if(ids.has(id)) fail(`Duplicate Normal id: ${id}`);
  ids.add(id);
  const nounKey=String(noun).toLocaleLowerCase('de-DE');
  if(nouns.has(nounKey)) fail(`Duplicate Normal noun: ${noun}`);
  nouns.add(nounKey);
  if(challengeIds.has(id)||challengeNouns.has(nounKey)) fail(`Normal overlaps Challenge: ${id} / ${noun}`);
  if(!Object.hasOwn(articleCounts,article)) fail(`Invalid Normal article for ${id}: ${article}`);
  if(![1,2,3].includes(level)) fail(`Invalid Normal level for ${id}: ${level}`);
  if(track!=='bridge'||coverage!=='core-expanded'||phase!=='V2-2') fail(`Invalid Normal tuple contract for ${id}`);
  if(typeof rule!=='string'||rule.length<20) fail(`Normal article guidance is missing for ${id}`);
  if(typeof example!=='string'||!example.includes(noun)||!example.startsWith(`${articleCaps[article]} ${noun}`)) fail(`Normal example/article mismatch for ${id}: ${example}`);
  if(typeof group!=='string'||!group) fail(`Normal semantic group missing for ${id}`);
  if(!evidence||!['B2','C1'].includes(evidence.cefrEstimate)||!Number.isInteger(evidence.frequencyRank)||evidence.frequencyRank<=0||!Number.isInteger(evidence.frequencyCount)||evidence.frequencyCount<=0||evidence.genderCorroborated!==true) fail(`Normal source evidence is invalid for ${id}`);
  if(level===1&&evidence.cefrEstimate!=='B2') fail(`Normal Intermediate must be B2-estimated: ${id}`);
  if(level===3&&(evidence.cefrEstimate!=='C1'||evidence.frequencyRank<10500)) fail(`Normal Advanced source gate failed for ${id}`);
  const gloss=translations[id];
  if(typeof gloss!=='string'||!gloss.trim()||gloss.length>145) fail(`Normal gloss is missing/invalid for ${id}`);
  const runtime=runtimeProvenance[id];
  const formal=provenance.entries?.[id];
  for(const item of [runtime,formal]){
    if(item?.reviewStatus!=='source-certified'||item?.license!=='CC-BY-SA-4.0'||item?.genderCorroborated!==true) fail(`Normal provenance is incomplete for ${id}`);
    if(item?.cefrEstimate!==evidence.cefrEstimate||item?.frequencyRank!==evidence.frequencyRank) fail(`Normal provenance/evidence mismatch for ${id}`);
  }
  levelCounts[level]++;
  cefrCounts[evidence.cefrEstimate]++;
  levelCefr[level][evidence.cefrEstimate]++;
  articleCounts[article]++;
}

if(JSON.stringify(levelCounts)!==JSON.stringify({1:400,2:350,3:250})) fail(`Unexpected Normal level counts: ${JSON.stringify(levelCounts)}`);
if(JSON.stringify(cefrCounts)!==JSON.stringify({B2:600,C1:400})) fail(`Unexpected Normal CEFR-estimate counts: ${JSON.stringify(cefrCounts)}`);
if(JSON.stringify(levelCefr)!==JSON.stringify({1:{B2:400,C1:0},2:{B2:200,C1:150},3:{B2:0,C1:250}})) fail(`Unexpected Normal level/CEFR mix: ${JSON.stringify(levelCefr)}`);
if(Math.min(...Object.values(articleCounts))<100) fail(`Normal article coverage is too narrow: ${JSON.stringify(articleCounts)}`);
if(provenance.count!==1000||Object.keys(provenance.entries||{}).length!==1000||provenance.reviewStatus!=='source-certified'||provenance.license!=='CC-BY-SA-4.0') fail('Formal Normal provenance summary is invalid.');
if(report.selected!==1000||JSON.stringify(report.levelCounts)!==JSON.stringify({'1':400,'2':350,'3':250})||JSON.stringify(report.cefrEstimateCounts)!==JSON.stringify({B2:600,C1:400})) fail('Normal corpus report does not match certified counts.');
if(JSON.stringify(report.levelCefrMix)!==JSON.stringify({'1':{B2:400},'2':{B2:200,C1:150},'3':{C1:250}})) fail('Normal report level/CEFR mix is invalid.');
if(report.eligible?.eligibleTransitionC1<150||report.eligible?.eligibleAdvancedC1<250||report.eligible?.advancedMinFrequencyRank!==10500||report.eligible?.transitionMaxFrequencyRank!==14000||report.eligible?.transitionMinLearnerValue!==5) fail('Normal transition/Advanced eligibility report is incomplete.');
if(report.learnerValueRanges?.['3']?.[0]<5) fail('Normal Advanced learner-value floor is unexpectedly low.');
if(!docs.includes('targeting estimates, not official Goethe B2/C1 list membership')||!docs.includes('learner value is at least 5')||!docs.includes('formal/abstract lexical evidence')) fail('Normal methodology documentation is incomplete.');
if(!license.includes('Attribution-ShareAlike 4.0 International')) fail('CC-BY-SA-4.0 license text is missing.');
for(const fragment of [
  '83837efd46241e7226fc6daaa9d0cc81b57bf746434b8c539049c660d98ba761',
  '73075bb76c9261c44923f4909858586b261bfd83',
  'a56efcb80b64433107ec1f376b933c572f2427c9'
]) if(!generator.includes(fragment)) fail(`Normal generator integrity pin missing: ${fragment}`);
for(const fragment of [
  'ADVANCED_MIN_FREQUENCY_RANK = 10500',
  'TRANSITION_MAX_FREQUENCY_RANK = 14000',
  'TRANSITION_MIN_LEARNER_VALUE = 5',
  'formal_advanced_evidence'
]) if(!refinement.includes(fragment)) fail(`Normal learner-suitability refinement gate is missing: ${fragment}`);

console.log(`Normal certification passed: 1000 nouns, L1/L2/L3 400/350/250, B2/C1 600/400, Level 2 mix 200 B2 + 150 C1, articles der/die/das ${articleCounts.der}/${articleCounts.die}/${articleCounts.das}, zero Challenge overlap.`);
