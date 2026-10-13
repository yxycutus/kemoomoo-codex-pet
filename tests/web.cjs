// Browser regression checks. Starts and closes its own loopback-only HTTP server.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const root = path.resolve(__dirname, '../web');
const mime = {'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.png':'image/png','.webp':'image/webp'};
const server = http.createServer((req, res) => {
  let route;
  try { route = decodeURIComponent(new URL(req.url, 'http://localhost').pathname); }
  catch { res.writeHead(400).end(); return; }
  // Exercise project-site hosting with the same files below a prefix.
  route = route.replace(/^\/project\//, '/');
  const file = path.resolve(root, '.' + (route.endsWith('/') ? route + 'index.html' : route));
  if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
  fs.readFile(file, (error, data) => {
    if (error) { res.writeHead(404).end(); return; }
    res.writeHead(200, {'Content-Type': mime[path.extname(file)] || 'application/octet-stream'}).end(data);
  });
});
const pass = text => console.log('PASS:', text);
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  let browser;
  try {
    browser = await chromium.launch({headless: true, ...(process.env.CHROME_PATH ? {executablePath: process.env.CHROME_PATH} : {})});
    const errors = [];
    const context = await browser.newContext({viewport:{width:1280,height:900}});
    const page = await context.newPage();
    page.on('pageerror', e => errors.push(e.message));
    const goto = async (url = '/') => { await page.goto(base+url); await page.locator('#kemoomoo').waitFor({state:'visible'}); };
    const state = name => page.waitForFunction(name => document.querySelector('.desk-pet')?.dataset.state === name, name);
    const open = async () => { await page.locator('.desk-pet').focus(); await page.keyboard.press('Enter'); await page.locator('#pet-panel').waitFor({state:'visible'}); };
    const settings = async () => { await open(); await page.locator('.pet-settings summary').click(); };
    const event = detail => page.evaluate(detail => document.dispatchEvent(new CustomEvent('cutus:pet', {detail})), detail);
    const bounds = async selector => {
      await page.waitForFunction(selector => {const e=document.querySelector(selector),r=e?.getBoundingClientRect();return r&&r.x>=0&&r.y>=0&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1;}, selector, {timeout:3000}).catch(async error=>{console.log(await page.evaluate(()=>({inner:[innerWidth,innerHeight],visual:[visualViewport.width,visualViewport.height],panel:document.querySelector('#pet-panel').getBoundingClientRect().toJSON(),style:document.querySelector('#pet-panel').style.cssText})));throw error;});
      const r = await page.locator(selector).boundingBox(), v = page.viewportSize();
      assert.ok(r && r.x>=0 && r.y>=0 && r.x+r.width<=v.width+1 && r.y+r.height<=v.height+1, `${selector}: ${JSON.stringify(r)}`);
    };
    await goto(); await state('idle'); await open();
    assert.equal(await page.locator('.pet-nav a').count(), 0, 'No personal-site dead links');
    await page.locator('.pet-page-map summary').click();
    for (const hash of await page.locator('.pet-local-nav a').evaluateAll(a=>a.map(x=>x.hash))) {
      assert.ok(await page.evaluate(hash=>!!document.getElementById(decodeURIComponent(hash.slice(1))), hash));
    }
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('.desk-pet').evaluate(e=>e===document.activeElement), true);
    await page.addScriptTag({url:base+'/pet.js'});
    assert.equal(await page.locator('#kemoomoo').count(),1);
    pass('Demo, optional recommendation, real chapter links, keyboard focus and duplicate initialization');

    for (const name of ['waving','jumping','failed','waiting','running','review','running-right','running-left']) {
      await event({state:name}); await state(name); await state('idle');
    }
    await event({state:'constructor'}); await state('idle');
    await event({scene:'achievement',duration:500}); await state('achievement'); await state('idle');
    pass('All nine animation states, invalid event ignored and scene returns to rest');

    let r = await page.locator('.desk-pet').boundingBox();
    await page.mouse.move(r.x+r.width/2,r.y+r.height/2); await page.mouse.down();
    await page.mouse.move(600,420,{steps:8}); await state('running-left'); await page.mouse.up();
    await state('jumping'); await state('idle');
    assert.equal(await page.locator('#pet-panel').isHidden(),true);
    r = await page.locator('.desk-pet').boundingBox();
    for (const [dx,dy,row,col] of [[0,-150,9,0],[150,0,9,4],[0,150,10,0],[-150,0,10,4]]) {
      await page.mouse.move(r.x+r.width/2+dx,r.y+r.height*.42+dy);
      await page.waitForFunction(({row,col})=>{const d=document.querySelector('.desk-pet').dataset;return +d.row===row&&+d.frame===col;},{row,col});
    }
    await settings(); await page.locator('[data-setting="gaze"]').uncheck();
    await page.locator('[data-size="1"]').click(); assert.equal(await page.locator('.pet-size-value').textContent(),'95%');
    await page.locator('[data-setting="animation"]').uncheck(); await page.keyboard.press('Escape');
    await page.reload(); await state('idle'); await settings();
    assert.equal(await page.locator('[data-setting="gaze"]').isChecked(),false);
    assert.equal(await page.locator('[data-setting="animation"]').isChecked(),false);
    assert.equal(await page.locator('.pet-size-value').textContent(),'95%');
    await page.locator('[data-setting="animation"]').check(); await page.keyboard.press('Escape');
    pass('Drag, release jump, gaze cardinals and preference persistence');

    await page.emulateMedia({reducedMotion:'reduce'}); await settings();
    assert.equal(await page.locator('[data-setting="animation"]').isDisabled(),true);
    await page.keyboard.press('Escape'); await event({scene:'resource',duration:500}); await state('resource');
    assert.equal(await page.locator('.pet-scene').evaluate(e=>getComputedStyle(e).animationName),'none');
    await page.emulateMedia({reducedMotion:'no-preference'}); await state('idle');
    await page.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'));});
    const frozen=await page.locator('.pet-sprite').evaluate(e=>e.style.backgroundPosition);
    await page.waitForTimeout(400);
    assert.equal(await page.locator('.pet-sprite').evaluate(e=>e.style.backgroundPosition),frozen);
    await page.evaluate(()=>{delete document.hidden;document.dispatchEvent(new Event('visibilitychange'));});
    await page.locator('.pet-dismiss').click(); await page.reload();
    await page.locator('.pet-restore').click(); await page.locator('#kemoomoo').waitFor({state:'visible'});
    pass('Reduced motion, background pause, hide/restore');

    // Host websites often style all section/aside elements; widget margins must stay isolated.
    await page.addStyleTag({content:'section, aside { margin-top: 64px; }'});
    await open();
    for (const width of [320,390,768,1280]) { await page.setViewportSize({width,height:640}); await bounds('#kemoomoo'); await bounds('#pet-panel'); }
    await page.setViewportSize({width:390,height:360}); await bounds('#pet-panel');
    await page.keyboard.press('Escape');
    await goto('/project/'); await state('idle'); await open();
    assert.equal(await page.locator('.pet-nav a').count(),0);
    await page.keyboard.press('Escape');
    pass('Responsive widths, short viewport and subdirectory hosting');

    const blocked = await browser.newContext();
    await blocked.addInitScript(()=>{Storage.prototype.getItem=Storage.prototype.setItem=()=>{throw new DOMException('disabled','SecurityError');};});
    const denied = await blocked.newPage(); denied.on('pageerror',e=>errors.push(e.message));
    await denied.goto(base); await denied.locator('.desk-pet').click(); await denied.locator('.pet-settings summary').click();
    await denied.locator('[data-size="1"]').click(); await denied.locator('.pet-hide').click(); await denied.locator('.pet-restore').click();
    await denied.locator('#kemoomoo').waitFor({state:'visible'});
    pass('Storage-disabled operation');

    const failureContext = await browser.newContext(); const failure = await failureContext.newPage(); failure.on('pageerror',e=>errors.push(e.message));
    await failure.route('**/pet/spritesheet.webp',route=>route.abort()); await failure.goto(base);
    await failure.locator('#kemoomoo').waitFor({state:'visible'});
    assert.match(await failure.locator('.pet-sprite').evaluate(e=>e.style.backgroundImage),/spritesheet\.png/);
    await failure.route('**/pet/spritesheet.png',route=>route.abort()); await failure.reload();
    await failure.getByRole('button',{name:'科哞哞未能加载，点击重试'}).waitFor();
    await failure.unroute('**/pet/spritesheet.png'); await failure.locator('.pet-restore').click();
    await failure.locator('#kemoomoo').waitFor({state:'visible'});
    await failure.unroute('**/pet/spritesheet.webp');
    await failure.route('**/pet/spritesheet.webp',route=>route.fulfill({path:path.join(root,'pet/cutouts/welcome.webp'),contentType:'image/webp'}));
    await failure.reload(); await failure.locator('#kemoomoo').waitFor({state:'visible'});
    assert.match(await failure.locator('.pet-sprite').evaluate(e=>e.style.backgroundImage),/spritesheet\.png/);
    await failure.route('**/pet/cutouts/achievement.webp',route=>route.abort());
    await failure.evaluate(()=>document.dispatchEvent(new CustomEvent('cutus:pet',{detail:{scene:'achievement'}})));
    await failure.waitForFunction(()=>document.querySelector('.desk-pet').dataset.state==='idle');
    pass('Missing WebP, incorrect dimensions, PNG fallback, double failure retry and cutout failure');

    const mobile = await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
    const touch = await mobile.newPage();touch.on('pageerror',e=>errors.push(e.message));await touch.goto(base);
    await touch.locator('.desk-pet').tap();await touch.locator('#pet-panel').waitFor({state:'visible'});await touch.locator('.pet-panel-close').tap();
    const tr=await touch.locator('.desk-pet').boundingBox(),x=tr.x+tr.width/2,y=tr.y+tr.height/2;
    const cdp=await mobile.newCDPSession(touch);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});
    await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x-40,y:y-80}]});
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
    const after=await touch.locator('.desk-pet').boundingBox();
    assert.ok(Math.abs(after.x-tr.x+40)<2&&Math.abs(after.y-tr.y+80)<2);
    assert.equal(await touch.locator('#pet-panel').isHidden(),true);
    pass('Real touch tap and drag');
    assert.deepEqual(errors,[]);pass('No unexpected page script errors');
    if (process.env.SCREENSHOT_DIR) {
      fs.mkdirSync(process.env.SCREENSHOT_DIR,{recursive:true});
      await page.setViewportSize({width:1280,height:900});await goto();await settings();await page.locator('.pet-reset').click();await page.keyboard.press('Escape');await open();
      await page.screenshot({path:path.join(process.env.SCREENSHOT_DIR,'desktop.png'),fullPage:true});
      await touch.reload();await touch.locator('.desk-pet').tap();await touch.locator('#pet-panel').waitFor({state:'visible'});await touch.screenshot({path:path.join(process.env.SCREENSHOT_DIR,'mobile.png')});
    }
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve=>server.close(resolve));
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
