import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import { chromium } from 'playwright';

const BASE_URL=process.env.ARTIKELWERK_URL||'http://127.0.0.1:4173';
const artifactDir='test-artifacts/v2-2';
await fs.mkdir(artifactDir,{recursive:true});

const corpusSource=await fs.readFile('bridge-corpus.js','utf8');
const corpusContext={window:{}};
vm.runInNewContext(corpusSource,corpusContext,{filename:'bridge-corpus.js'});
const bridgeRows=corpusContext.window.ARTIKELWERK_BRIDGE_CORPUS;
assert.equal(bridgeRows.length,1000,'Bridge browser test requires exactly 1000 corpus rows');
const bridgeNouns=new Set(bridgeRows.map(row=>row[1]));
const bridgeByNoun=new Map(bridgeRows.map(row=>[row[1],row]));

const optionDisabled=(page,selector)=>page.locator(selector).evaluate(option=>option.disabled===true);
const text=async locator=>((await locator.textContent())||'').trim();

const browser=await chromium.launch({headless:true});
try{
  for(const profile of [
    {name:'desktop',width:1440,height:900,mobile:false,touch:false},
    {name:'mobile',width:390,height:844,mobile:true,touch:true},
  ]){
    const context=await browser.newContext({viewport:{width:profile.width,height:profile.height},isMobile:profile.mobile,hasTouch:profile.touch});
    const page=await context.newPage();
    const errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
    await page.goto(BASE_URL,{waitUntil:'networkidle'});

    assert.equal(await page.locator('#vocabularyTrackSelect').inputValue(),'challenge',`${profile.name}: Challenge must remain the default track`);
    assert.equal(await optionDisabled(page,'#vocabularyTrackSelect option[value="bridge"]'),false,`${profile.name}: installed Bridge Practice option is disabled`);
    assert.equal(await page.locator('#bridgeTrackBtn').isDisabled(),false,`${profile.name}: installed Bridge CTA is disabled`);
    assert.match(await text(page.locator('#bridgeTrackNote')),/1,000.*ready|1,000.*intermediate/i,`${profile.name}: Bridge readiness copy does not report the installed corpus`);

    await page.locator('#vocabularyTrackSelect').selectOption('bridge');
    await page.locator('#vocabularyTrackSelect').dispatchEvent('change');
    assert.equal(await page.locator('#vocabularyTrackSelect').inputValue(),'bridge',`${profile.name}: Bridge selection did not stick`);
    const stateAfterSelect=await page.evaluate(()=>JSON.parse(localStorage.getItem('artikelwerk_data')));
    assert.equal(stateAfterSelect.settings.vocabularyTrack,'bridge',`${profile.name}: Bridge selection was not persisted`);
    assert.deepEqual(await page.locator('#difficultySelect option').allTextContents(),[
      'All B2–C1 levels','Level 1 — Intermediate','Level 2 — Upper Intermediate','Level 3 — Advanced'
    ],`${profile.name}: Bridge difficulty labels are wrong`);

    await page.locator('#openPracticeBtn').click();
    await page.locator('#practiceScreen:not([hidden])').waitFor({state:'visible'});
    assert.equal(await text(page.locator('#practiceScreenTitle')),'Bridge practice',`${profile.name}: Practice does not identify Bridge`);
    const promptText=await text(page.locator('#nounPrompt'));
    const noun=[...bridgeNouns].find(candidate=>promptText.includes(candidate));
    assert.ok(noun,`${profile.name}: Practice prompt is not a Bridge noun: ${promptText}`);
    const row=bridgeByNoun.get(noun);
    assert.ok(row,`${profile.name}: could not recover Bridge row for ${noun}`);

    await page.locator('#showTranslationBtn').click();
    await page.locator('#translationHint.show').waitFor({state:'visible'});
    const meaning=await text(page.locator('#translationText'));
    assert.ok(meaning && !/unavailable/i.test(meaning),`${profile.name}: Bridge noun has no local English meaning`);
    assert.equal(await text(page.locator('#translationLabel')),'English',`${profile.name}: Bridge meaning is treated as fallback/unavailable`);

    const correctButton=page.locator(`.answer-btn[data-article="${row[2]}"]`);
    await correctButton.click();
    await page.locator('#feedback.show').waitFor({state:'visible'});
    const stateAfterAnswer=await page.evaluate(()=>JSON.parse(localStorage.getItem('artikelwerk_data')));
    assert.equal(stateAfterAnswer.aggregates.answers,1,`${profile.name}: global aggregate did not record Bridge answer`);
    assert.equal(stateAfterAnswer.aggregatesByTrack.bridge.answers,1,`${profile.name}: Bridge aggregate did not record answer`);
    assert.equal(stateAfterAnswer.aggregatesByTrack.challenge.answers,0,`${profile.name}: Bridge answer contaminated Challenge aggregate`);
    await page.keyboard.press('Escape');

    await page.locator('#tabStats').click();
    assert.equal(await optionDisabled(page,'#progressTrackSelect option[value="bridge"]'),false,`${profile.name}: Bridge Progress option is disabled`);
    await page.locator('#progressTrackSelect').selectOption('bridge');
    await page.locator('#progressTrackSelect').dispatchEvent('change');
    assert.match(await text(page.locator('#progressTrackMeta')),/Bridge.*1,000/i,`${profile.name}: Bridge Progress metadata is wrong`);
    assert.equal(await text(page.locator('#statTotal')),'1',`${profile.name}: Bridge Progress total is not isolated`);
    await page.locator('#progressTrackSelect').selectOption('all');
    await page.locator('#progressTrackSelect').dispatchEvent('change');
    assert.match(await text(page.locator('#progressTrackMeta')),/All vocabulary.*2,000/i,`${profile.name}: combined Progress scope is not 2,000 nouns`);

    await page.locator('#tabLibrary').click();
    assert.equal(await optionDisabled(page,'#libraryTrackSelect option[value="bridge"]'),false,`${profile.name}: Bridge Vocabulary option is disabled`);
    await page.locator('#libraryTrackSelect').selectOption('bridge');
    await page.locator('#libraryTrackSelect').dispatchEvent('change');
    assert.match(await text(page.locator('#libraryMeta')),/1000 of 1000 nouns.*Bridge/i,`${profile.name}: Bridge Vocabulary count is wrong`);
    await page.locator('.word-open-btn').first().click();
    await page.locator('#wordDetailModal.show').waitFor({state:'visible'});
    const setField=page.locator('#wordDetailContent .detail-field').filter({has:page.locator('strong',{hasText:'Set'})}).first();
    assert.equal(await setField.count(),1,`${profile.name}: Bridge word detail Set field is missing`);
    assert.match(await text(setField.locator('span')),/Bridge.*B2.*C1/i,`${profile.name}: Bridge word detail set label is wrong`);
    assert.match(await text(page.locator('#wordDetailContent')),/English/i,`${profile.name}: Bridge word detail does not expose English content`);
    await page.keyboard.press('Escape');
    await page.locator('#libraryTrackSelect').selectOption('all');
    await page.locator('#libraryTrackSelect').dispatchEvent('change');
    assert.match(await text(page.locator('#libraryMeta')),/2000 of 2000 nouns.*All vocabulary/i,`${profile.name}: combined Vocabulary scope is not 2,000 nouns`);

    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
    assert.ok(overflow<=1,`${profile.name}: V2-2 introduced ${overflow}px horizontal overflow`);
    await page.screenshot({path:`${artifactDir}/${profile.name}-bridge.png`,fullPage:true});
    assert.deepEqual(errors,[],`${profile.name}: browser errors: ${errors.join(' | ')}`);
    await context.close();
  }
}finally{
  await browser.close();
}

console.log('V2-2 Bridge runtime certification passed on desktop and mobile.');
