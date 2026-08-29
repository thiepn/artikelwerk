import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { chromium } from 'playwright';

const BASE_URL=process.env.ARTIKELWERK_URL||'http://127.0.0.1:4173';
const artifactDir='test-artifacts/v2-1';
await fs.mkdir(artifactDir,{recursive:true});
const optionDisabled=(page,selector)=>page.locator(selector).evaluate(option=>option.disabled===true);

const source=await fs.readFile('index.html','utf8');
assert.match(source,/const VOCABULARY_TRACKS = Object\.freeze/,'track registry missing');
assert.match(source,/track:track==="bridge"\?"bridge":"challenge"/,'vocabulary rows are not track-aware');
assert.match(source,/const SCHEMA_VERSION = 10;/,'progress schema was not upgraded for track aggregates');
assert.match(source,/aggregatesByTrack/,'per-track aggregate storage missing');
assert.match(source,/Bridge · B2–C1/,'Bridge UX contract missing');

const browser=await chromium.launch({headless:true});
try{
  for(const profile of [
    {name:'desktop',width:1440,height:900,mobile:false,touch:false},
    {name:'mobile',width:390,height:844,mobile:true,touch:true},
  ]){
    const context=await browser.newContext({viewport:{width:profile.width,height:profile.height},isMobile:profile.mobile,hasTouch:profile.touch});
    const page=await context.newPage();
    const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
    await page.goto(BASE_URL,{waitUntil:'networkidle'});

    assert.equal(await page.locator('#vocabularyTrackSelect').inputValue(),'challenge',`${profile.name}: Challenge is not the default track`);
    assert.equal(await optionDisabled(page,'#vocabularyTrackSelect option[value="bridge"]'),false,`${profile.name}: installed Bridge option should be enabled`);
    assert.equal(await page.locator('#bridgeTrackBtn').isDisabled(),false,`${profile.name}: installed Bridge CTA should be enabled`);
    assert.match((await page.locator('#practiceTrackKicker').textContent())||'',/Challenge.*C1.*C2/i,`${profile.name}: Challenge identity missing from Practice`);
    assert.match((await page.locator('#bridgeTrackNote').textContent())||'',/1,000.*ready|1,000.*intermediate/i,`${profile.name}: installed Bridge readiness note missing`);

    const difficulty=await page.locator('#difficultySelect option').allTextContents();
    assert.deepEqual(difficulty,['All advanced levels','Level 1 — Advanced','Level 2 — Difficult','Level 3 — Very Difficult'],`${profile.name}: Challenge difficulty labels changed`);

    await page.locator('#openPracticeBtn').click();
    await page.locator('#practiceScreen:not([hidden])').waitFor({state:'visible'});
    assert.equal(((await page.locator('#practiceScreenTitle').textContent())||'').trim(),'Challenge practice',`${profile.name}: Practice title does not identify Challenge`);
    assert.ok(((await page.locator('#nounPrompt').textContent())||'').trim().length>3,`${profile.name}: Challenge session has no noun`);
    await page.locator('.answer-btn').first().click();
    await page.locator('#feedback.show').waitFor({state:'visible'});

    const state=await page.evaluate(()=>JSON.parse(localStorage.getItem('artikelwerk_data')));
    assert.equal(state.schemaVersion,10,`${profile.name}: persisted schema is not v10`);
    assert.equal(state.settings.vocabularyTrack,'challenge',`${profile.name}: selected track was not persisted`);
    assert.equal(state.aggregatesByTrack.challenge.answers,1,`${profile.name}: Challenge aggregate did not receive the answer`);
    assert.equal(state.aggregatesByTrack.bridge.answers,0,`${profile.name}: Bridge aggregate was contaminated by Challenge practice`);
    assert.equal(state.aggregates.answers,1,`${profile.name}: global aggregate changed semantics`);
    await page.keyboard.press('Escape');

    await page.locator('#tabStats').click();
    assert.equal(await page.locator('#progressTrackSelect').inputValue(),'current',`${profile.name}: Progress should follow current track by default`);
    assert.equal(await optionDisabled(page,'#progressTrackSelect option[value="bridge"]'),false,`${profile.name}: installed Bridge Progress scope should be enabled`);
    assert.match((await page.locator('#progressTrackMeta').textContent())||'',/Challenge.*1,000/i,`${profile.name}: Progress scope metadata is wrong`);
    assert.equal(((await page.locator('#statTotal').textContent())||'').trim(),'1',`${profile.name}: Challenge total answers did not remain isolated`);
    await page.locator('#progressTrackSelect').selectOption('all');
    assert.match((await page.locator('#progressTrackMeta').textContent())||'',/All vocabulary.*2,000/i,`${profile.name}: All Progress scope metadata is wrong`);

    await page.locator('#tabLibrary').click();
    assert.equal(await page.locator('#libraryTrackSelect').inputValue(),'current',`${profile.name}: Vocabulary should follow current track by default`);
    assert.equal(await optionDisabled(page,'#libraryTrackSelect option[value="bridge"]'),false,`${profile.name}: installed Bridge library scope should be enabled`);
    assert.match((await page.locator('#libraryMeta').textContent())||'',/1000 of 1000 nouns.*Challenge/i,`${profile.name}: Challenge library count changed`);
    await page.locator('.word-open-btn').first().click();
    await page.locator('#wordDetailModal.show').waitFor({state:'visible'});
    const setField=page.locator('#wordDetailContent .detail-field').filter({has:page.locator('strong', {hasText:'Set'})}).first();
    assert.equal(await setField.count(),1,`${profile.name}: word detail Set field is missing`);
    assert.match((await setField.locator('span').textContent())||'',/Challenge.*C1.*C2/i,`${profile.name}: word detail does not expose Challenge · C1–C2 set`);
    await page.keyboard.press('Escape');
    await page.locator('#libraryTrackSelect').selectOption('all');
    await page.locator('#libraryTrackSelect').dispatchEvent('change');
    assert.match((await page.locator('#libraryMeta').textContent())||'',/2000 of 2000 nouns.*All vocabulary/i,`${profile.name}: All library scope is wrong`);

    if(profile.name==='desktop'){
      const legacy=structuredClone(state);
      legacy.schemaVersion=9;
      delete legacy.aggregatesByTrack;
      legacy.aggregates={answers:7,correct:5,currentStreak:2,bestStreak:4};
      legacy.settings={};
      await page.evaluate(payload=>{
        localStorage.setItem('artikelwerk_data',JSON.stringify(payload));
        localStorage.removeItem('artikelwerk_data_tmp');
      },legacy);
      await page.reload({waitUntil:'networkidle'});
      const migrated=await page.evaluate(()=>JSON.parse(localStorage.getItem('artikelwerk_data')));
      assert.equal(migrated.schemaVersion,10,'desktop: v9 state did not migrate to v10');
      assert.equal(migrated.settings.vocabularyTrack,'challenge','desktop: migration did not default to Challenge');
      assert.equal(migrated.aggregatesByTrack.challenge.answers,7,'desktop: historical answers were not assigned to Challenge');
      assert.equal(migrated.aggregatesByTrack.challenge.bestStreak,4,'desktop: historical best streak was not preserved');
      assert.equal(migrated.aggregatesByTrack.bridge.answers,0,'desktop: migration invented Bridge progress');
    }

    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
    assert.ok(overflow<=1,`${profile.name}: V2-1 introduced ${overflow}px horizontal overflow`);
    await page.screenshot({path:`${artifactDir}/${profile.name}-tracks.png`,fullPage:true});
    assert.deepEqual(errors,[],`${profile.name}: browser errors: ${errors.join(' | ')}`);
    await context.close();
  }
}finally{
  await browser.close();
}
console.log('V2-1 vocabulary track architecture tests passed.');
