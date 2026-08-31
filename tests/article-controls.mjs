import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { chromium } from 'playwright';

const BASE_URL=process.env.ARTIKELWERK_URL||'http://127.0.0.1:4173';
const artifactDir='test-artifacts/article-controls';
await fs.mkdir(artifactDir,{recursive:true});

const browser=await chromium.launch({headless:true});
try{
  const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
  const page=await context.newPage();
  const errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  page.on('console',message=>{ if(message.type()==='error') errors.push(message.text()); });

  await page.goto(BASE_URL,{waitUntil:'networkidle'});

  assert.equal(await page.locator('#settingsBtn').isVisible(),true,'Settings control must remain reachable on a 390 px mobile viewport');
  assert.equal(await page.locator('#practiceScreen').getAttribute('data-article-controls'),'standard','fresh installs must retain the existing Standard layout');
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true,'Settings control must not introduce horizontal page overflow');

  await page.locator('#settingsBtn').click();
  await page.locator('#settingsModal.show').waitFor({state:'visible'});
  assert.equal(await page.locator('input[name="articleControlsLayout"][value="standard"]').isChecked(),true,'Settings must show Standard as the default');

  await page.locator('input[name="articleControlsLayout"][value="bottom-bar"]').check();
  assert.equal(await page.locator('#practiceScreen').getAttribute('data-article-controls'),'bottom-bar','Bottom Bar must apply immediately');
  assert.equal(await page.evaluate(()=>localStorage.getItem('artikelwerk_article_controls')),'bottom-bar','Bottom Bar preference must persist locally');
  await page.locator('#settingsCloseBtn').click();

  await page.locator('#openPracticeBtn').click();
  await page.locator('#practiceScreen:not([hidden])').waitFor({state:'visible'});
  assert.equal(await page.locator('.answers').evaluate(el=>getComputedStyle(el).position),'fixed','Bottom Bar article controls must remain fixed to the viewport');
  const bottomBoxes=await page.locator('.answer-btn').evaluateAll(buttons=>buttons.map(button=>{
    const r=button.getBoundingClientRect();
    return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom};
  }));
  assert.equal(bottomBoxes.length,3,'Bottom Bar must expose all three article targets');
  assert.ok(bottomBoxes.every(box=>box.height>=50),'Bottom Bar article targets must remain at least 50 px tall');
  assert.ok(Math.max(...bottomBoxes.map(box=>box.y))-Math.min(...bottomBoxes.map(box=>box.y))<=2,'Bottom Bar choices must remain in one row');
  assert.ok(844-Math.max(...bottomBoxes.map(box=>box.bottom))<=20,'Bottom Bar choices must sit within thumb reach at the bottom edge');
  await page.screenshot({path:`${artifactDir}/bottom-bar-mobile.png`,fullPage:false});
  await page.locator('#closePracticeBtn').click();

  await page.reload({waitUntil:'networkidle'});
  assert.equal(await page.locator('#practiceScreen').getAttribute('data-article-controls'),'bottom-bar','Bottom Bar choice must survive reload');
  await page.locator('#settingsBtn').click();
  await page.locator('input[name="articleControlsLayout"][value="stacked"]').check();
  await page.locator('#settingsCloseBtn').click();
  await page.locator('#openPracticeBtn').click();
  await page.locator('#practiceScreen:not([hidden])').waitFor({state:'visible'});

  assert.equal(await page.locator('#practiceScreen').getAttribute('data-article-controls'),'stacked','Stacked layout must apply to practice');
  assert.equal(await page.locator('#quizContent').evaluate(el=>getComputedStyle(el).overflowY),'auto','Stacked mode must allow feedback/details to scroll rather than shrinking answer targets');
  const stackedBoxes=await page.locator('.answer-btn').evaluateAll(buttons=>buttons.map(button=>{
    const r=button.getBoundingClientRect();
    return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom};
  }));
  assert.equal(stackedBoxes.length,3,'Stacked mode must expose all three article targets');
  assert.ok(stackedBoxes.every(box=>box.height>=50),'Stacked article targets must remain at least 50 px tall');
  assert.ok(stackedBoxes.every(box=>box.width>=300),'Stacked article targets must span most of a phone width for either hand');
  assert.ok(stackedBoxes[0].y<stackedBoxes[1].y && stackedBoxes[1].y<stackedBoxes[2].y,'Stacked choices must appear as der, die, das on separate vertical rows');
  assert.ok(Math.max(...stackedBoxes.map(box=>box.x))-Math.min(...stackedBoxes.map(box=>box.x))<=2,'Stacked choices must share the same horizontal reach zone');
  await page.screenshot({path:`${artifactDir}/stacked-mobile.png`,fullPage:false});
  await page.locator('#closePracticeBtn').click();

  await page.locator('#settingsBtn').click();
  await page.locator('input[name="articleControlsLayout"][value="standard"]').check();
  await page.locator('#settingsCloseBtn').click();
  await page.locator('#openPracticeBtn').click();
  await page.locator('#practiceScreen:not([hidden])').waitFor({state:'visible'});
  assert.notEqual(await page.locator('.answers').evaluate(el=>getComputedStyle(el).position),'fixed','Standard must not inherit Bottom Bar positioning');
  const standardBoxes=await page.locator('.answer-btn').evaluateAll(buttons=>buttons.map(button=>{
    const r=button.getBoundingClientRect();
    return {x:r.x,y:r.y,width:r.width,height:r.height};
  }));
  assert.ok(Math.max(...standardBoxes.map(box=>box.y))-Math.min(...standardBoxes.map(box=>box.y))<=2,'Standard must preserve the original horizontal three-button row');
  assert.equal(await page.evaluate(()=>localStorage.getItem('artikelwerk_article_controls')),'standard','Returning to Standard must persist');

  assert.deepEqual(errors,[],'Article-control layouts emitted browser errors');
  await context.close();
  console.log('Mobile article-control layout certification passed.');
}finally{
  await browser.close();
}
