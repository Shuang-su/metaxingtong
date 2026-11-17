#!/usr/bin/env python3
import json,hashlib,subprocess
from PIL import Image,ImageDraw
import numpy as np
import repair_v13 as r
DOC=r.DOC;ROOT=r.ROOT;OUT=ROOT/'emotes/sunburst/agent-emotes/03-awake/versions/20261117-continuity-v13/v13-head-r2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def palette(im):return im.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
def savegif(fs,p,t):fs[0].save(p,save_all=True,append_images=fs[1:],duration=t,loop=0,disposal=2,optimize=False)
def mae(a,b,box):return float(np.abs(np.array(a.crop(box)).astype(float)-np.array(b.crop(box)).astype(float)).mean())
def main():
 OUT.mkdir(parents=True,exist_ok=False);old,times=r.v12.load(r.SRC03);new=[];small=[];compare=[];rows=[];proof=[]
 for n,im in enumerate(old,1):
  amount={2:8,3:16,4:24}.get(n,0)
  if amount:
   q,allowed,protected,params=r.head_trial(im,amount,frame=n)
   q.convert('RGB').save(OUT/f'candidate-{n:02}.png');Image.fromarray(allowed.astype('uint8')*255).save(OUT/f'allowed-{n:02}.png');Image.fromarray(protected.astype('uint8')*255).save(OUT/f'protected-{n:02}.png')
  else:
   allowed=np.zeros((768,768),bool);protected=~allowed;q=r.v12.quantize(im,im,allowed);params={'method':'unchanged'}
  a=np.array(im);b=np.array(q.convert('RGB'));changed=np.any(a!=b,axis=2);assert not (changed&~allowed).any() and not (changed&protected).any();assert not changed[560:].any()
  color_mask=np.array(Image.open(r.SRC03.parent/f'allowed-mask-{n:02}.png'))>0;assert not (changed&color_mask).any()
  new.append(q);s=q.convert('RGB').resize((112,112),Image.Resampling.LANCZOS);small.append(palette(s));c=Image.new('RGB',(224,130),'#eee');c.paste(im.resize((112,112),Image.Resampling.LANCZOS),(0,18));c.paste(s,(112,18));d=ImageDraw.Draw(c);d.text((2,2),f'v11 F{n:02}',fill='black');d.text((114,2),'v13 trial',fill='black');compare.append(palette(c));rows.append({'frame':n,'duration_ms':times[n-1],'changed_pixels':int(changed.sum()),'outside_mask_changed_pixels':0,'protected_changed_pixels':0,**params})
 savegif(new,OUT/'03-v13-CANDIDATE-master-768.gif',times);savegif(small,OUT/'03-v13-CANDIDATE-chat-112.gif',times);savegif(compare,OUT/'03-v13-before-after-112.gif',times)
 for start in range(0,54,18):
  c=Image.new('RGB',(6*224,3*130),'#eee')
  for j,im in enumerate(compare[start:start+18]):c.paste(im.convert('RGB'),(j%6*224,j//6*130))
  c.save(OUT/f'03-v13-contact-{start+1:02}-{start+18:02}.png')
 c=Image.new('RGB',(6*224,130),'#eee')
 for j,n in enumerate([52,53,54,1,2,3]):c.paste(compare[n-1].convert('RGB'),(j*224,0))
 c.save(OUT/'03-v13-loop-boundary-112.png')
 (OUT/'construction.json').write_text(json.dumps({'source':str(r.SRC03.relative_to(ROOT)),'sha256':sha(r.SRC03),'source_frames_only':True,'new_or_repeated_frames_inserted':False,'frames':rows},indent=2)+'\n')
 decoded,nt=r.v12.load(OUT/'03-v13-CANDIDATE-master-768.gif');assert nt==times==json.loads((ROOT/'emotes/sunburst/agent-emotes/03-awake/manifest.json').read_text())['frame_durations_ms']
 for n,(im,q) in enumerate(zip(old,decoded),1):
  assert q.tobytes()==new[n-1].convert('RGB').tobytes()
  if n not in [2,3,4]:assert q.tobytes()==im.tobytes()
 transitions=[]
 for i in range(54):
  j=(i+1)%54;row={'from':i+1,'to':j+1}
  for name,box in [('whole',(0,0,768,768)),('head_and_collar',(0,100,400,560))]:row[name]={'before':mae(old[i],old[j],box),'after':mae(decoded[i],decoded[j],box)}
  transitions.append(row)
 for p in sorted(OUT.glob('*.gif')):
  fs,tt=r.v12.load(p);assert len(fs)==54 and tt==times and Image.open(p).info.get('loop')==0
  result=subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],capture_output=True,text=True);assert result.returncode==0 and result.stderr=='',result.stderr
  proof.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size,'frames':len(fs),'durations_ms':tt,'size':fs[0].size,'ffmpeg_full_decode_pass':True})
 unchanged=[]
 for code,path,expected,n,ms in [('02',r.SRC02,'71f0f0c4ba445de6a1026d5eff88fe41773a9b859c1c6762dc5ccfa4a5ecdaab',58,4860),('03',r.SRC03,'37f901655390cabe5575945a91e7833e4b731db7cf4855c4a1f48aecacfe3e06',54,4650),('11',r.SRC11,'2e536d3ffb84e72682e9ee711749b3838255c3bd0788471e27ab9f770705f311',54,4740)]:
  assert sha(path)==expected;fs,tt=r.v12.load(path);assert len(fs)==n and sum(tt)==ms
  ff=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'],capture_output=True,text=True);assert ff.returncode==0 and not ff.stderr
  unchanged.append({'emote':code,'path':str(path.relative_to(ROOT)),'sha256':expected,'frames':n,'total_ms':ms,'full_decode_pass':True,'retained_unchanged':True})
  if code in ['02','11']:
   c=Image.new('RGB',(8*112,((n+7)//8)*130),'#eee');d=ImageDraw.Draw(c)
   for j,f in enumerate(fs):x=j%8*112;y=j//8*130;c.paste(f.resize((112,112),Image.Resampling.LANCZOS),(x,y+18));d.text((x+2,y+2),f'F{j+1:02} {tt[j]}ms',fill='black')
   c.save(DOC/f'{code}-baseline-all-112.png')
 v11=json.loads((ROOT/'docs/changes/20261115-user-color-reference-v11/final-v11-validation.json').read_text());originals=[]
 for e in json.loads((ROOT/'docs/changes/20261113-emote-local-patch-review/intake-verification.json').read_text())['files_verified']:
  assert sha(ROOT/e['path'])==e['sha256'];originals.append(e['path'])
 refs=ROOT/'docs/changes/20261115-user-color-reference-v11/references'
 for name,h in [('OpenAI Playground 2026-11-05 at 12.43.45.png','01ed7bcb93b3868bc11a65cd70d393b9ec8df5038f8d45c07dd1e0dda4df6aa3'),('naigreen-not-angry.gif','fdf70c25d163d202b84cd8fda911f41b1c43a66d63496ba8cadecd72753aaa52')]:assert sha(refs/name)==h;originals.append(str((refs/name).relative_to(ROOT)))
 report={'version':'03-v13-head-r2','status':'candidate, not final dynamic acceptance','changed_frames':[2,3,4],'changed_duration_ms':sum(times[x-1] for x in [2,3,4]),'preserved_whole_frames':51,'protected_pixels_changed':0,'v11_Nailv_color_region_changed_pixels':0,'original_frames':54,'distinct_decoded_frames':len({hashlib.sha256(x.tobytes()).hexdigest() for x in decoded}),'total_ms':sum(nt),'gifs':proof,'transitions':transitions,'unchanged_baselines':unchanged,'original_files_hashes_pass':originals,'api_calls':0,'api_generation_cost_usd':0,'codex_work_usage':'Not measured per task. No API call does not mean no Codex/Work quota consumption.','actual_visible_playback':'UNVERIFIED: no desktop interaction tool or DISPLAY available; old blocked browser route not retried','visual_review':'pending contact review','remaining':'Wake expression change and original loop pose change are not resolved. 02 stays v11; 11 stays v12; desk trial not adopted.'}
 (DOC/'v13-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'transitions_first6':transitions[:6],'loop':transitions[-1],'artifacts':proof},indent=2))
if __name__=='__main__':main()
