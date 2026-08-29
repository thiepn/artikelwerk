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
if(!Array.isArray(bridge)||bridge.length!==1000) fail(`Bridge corpus must contain exactly 1000 rows; found ${bridge?.length}`);
if(meta?.count!==1000) fail('Bridge corpus metadata count must be 1000.');

const translationContext={window:{
  ARTIKELWERK_TRANSLATIONS:Object.freeze({}),
  ARTIKELWERK_TRANSLATION_PROVENANCE:Object.freeze({})
}};
vm.runInNewContext(translationSource,translationContext,{filename:'bridge-translations.js'});
const translations=translationContext.window.ARTIKELWERK_TRANSLATIONS||{};
const runtimeProvenance=translationContext.window.ARTIKELWERK_TRANSLATION_PROVENANCE||{};
const certification=translationContext.window.ARTIKELWERK_BRIDGE_CONTENT_CERTIFICATION||{};
if(Object.keys(translations).length!==1000) fail(`Bridge translation asset must contain 1000 entries; found ${Object.keys(translations).length}`);
if(Object.keys(runtimeProvenance).length!==1000) fail('Bridge runtime provenance must contain 1000 entries.');
if(certification.reviewStatus!=='source-certified'||certification.license!=='CC-BY-SA-4.0'||certification.count!==1000) fail('Bridge runtime certification marker is invalid.');

const ids=new Set();
const nouns=new Set();
const levelCounts={1:0,2:0,3:0};
const cefrCounts={B2:0,C1:0};
const articleCounts={der:0,die:0,das:0};
const articleCaps={der:'Der',die:'Die',das:'Das'};
for(const row of bridge){
  if(!Array.isArray(row)||row.length<11) fail(`Bridge row is missing required fields: ${JSON.stringify(row)}`);
  const [id,noun,article,level,rule,example,group,coverage,phase,track,evidence]=row;
  if(typeof id!=='string'||!/^[a-z0-9][a-z0-9-]*$/.test(id)) fail(`Invalid Bridge id: ${String(id)}`);
  if(ids.has(id)) fail(`Duplicate Bridge id: ${id}`);
  ids.add(id);
  const nounKey=String(noun).toLocaleLowerCase('de-DE');
  if(nouns.has(nounKey)) fail(`Duplicate Bridge noun: ${noun}`);
  nouns.add(nounKey);
  if(challengeIds.has(id)||challengeNouns.has(nounKey)) fail(`Bridge overlaps Challenge: ${id} / ${noun}`);
  if(!Object.hasOwn(articleCounts,article)) fail(`Invalid Bridge article for ${id}: ${article}`);
  if(![1,2,3].includes(level)) fail(`Invalid Bridge level for ${id}: ${level}`);
  if(track!=='bridge'||coverage!=='core-expanded'||phase!=='V2-2') fail(`Invalid Bridge tuple contract for ${id}`);
  if(typeof rule!=='string'||rule.length<20) fail(`Bridge article guidance is missing for ${id}`);
  if(typeof example!=='string'||!example.includes(noun)||!example.startsWith(`${articleCaps[article]} ${noun}`)) fail(`Bridge example/article mismatch for ${id}: ${example}`);
  if(typeof group!=='string'||!group) fail(`Bridge semantic group missing for ${id}`);
  if(!evidence||!['B2','C1'].includes(evidence.cefrEstimate)||!Number.isInteger(evidence.frequencyRank)||evidence.frequencyRank<=0||!Number.isInteger(evidence.frequencyCount)||evidence.frequencyCount<=0||evidence.genderCorroborated!==true) fail(`Bridge source evidence is invalid for ${id}`);
  if(level<3&&evidence.cefrEstimate!=='B2') fail(`Bridge Level ${level} must be B2-estimated: ${id}`);
  if(level===3&&(evidence.cefrEstimate!=='C1'||evidence.frequencyRank<10500)) fail(`Bridge Advanced source gate failed for ${id}`);
  const gloss=translations[id];
  if(typeof gloss!=='string'||!gloss.trim()||gloss.length>145) fail(`Bridge gloss is missing/invalid for ${id}`);
  const runtime=runtimeProvenance[id];
  const formal=provenance.entries?.[id];
  for(const item of [runtime,formal]){
    if(item?.reviewStatus!=='source-certified'||item?.license!=='CC-BY-SA-4.0'||item?.genderCorroborated!==true) fail(`Bridge provenance is incomplete for ${id}`);
    if(item?.cefrEstimate!==evidence.cefrEstimate||item?.frequencyRank!==evidence.frequencyRank) fail(`Bridge provenance/evidence mismatch for ${id}`);
  }
  levelCounts[level]++;
  cefrCounts[evidence.cefrEstimate]++;
  articleCounts[article]++;
}

if(JSON.stringify(levelCounts)!==JSON.stringify({1:400,2:350,3:250})) fail(`Unexpected Bridge level counts: ${JSON.stringify(levelCounts)}`);
if(JSON.stringify(cefrCounts)!==JSON.stringify({B2:750,C1:250})) fail(`Unexpected Bridge CEFR-estimate counts: ${JSON.stringify(cefrCounts)}`);
if(Math.min(...Object.values(articleCounts))<120) fail(`Bridge article balance is too narrow: ${JSON.stringify(articleCounts)}`);
if(provenance.count!==1000||Object.keys(provenance.entries||{}).length!==1000||provenance.reviewStatus!=='source-certified'||provenance.license!=='CC-BY-SA-4.0') fail('Formal Bridge provenance summary is invalid.');
if(report.selected!==1000||JSON.stringify(report.levelCounts)!==JSON.stringify({'1':400,'2':350,'3':250})||JSON.stringify(report.cefrEstimateCounts)!==JSON.stringify({B2:750,C1:250})) fail('Bridge corpus report does not match certified counts.');
if(report.eligible?.eligibleAdvancedC1<250||report.eligible?.advancedMinFrequencyRank!==10500) fail('Bridge Advanced eligibility report is incomplete.');
if(!docs.includes('targeting estimates, not official Goethe B2/C1 list membership')||!docs.includes('formal lexical evidence')) fail('Bridge methodology documentation is incomplete.');
if(!license.includes('Attribution-ShareAlike 4.0 International')) fail('CC-BY-SA-4.0 license text is missing.');
for(const fragment of [
  '83837efd46241e7226fc6daaa9d0cc81b57bf746434b8c539049c660d98ba761',
  '73075bb76c9261c44923f4909858586b261bfd83',
  'a56efcb80b64433107ec1f376b933c572f2427c9'
]) if(!generator.includes(fragment)) fail(`Bridge generator integrity pin missing: ${fragment}`);
if(!refinement.includes('ADVANCED_MIN_FREQUENCY_RANK = 10500')||!refinement.includes('formal_advanced_evidence')) fail('Bridge learner-suitability refinement gate is missing.');

console.log(`Bridge certification passed: 1000 nouns, L1/L2/L3 400/350/250, B2/C1 750/250, articles der/die/das ${articleCounts.der}/${articleCounts.die}/${articleCounts.das}, zero Challenge overlap.`);
