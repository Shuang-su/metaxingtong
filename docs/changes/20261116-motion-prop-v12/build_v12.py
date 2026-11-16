#!/usr/bin/env python3
"""Build reversible partial 03 mouth phase and local 11 prop stabilization."""
import json,hashlib,csv
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import repair_v12 as r
DOC=r.DOC;ROOT=r.ROOT
OUT03=ROOT/'emotes/sunburst/agent-emotes/03-awake/versions/20261116-motion-v12/v12-mouth-phase-r3'
OUT11=ROOT/'emotes/sunburst/agent-emotes/11-count/versions/20261116-motion-v12/v12-prop-r6'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def savegif(fs,p,ts):fs[0].save(p,save_all=True,append_images=fs[1:],duration=ts,loop=0,disposal=2,optimize=False)
def palette(im):return im.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
def build(code,src,out):
 out.mkdir(parents=True,exist_ok=False);old,ts=r.load(src);new=[];records=[];small=[];comp=[];native=[]
 for n,im in enumerate(old,1):
  if code=='03':
   if n==5:q,mask,rec=r.mouth_trial(im)
   else:mask=np.zeros((768,768),bool);q=r.quantize(im,im,mask);rec={'method':'unchanged'}
  else:
   q,mask,prop,rec=r.prop_repair(im,old[0]);Image.fromarray(prop.astype('uint8')*255).save(out/f'source-prop-mask-{n:02}.png')
  rgb=q.convert('RGB');a=np.array(im);b=np.array(rgb);change=np.any(a!=b,axis=2)
  assert not (change&~mask).any()
  if code=='11':
   assert not change[:,:505].any()
   protected=r.hair_protection(im);assert not (change&protected).any();Image.fromarray(protected.astype('uint8')*255).save(out/f'protected-hair-{n:02}.png')
  if mask.any():
   rgb.save(out/f'candidate-{n:02}.png');Image.fromarray(mask.astype('uint8')*255).save(out/f'allowed-{n:02}.png')
  records.append({'frame':n,'duration_ms':ts[n-1],'changed_pixels':int(change.sum()),'outside_mask_changed_pixels':0,**rec});new.append(q)
  s=rgb.resize((112,112),Image.Resampling.LANCZOS);small.append(palette(s))
  c=Image.new('RGB',(224,130),'#eee');c.paste(im.resize((112,112),Image.Resampling.LANCZOS),(0,18));c.paste(s,(112,18));d=ImageDraw.Draw(c);d.text((2,2),'before',fill='black');d.text((114,2),'v12 '+f'F{n:02}',fill='black');comp.append(palette(c))
  if code=='03':box=(120,430,285,510)
  else:box=(500,405,760,753)
  w=box[2]-box[0];h=box[3]-box[1];c=Image.new('RGB',(w*2,h+20),'#eee');c.paste(im.crop(box),(0,20));c.paste(rgb.crop(box),(w,20));d=ImageDraw.Draw(c);d.text((2,2),f'before F{n:02}',fill='black');d.text((w+2,2),'v12',fill='black');native.append(palette(c))
 savegif(new,out/f'{code}-v12-CANDIDATE-master-768.gif',ts);savegif(small,out/f'{code}-v12-CANDIDATE-chat-112.gif',ts);savegif(comp,out/f'{code}-v12-before-after-112.gif',ts);savegif(native,out/f'{code}-v12-local-before-after.gif',ts)
 for start in range(0,len(old),18):
  c=Image.new('RGB',(6*224,3*130),'#eee')
  for j,im in enumerate(comp[start:start+18]):c.paste(im.convert('RGB'),((j%6)*224,(j//6)*130))
  c.save(out/f'{code}-112-contact-{start+1:02}-{min(start+18,len(old)):02}.png')
 (out/'construction.json').write_text(json.dumps({'source':str(src.relative_to(ROOT)),'source_sha256':sha(src),'original_frame_durations_ms':ts,'frames':records,'api_calls':0},indent=2)+'\n')
 if code=='11':
  for start in range(0,len(old),9):
   c=Image.new('RGB',(3*520,3*368),'#eee')
   for j,im in enumerate(native[start:start+9]):c.paste(im.convert('RGB'),((j%3)*520,(j//3)*368))
   c.save(out/f'11-native-contact-{start+1:02}-{min(start+9,len(old)):02}.jpg',quality=95)
 print(code,'built',len(new),'frames',sum(ts),'ms',flush=True)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--only',choices=['03','11','both'],default='11');a=p.parse_args()
 if a.only in ['03','both']:build('03',r.SRC03,OUT03)
 if a.only in ['11','both']:build('11',r.SRC11,OUT11)
