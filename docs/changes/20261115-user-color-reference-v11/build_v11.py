#!/usr/bin/env python3
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import color_v11 as c

def outdir(name):return c.ROOT/'emotes/sunburst/agent-emotes'/name/'versions/20261115-user-color-reference/v11-color-r5'
def savegif(fs,p,times):fs[0].save(p,save_all=True,append_images=fs[1:],duration=times,loop=0,disposal=2,optimize=False)
def main():
 samples=c.reference_samples();(c.DOC/'reference-sampling.json').write_text(json.dumps(samples,ensure_ascii=False,indent=2)+'\n')
 for name in c.SOURCES:
  fs,times=c.load(name);pool=c.set_common_pool(name,fs);out=outdir(name);out.mkdir(parents=True,exist_ok=True)
  results=[];rows=[];overlays=[]
  for n,im in enumerate(fs,1):
   q,ms,row=c.transform(name,im,n,samples);rgb=q.convert('RGB');rgb.save(out/f'candidate-{n:02}.png');union=np.zeros((768,768),bool)
   overlay=np.array(im).copy();colors={'hair':[240,0,150],'bang':[0,200,0],'left_iris':[0,140,255],'right_iris':[240,170,0]}
   for key,m in ms.items():
    Image.fromarray(m.astype('uint8')*255).save(out/f'{key}-mask-{n:02}.png');union|=m;overlay[m]=np.rint(overlay[m]*.5+np.array(colors[key])*.5).astype('uint8')
   Image.fromarray(union.astype('uint8')*255).save(out/f'allowed-mask-{n:02}.png')
   layer=rgb.convert('RGBA');layer.putalpha(Image.fromarray(union.astype('uint8')*255));layer.save(out/f'local-color-layer-{n:02}.png')
   row.update(frame=n,duration_ms=times[n-1],outside_mask_changed_pixels=0);rows.append(row);results.append(q);overlays.append(Image.fromarray(overlay))
   if n%10==0:print(name,n,'/',len(fs),flush=True)
  prefix=name[:2];savegif(results,out/f'{prefix}-v11-CANDIDATE-master-768.gif',times)
  previews=[p.convert('RGB').resize((112,112),Image.Resampling.LANCZOS).quantize(colors=256,dither=Image.Dither.NONE) for p in results]
  savegif(previews,out/f'{prefix}-v11-CANDIDATE-preview-112.gif',times)
  comps=[]
  for n,(before,after) in enumerate(zip(fs,results),1):
   im=Image.new('RGB',(640,342),'#eee');d=ImageDraw.Draw(im);d.text((4,4),f'previous F{n:02} {times[n-1]}ms',fill='black');d.text((324,4),'v11 user reference color',fill='black');im.paste(before.resize((320,320),Image.Resampling.LANCZOS),(0,22));im.paste(after.convert('RGB').resize((320,320),Image.Resampling.LANCZOS),(320,22));comps.append(im.quantize(colors=256,dither=Image.Dither.NONE))
  savegif(comps,out/f'{prefix}-previous-v11-comparison-320.gif',times)
  for label,images,sz,cols in [('all-frames-at-112',previews,112,8),('all-mask-overlays-192',overlays,192,6)]:
   canvas=Image.new('RGB',(cols*(sz+4),((len(images)+cols-1)//cols)*(sz+20)),'#eee');d=ImageDraw.Draw(canvas)
   for j,im in enumerate(images):
    x=j%cols*(sz+4);y=j//cols*(sz+20);canvas.paste(im.convert('RGB').resize((sz,sz),Image.Resampling.LANCZOS),(x,y));d.text((x+2,y+sz+2),f'{j+1:02} {times[j]}ms',fill='black')
   canvas.save(out/(label+'.png'))
  (out/'construction.json').write_text(json.dumps({'version':'v11-color-r5','source':c.SOURCES[name],'source_sha256':hashlib.sha256((c.ROOT/'emotes/sunburst/agent-emotes'/name/c.SOURCES[name]).read_bytes()).hexdigest(),'common_hair_palette_rgb':pool.tolist(),'reference_rule':'PNG 75%, single-frame GIF-name sample 25%; distinct left and right iris samples; hair warm taupe not green','frame_durations_ms':times,'frames':rows},ensure_ascii=False,indent=2)+'\n');print(name,'finished',flush=True)

if __name__=='__main__':main()
