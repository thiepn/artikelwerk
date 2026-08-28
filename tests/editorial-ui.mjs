import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
const baseURL=process.env.ARTIKELWERK_URL||'http://127.0.0.1:4173';
const evidenceDir='test-artifacts/ui5';
await mkdir(evidenceDir,{recursive:true});
const assert=(c,m)=>{if(!c)throw new Error(m);};
const browser=await chromium.launch({headless:true});
for(const p of [{name:'desktop',width:1440,height:900,mobile:false,touch:false},{name:'mobile',width:390,height:844,mobile:true,touch:true}]){
 const context=await browser.newContext({viewport:{width:p.width,height:p.height},isMobile:p.mobile,hasTouch:p.touch});
 const page=await context.newPage(); const errors=[]; page.on('pageerror',e=>errors.push(e.message)); page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.goto(baseURL,{waitUntil:'networkidle'});
 const vars=await page.evaluate(()=>{const r=getComputedStyle(document.documentElement);return{accent:r.getPropertyValue('--accent').trim(),bg:r.getPropertyValue('--bg').trim(),radius:r.getPropertyValue('--radius').trim()};});
 assert(vars.accent==='#d45532',`${p.name}: accent ${vars.accent}`); assert(vars.bg==='#f7f4ee',`${p.name}: bg ${vars.bg}`); assert(vars.radius==='6px',`${p.name}: radius ${vars.radius}`);
 const hero=await page.locator('.practice-hero').evaluate(el=>{const s=getComputedStyle(el);return{radius:s.borderRadius,shadow:s.boxShadow};}); assert(parseFloat(hero.radius)===0,`${p.name}: hero rounded`); assert(hero.shadow==='none',`${p.name}: hero shadow`);
 assert(await page.locator('.practice-hero-articles').isHidden(),`${p.name}: article trio visible`);
 const queue=await page.locator('.queue-stat').first().evaluate(el=>parseFloat(getComputedStyle(el).borderRadius)); assert(queue===0,`${p.name}: queue stat rounded`);
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth); assert(overflow<=1,`${p.name}: overflow ${overflow}`);
 await page.screenshot({path:`${evidenceDir}/${p.name}-landing.png`,fullPage:true});
 await page.locator('#openPracticeBtn').click(); await page.locator('#practiceScreen:not([hidden])').waitFor({state:'visible'});
 const quiz=await page.locator('#quizCard').evaluate(el=>{const s=getComputedStyle(el);return{radius:s.borderRadius,shadow:s.boxShadow};}); assert(parseFloat(quiz.radius)===0,`${p.name}: quiz rounded`); assert(quiz.shadow==='none',`${p.name}: quiz shadow`);
 const nounFont=await page.locator('#nounPrompt').evaluate(el=>getComputedStyle(el).fontFamily); assert(/Georgia|Palatino|Iowan/i.test(nounFont),`${p.name}: noun font ${nounFont}`);
 const cr=await page.locator('.confidence-btn').first().evaluate(el=>parseFloat(getComputedStyle(el).borderRadius)); assert(cr===0,`${p.name}: confidence pill`);
 await page.screenshot({path:`${evidenceDir}/${p.name}-practice.png`,fullPage:false}); await page.keyboard.press('Escape');
 await page.locator('#tabStats').click(); const sec=await page.locator('#statsView .panel.section').first().evaluate(el=>{const s=getComputedStyle(el);return{radius:s.borderRadius,shadow:s.boxShadow};}); assert(parseFloat(sec.radius)===0&&sec.shadow==='none',`${p.name}: progress cards remain`); await page.screenshot({path:`${evidenceDir}/${p.name}-progress.png`,fullPage:true});
 await page.locator('#tabLibrary').click(); const chip=await page.locator('.article-chip').first().evaluate(el=>{const s=getComputedStyle(el);return{radius:s.borderRadius,border:s.borderTopWidth};}); assert(parseFloat(chip.radius)===0&&parseFloat(chip.border)===0,`${p.name}: article chip remains`); await page.screenshot({path:`${evidenceDir}/${p.name}-vocabulary.png`,fullPage:true});
 assert(errors.length===0,`${p.name}: browser errors ${errors.join(' | ')}`); await context.close();
}
await browser.close(); console.log('UI5 editorial interface certification passed.');
