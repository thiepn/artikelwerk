import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { chromium } from 'playwright';
const BASE_URL=process.env.ARTIKELWERK_URL||'http://127.0.0.1:4173';
const baseOrigin=new URL(BASE_URL).origin;
const profiles=[
  {name:'small-phone',width:360,height:640,isMobile:true,hasTouch:true},
  {name:'modern-phone',width:390,height:844,isMobile:true,hasTouch:true},
  {name:'large-android',width:412,height:915,isMobile:true,hasTouch:true},
  {name:'phone-landscape',width:844,height:390,isMobile:true,hasTouch:true},
  {name:'tablet',width:768,height:1024,isMobile:true,hasTouch:true},
  {name:'desktop',width:1440,height:900,isMobile:false,hasTouch:false},
];
const checks=[
  ['Handlungsansatz','der Handlungsansatz','approach to action'],
  ['Kompetenzprofil','das Kompetenzprofil','competency profile'],
  ['Bewertungsansatz','der Bewertungsansatz','evaluation approach'],
  ['Interpretationsansatz','der Interpretationsansatz','interpretive approach'],
  ['Deutungsansatz','der Deutungsansatz','interpretive approach'],
  ['Analyseansatz','der Analyseansatz','analytical approach'],
  ['Forschungsansatz','der Forschungsansatz','research approach'],
  ['Primat','der/das Primat','both der Primat and das Primat'],
  ['Dossier','das Dossier','obsolete'],
  ['Erbe','das/der Erbe','inheritance; legacy'],
  ['Mangel','der/die Mangel','laundry mangle'],
  ['Hinweis','der Hinweis','Hinweises'],
];
await fs.mkdir('test-artifacts',{recursive:true});
const browser=await chromium.launch({headless:true});
try{for(const profile of profiles){const context=await browser.newContext({viewport:{width:profile.width,height:profile.height},isMobile:profile.isMobile,hasTouch:profile.hasTouch});const page=await context.newPage();const errors=[];const external=[];page.on('pageerror',error=>errors.push(error.message));page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});page.on('request',request=>{const url=request.url();if(url.startsWith('data:')||url.startsWith('blob:'))return;try{if(new URL(url).origin!==baseOrigin)external.push(url);}catch{external.push(url);}});await page.goto(BASE_URL,{waitUntil:'networkidle'});await page.locator('#tabLibrary').click();await page.locator('#libraryView.active').waitFor({state:'visible'});for(const [query,titlePart,detailPart] of checks){await page.locator('#librarySearch').fill(query);const row=page.locator('#libraryBody tr').first();await row.waitFor({state:'visible'});assert.match((await row.textContent())||'',new RegExp(query,'i'),`${profile.name}: vocabulary row missing ${query}`);await row.locator('.library-details-btn').click();await page.locator('#wordDetailModal[aria-hidden="false"]').waitFor({state:'visible'});const title=(await page.locator('#wordDetailTitle').textContent())||'';const detail=(await page.locator('#wordDetailContent').textContent())||'';assert.ok(title.includes(titlePart),`${profile.name}: title mismatch for ${query}: ${title}`);assert.ok(detail.includes(detailPart),`${profile.name}: detail mismatch for ${query}: expected ${detailPart}`);assert.ok(detail.includes('Reviewed'),`${profile.name}: certification label missing for ${query}`);assert.ok(!detail.includes('English gloss unavailable'),`${profile.name}: unavailable gloss rendered for ${query}`);await page.locator('#wordDetailCloseBtn').click();await page.locator('#wordDetailModal[aria-hidden="true"]').waitFor({state:'attached'});}await page.locator('#tabPractice').click();await page.locator('#openPracticeBtn').click();await page.locator('#practiceScreen').waitFor({state:'visible'});await page.locator('.answer-btn').first().click();await page.locator('#translationHint.show').waitFor({state:'visible'});const translation=((await page.locator('#translationText').textContent())||'').trim();assert.ok(translation&&translation!=='English gloss unavailable',`${profile.name}: practice did not render a certified translation`);assert.equal((await page.locator('#translationLabel').textContent())?.trim(),'English',`${profile.name}: translation is still marked as a fallback cue`);const shell=await page.locator('#practiceScreen').boundingBox();assert.ok(shell&&shell.x>=-1&&shell.y>=-1&&shell.x+shell.width<=profile.width+1&&shell.y+shell.height<=profile.height+1,`${profile.name}: practice viewport overflow`);await page.screenshot({path:`test-artifacts/content-${profile.name}-${profile.width}x${profile.height}.png`,fullPage:false});assert.deepEqual(external,[],`${profile.name}: external runtime requests: ${external.join(', ')}`);assert.deepEqual(errors,[],`${profile.name}: browser errors: ${errors.join(' | ')}`);await context.close();}}finally{await browser.close();}
console.log('Content runtime device-matrix verification passed.');
