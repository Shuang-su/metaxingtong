"""Play decoded GIF at 112px for three real-time cycles in local Chromium."""
from pathlib import Path
import base64,io,json
from PIL import Image
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent

def main():
    urls=[];delays=[]
    with Image.open(HERE/'review-112.gif') as g:
        for i in range(g.n_frames):
            g.seek(i);b=io.BytesIO();g.convert('RGB').save(b,format='PNG');urls.append('data:image/png;base64,'+base64.b64encode(b.getvalue()).decode());delays.append(g.info['duration'])
    html='''<body style="background:#eee"><p>112 px / original exposure / three cycles</p><canvas width="112" height="112"></canvas><p id="status"></p><script>
const urls=URLS,ds=DELAYS;const canvas=document.querySelector('canvas'),ctx=canvas.getContext('2d');window.log=[];window.done=false;
Promise.all(urls.map(u=>new Promise(r=>{let i=new Image;i.onload=()=>r(i);i.src=u}))).then(images=>{
let start=performance.now(),last=-1;function play(now){let t=now-start,loop=Math.floor(t/4560);if(loop>=3){window.done=true;document.querySelector('#status').textContent='three cycles complete';return}let phase=t%4560,sum=0,i=0;while(i<53&&phase>=sum+ds[i])sum+=ds[i++];let id=loop*54+i;if(id!==last){ctx.drawImage(images[i],0,0);log.push({loop:loop+1,frame:i+1,elapsed_ms:t});last=id;}document.querySelector('#status').textContent=`cycle ${loop+1} frame ${i+1}`;requestAnimationFrame(play)}requestAnimationFrame(play)});
</script>'''.replace('URLS',json.dumps(urls)).replace('DELAYS',json.dumps(delays))
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':480,'height':280},record_video_dir=str(HERE/'playback-video'),record_video_size={'width':480,'height':280})
        page=context.new_page();page.set_content(html)
        page.wait_for_function('window.done===true',timeout=20000)
        log=page.evaluate('window.log');page.screenshot(path=str(HERE/'playback-complete.png'))
        assert len(log)==162 and [(r['loop'],r['frame']) for r in log]==[(loop,i) for loop in range(1,4) for i in range(1,55)]
        (HERE/'playback.json').write_text(json.dumps(dict(browser=browser.version,cycles=3,frames_presented=len(log),expected_elapsed_ms=13680,observations=log),indent=2)+'\n')
        context.close();browser.close()
    print('Chromium presented all 162 frames over three 4560ms cycles at 112px.')
if __name__=='__main__':main()
