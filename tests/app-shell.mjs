import assert from "node:assert/strict";
import fs from "node:fs/promises";
import { chromium } from "playwright";

const BASE_URL=process.env.ARTIKELWERK_URL||"http://127.0.0.1:4173";
await fs.mkdir("test-artifacts",{recursive:true});

async function noHorizontalOverflow(page,label){
  const size=await page.evaluate(()=>({scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth}));
  assert.ok(size.scrollWidth<=size.clientWidth+1,`${label}: horizontal overflow ${size.scrollWidth} > ${size.clientWidth}`);
}

async function desktop(browser){
  const context=await browser.newContext({viewport:{width:1440,height:900}});
  const page=await context.newPage();
  const errors=[];
  page.on("pageerror",e=>errors.push(e.message));
  page.on("console",m=>{if(m.type()==="error") errors.push(m.text());});
  await page.goto(BASE_URL,{waitUntil:"networkidle"});
  assert.equal(await page.locator(".app-header .app-nav").count(),1,"desktop nav must live inside app header");
  assert.equal(await page.locator(".app-nav .tab").count(),3,"desktop shell must expose three primary destinations");
  const header=await page.locator(".app-header").boundingBox();
  const hero=await page.locator(".practice-hero").boundingBox();
  const support=await page.locator(".practice-support-grid").boundingBox();
  assert.ok(header&&hero&&support,"desktop shell boxes unavailable");
  assert.ok(hero.y>=header.y+header.height-1,"practice hero must follow app header");
  assert.ok(support.y>=hero.y+hero.height-1,"supporting practice content must follow hero");
  assert.equal(await page.locator("#openPracticeBtn").isVisible(),true,"primary practice CTA must be visible");
  await page.locator("#tabStats").click();
  await page.locator("#statsView.active").waitFor({state:"visible"});
  assert.equal(((await page.locator("#statsView .view-heading h2").textContent())||"").trim(),"Progress");
  await page.locator("#tabLibrary").click();
  await page.locator("#libraryView.active").waitFor({state:"visible"});
  assert.equal(((await page.locator("#libraryView .view-heading h2").textContent())||"").trim(),"Vocabulary");
  await page.locator("#tabPractice").click();
  await page.locator("#practiceView.active").waitFor({state:"visible"});
  await noHorizontalOverflow(page,"desktop");
  assert.deepEqual(errors,[],`desktop shell browser errors: ${errors.join(" | ")}`);
  await page.screenshot({path:"test-artifacts/shell-desktop-1440x900.png",fullPage:false});
  await context.close();
}

async function mobile(browser,width,height){
  const context=await browser.newContext({viewport:{width,height},isMobile:true,hasTouch:true,deviceScaleFactor:1});
  const page=await context.newPage();
  const errors=[];
  page.on("pageerror",e=>errors.push(e.message));
  page.on("console",m=>{if(m.type()==="error") errors.push(m.text());});
  await page.goto(BASE_URL,{waitUntil:"networkidle"});
  const nav=page.locator(".app-nav");
  const navBox=await nav.boundingBox();
  assert.ok(navBox,`${width}x${height}: bottom nav has no box`);
  const navPosition=await nav.evaluate(el=>getComputedStyle(el).position);
  assert.equal(navPosition,"fixed",`${width}x${height}: navigation must be fixed on mobile`);
  assert.ok(Math.abs(navBox.y+navBox.height-height)<=2,`${width}x${height}: nav must meet viewport bottom`);
  assert.equal(await page.locator(".app-header .brand").isVisible(),true,`${width}x${height}: compact top brand must remain visible`);
  assert.equal(await page.locator("#openPracticeBtn").isVisible(),true,`${width}x${height}: primary practice CTA must be visible`);
  const hero=await page.locator(".practice-hero").boundingBox();
  const support=await page.locator(".practice-support-grid").boundingBox();
  assert.ok(hero&&support&&support.y>=hero.y+hero.height-1,`${width}x${height}: practice hierarchy order is wrong`);
  for(const [tab,view] of [["#tabStats","#statsView"],["#tabLibrary","#libraryView"],["#tabPractice","#practiceView"]]){
    await page.locator(tab).click();
    await page.locator(`${view}.active`).waitFor({state:"visible"});
    const after=await nav.boundingBox();
    assert.ok(after&&Math.abs(after.y+after.height-height)<=2,`${width}x${height}: nav moved after ${tab}`);
  }
  await noHorizontalOverflow(page,`${width}x${height}`);
  assert.deepEqual(errors,[],`${width}x${height}: shell browser errors: ${errors.join(" | ")}`);
  await page.screenshot({path:`test-artifacts/shell-mobile-${width}x${height}.png`,fullPage:false});
  await context.close();
}

const browser=await chromium.launch({headless:true});
try{
  await desktop(browser);
  await mobile(browser,360,740);
  await mobile(browser,390,844);
  await mobile(browser,412,915);
  console.log("UI2 app-shell browser verification passed.");
}finally{await browser.close();}
