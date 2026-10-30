const {chromium}=require('playwright-core');
const fs=require('fs');
(async()=>{
 const app=process.env.APP;
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1280,height:900},locale:'zh-CN'});
 const errors=[],bad=[];
 page.on('pageerror',e=>errors.push(String(e)));
 page.on('response',r=>{if(r.url().startsWith('http://127.0.0.1:8765/')&&r.status()>=400&&!r.url().endsWith('/favicon.ico'))bad.push({url:r.url(),status:r.status()});});
 await page.goto('http://127.0.0.1:8765/?lang=zh&locale=zh-CN',{waitUntil:'domcontentloaded',timeout:60000});
 await page.waitForTimeout(35000);
 await page.screenshot({path:'startup.png',fullPage:false});
 const info=await page.evaluate(()=>({title:document.title,canvas:document.querySelectorAll('canvas').length,text:document.body.innerText.slice(0,1500),fatal:window.filmcraftLoad?.fatal||null}));
 fs.writeFileSync('startup.json',JSON.stringify({app,...info,errors,bad},null,2));
 await browser.close();
 if(errors.length||bad.length||info.fatal||!info.canvas)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
