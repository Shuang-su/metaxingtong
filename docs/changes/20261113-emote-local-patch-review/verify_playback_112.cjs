// Offline Chromium playback verification. Screenshots are local audit evidence.
const fs=require('fs');
const path=require('path');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'../../..');
const evidence='/workspace/emote-local-patch-review/browser-evidence';
const names=['02-butterfly','03-awake'];
const folders=names.map(n=>path.join(root,'emotes/sunburst/agent-emotes',n));
const reports=folders.map(p=>JSON.parse(fs.readFileSync(path.join(p,'versions/20261113-local-patch-review/rejected-review/validation.json'))));
fs.mkdirSync(path.join(evidence,'reference'),{recursive:true});
fs.mkdirSync(path.join(evidence,'samples'),{recursive:true});
const html=path.join(evidence,'playback.html');
fs.writeFileSync(html,'<!doctype html><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:white;width:224px;height:224px}main{display:grid;grid-template-columns:112px 112px}img{display:block;width:112px;height:112px;object-fit:contain}</style><main><img id="a"><img id="b"><img id="c"><img id="d"></main>');

let activeBrowser;
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-background-networking']});
 activeBrowser=browser;
 const context=await browser.newContext({viewport:{width:224,height:224},deviceScaleFactor:1,offline:true});
 const page=await context.newPage();
 const blocked=[];await page.route(/^https?:/,route=>{blocked.push(route.request().url());return route.abort();});
 await page.goto('file://'+html);
 const assign=async urls=>page.evaluate(async urls=>{await Promise.all(['a','b','c','d'].map(async(id,i)=>{const el=document.getElementById(id);el.src=urls[i];await el.decode();}));},urls.map(p=>'file://'+p));
 const references=[];
 for(let n=1;n<=58;n++){
  const paths=[],ids=[];
  for(let j=0;j<2;j++){
   const i=Math.min(n,reports[j].frame_count);ids.push(i);
   const v=path.join(folders[j],'versions/20261113-local-patch-review');
   const base=path.join(v,'original-decoded',String(i).padStart(2,'0')+'.png');
   paths.push(base,reports[j].modified_frames.includes(i)?path.join(v,'rejected-review','gif-decoded-'+String(i).padStart(2,'0')+'.png'):base);
  }
  await assign(paths);
  const name=String(n).padStart(3,'0')+'.png';
  await page.screenshot({path:path.join(evidence,'reference',name),animations:'allow'});
  references.push({file:'reference/'+name,frames:ids});
 }
 const urls=folders.flatMap(p=>[path.join(p,'master.gif'),path.join(p,'versions/20261113-local-patch-review/rejected-review/REJECTED-candidate-full-loop.gif')]);
 await assign(urls);
 const dimensions=await page.evaluate(()=>({devicePixelRatio,images:[...document.images].map(el=>({width:el.getBoundingClientRect().width,height:el.getBoundingClientRect().height,complete:el.complete,naturalWidth:el.naturalWidth}))}));
 const samples=[];const start=performance.now();
 while(performance.now()-start<20000){
  const n=samples.length,name=String(n).padStart(4,'0')+'.png';
  const before=performance.now()-start;
  await page.screenshot({path:path.join(evidence,'samples',name),animations:'allow'});
  samples.push({file:'samples/'+name,before_ms:before,after_ms:performance.now()-start});
  await page.waitForTimeout(15);
 }
 await browser.close();
 const result={status:'captured_requires_frame_matching',dimensions,blocked_network_requests:blocked,references,samples,elapsed_ms:performance.now()-start};
 fs.writeFileSync(path.join(evidence,'capture.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify({evidence,samples:samples.length,dimensions}));
})().catch(async e=>{
 fs.writeFileSync(path.join(evidence,'capture-failure.json'),JSON.stringify({status:'blocked_or_failed_not_verified',error:e.message},null,2));
 if(activeBrowser)await activeBrowser.close();
 console.error(e.message);process.exitCode=1;
});
