import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { chromium } from 'playwright';

const BASE_URL=process.env.ARTIKELWERK_URL||'http://127.0.0.1:4173';
const artifactDir='test-artifacts/session-completion';
await fs.mkdir(artifactDir,{recursive:true});

const source=await fs.readFile('index.html','utf8');
const validArticles=new Set(['der','die','das']);
const rows=[];
for(const line of source.split(/\r?\n/)){
  const value=line.trim();
  if(!value.startsWith('["')||!value.endsWith('],')) continue;
  try{
    const row=JSON.parse(value.slice(0,-1));
    if(Array.isArray(row)&&row.length>=7&&validArticles.has(row[2])&&Number.isInteger(row[3])) rows.push(row);
  }catch{}
}
assert.equal(rows.length,1000,'session regression test requires the 1,000-word Challenge corpus');
const byNoun=new Map(rows.map(row=>[row[1],row]));
const nouns=[...byNoun.keys()].sort((a,b)=>b.length-a.length);
const articles=['der','die','das'];

async function currentWord(page){
  const prompt=((await page.locator('#nounPrompt').textContent())||'').trim();
  const noun=nouns.find(candidate=>prompt.includes(candidate));
  assert.ok(noun,`Could not identify current noun from prompt: ${prompt}`);
  return {noun,row:byNoun.get(noun)};
}

async function prepareTwoQuestionSession(page){
  await page.goto(BASE_URL,{waitUntil:'networkidle'});
  await page.locator('#modeSelect').selectOption('practice');
  await page.locator('#formatSelect').selectOption('standard');
  await page.evaluate(()=>{
    const select=document.querySelector('#sessionSelect');
    if(!select.querySelector('option[value="2"]')) select.add(new Option('2 questions','2'));
    select.value='2';
    select.dispatchEvent(new Event('change',{bubbles:true}));
  });
  await page.locator('#openPracticeBtn').click();
  await page.locator('#practiceScreen:not([hidden])').waitFor({state:'visible'});
  assert.equal(((await page.locator('#nextBtn').textContent())||'').trim(),'Next','new session must start with Next semantics');
}

async function answerCorrect(page){
  const {noun,row}=await currentWord(page);
  await page.locator(`.answer-btn[data-article="${row[2]}"]`).click();
  await page.locator('#feedback.show').waitFor({state:'visible'});
  return {noun,row};
}

async function answerWrongThenCorrect(page){
  const {noun,row}=await currentWord(page);
  const wrong=articles.find(article=>article!==row[2]);
  await page.locator(`.answer-btn[data-article="${wrong}"]`).click();
  await page.locator('#feedback.show').waitFor({state:'visible'});
  assert.equal(await page.locator('#nextBtn').isDisabled(),true,'a miss must require active correction before advancing');
  await page.locator(`.answer-btn[data-article="${row[2]}"]`).click();
  assert.equal(await page.locator('#nextBtn').isEnabled(),true,'corrective answer must re-enable the action');
  return {noun,row};
}

async function assertFinished(page,label){
  await page.locator('#nextBtn').click();
  await page.locator('#practiceScreen').waitFor({state:'hidden'});
  await page.locator('#summaryModal.show').waitFor({state:'visible'});
  assert.equal(await page.evaluate(()=>document.body.classList.contains('practice-open')),false,`${label}: Practice body lock remained after Finish`);
  assert.equal(await page.locator('#summaryTitle').textContent(),'Session complete',`${label}: summary did not open after Finish`);
}

async function runResolvedRetry(browser){
  const context=await browser.newContext({viewport:{width:1280,height:800}});
  const page=await context.newPage();
  const errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  page.on('console',message=>{if(message.type()==='error') errors.push(message.text());});
  await prepareTwoQuestionSession(page);

  const first=await answerWrongThenCorrect(page);
  assert.equal(((await page.locator('#nextBtn').textContent())||'').trim(),'Next','a queued delayed retry must keep Next semantics');
  await page.locator('#nextBtn').click();

  const second=await answerCorrect(page);
  assert.notEqual(second.noun,first.noun,'normal scored questions should not immediately repeat the missed noun');
  assert.equal(((await page.locator('#nextBtn').textContent())||'').trim(),'Next','pending reinforcement must prevent premature Finish');
  await page.locator('#nextBtn').click();

  assert.equal(((await page.locator('#questionCounter').textContent())||'').trim(),'Reinforcement','delayed retry was not presented');
  const retry=await currentWord(page);
  assert.equal(retry.noun,first.noun,'delayed retry must target the missed noun');
  await answerCorrect(page);

  assert.equal(((await page.locator('#nextBtn').textContent())||'').trim(),'Finish','a recovered delayed retry should resolve the session without a redundant final check');
  assert.equal(await page.locator('#nextBtn').getAttribute('aria-label'),'Finish session','Finish action must expose terminal semantics');
  await page.screenshot({path:`${artifactDir}/resolved-retry-finish.png`,fullPage:false});
  await assertFinished(page,'resolved retry');
  assert.match(((await page.locator('#summarySubtitle').textContent())||''),/1 reinforcement check/i,'resolved retry summary should record exactly one reinforcement check');
  assert.deepEqual(errors,[],'resolved-retry scenario emitted browser errors');
  await context.close();
}

async function runUnresolvedRetry(browser){
  const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
  const page=await context.newPage();
  const errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  page.on('console',message=>{if(message.type()==='error') errors.push(message.text());});
  await prepareTwoQuestionSession(page);

  const first=await answerWrongThenCorrect(page);
  await page.locator('#nextBtn').click();
  await answerCorrect(page);
  await page.locator('#nextBtn').click();

  assert.equal(((await page.locator('#questionCounter').textContent())||'').trim(),'Reinforcement','expected delayed retry before final check');
  const retry=await currentWord(page);
  assert.equal(retry.noun,first.noun,'reinforcement noun mismatch');
  const wrong=articles.find(article=>article!==retry.row[2]);
  await page.locator(`.answer-btn[data-article="${wrong}"]`).click();
  await page.locator('#feedback.show').waitFor({state:'visible'});
  assert.equal(await page.locator('#nextBtn').isDisabled(),true,'failed reinforcement must require correction');
  await page.locator(`.answer-btn[data-article="${retry.row[2]}"]`).click();
  assert.equal(((await page.locator('#nextBtn').textContent())||'').trim(),'Next','failed reinforcement must remain unresolved for one final check');
  await page.locator('#nextBtn').click();

  assert.match(((await page.locator('#questionCounter').textContent())||''),/^Final 1 \/ 1$/,'unresolved miss should receive exactly one final check');
  const finalCheck=await currentWord(page);
  assert.equal(finalCheck.noun,first.noun,'final check should target the unresolved missed noun');
  await page.locator(`.answer-btn[data-article="${finalCheck.row[2]}"]`).click();
  await page.locator('#feedback.show').waitFor({state:'visible'});
  assert.equal(((await page.locator('#nextBtn').textContent())||'').trim(),'Finish','last final check must expose Finish instead of dead-end Next');
  await page.screenshot({path:`${artifactDir}/final-check-finish-mobile.png`,fullPage:false});
  await assertFinished(page,'unresolved retry');
  assert.match(((await page.locator('#summarySubtitle').textContent())||''),/2 reinforcement checks/i,'summary should record delayed retry plus final check');
  assert.deepEqual(errors,[],'unresolved-retry scenario emitted browser errors');
  await context.close();
}

const browser=await chromium.launch({headless:true});
try{
  await runResolvedRetry(browser);
  await runUnresolvedRetry(browser);
  console.log('Session completion and bounded-repeat regression passed.');
}finally{
  await browser.close();
}
