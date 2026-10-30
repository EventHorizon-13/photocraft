const {chromium}=require('playwright-core');
const {PNG}=require('pngjs');
const fs=require('fs');
function colors(buffer){const p=PNG.sync.read(buffer),s=new Set();for(let y=0;y<p.height;y+=8)for(let x=0;x<p.width;x+=8){const i=(y*p.width+x)*4;s.add(p.data[i]+','+p.data[i+1]+','+p.data[i+2]);}return s.size}
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const reports=[];
 for(const mode of ['default','webgl']){
  const page=await browser.newPage({viewport:{width:1280,height:900},locale:'zh-CN'});
  const errors=[],consoleMessages=[],failed=[],pending=new Set();
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{if(consoleMessages.length<200)consoleMessages.push(m.type()+': '+m.text())});
  page.on('request',r=>pending.add(r.url()));
  page.on('requestfinished',r=>pending.delete(r.url()));
  page.on('requestfailed',r=>{pending.delete(r.url());failed.push({url:r.url(),reason:r.failure()?.errorText})});
  await page.goto('http://127.0.0.1:8765/?lang=zh&locale=zh-CN'+(mode==='webgl'?'&webgl':''),{waitUntil:'domcontentloaded',timeout:60000});
  await page.bringToFront();let count=0,elapsed=0;
  for(const wait of [15000,20000,30000,30000]){
   await page.waitForTimeout(wait);elapsed+=wait;
   await page.mouse.move(320,220);
   const buffer=await page.screenshot({path:'startup-'+mode+'.png'});count=colors(buffer);
   if(count>32)break;
  }
  const info=await page.evaluate(()=>({title:document.title,text:document.body.innerText.slice(0,1000),canvas:document.querySelectorAll('canvas').length,canvasSize:[...document.querySelectorAll('canvas')].map(c=>[c.width,c.height]),vectorAPI:typeof window.vectorcraft,apiKeys:window.vectorcraft?Object.keys(window.vectorcraft):[],visibility:document.visibilityState}));
  reports.push({mode,elapsed,colors:count,...info,errors,failed,pending:[...pending],consoleMessages});
  await page.close();
 }
 fs.writeFileSync('startup.json',JSON.stringify(reports,null,2));
 await browser.close();
 if(reports.some(r=>r.colors<=32||r.errors.length))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
