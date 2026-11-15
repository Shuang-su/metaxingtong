#!/usr/bin/env python3
"""Build v10 candidates at original frame count and timings."""
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from repair_desk import DOC,ROOT,load,plate,repair

OUT=ROOT/'emotes/sunburst/agent-emotes/11-count/versions/20261115-desk-continuity/v10-desk-r1'

def save_gif(frames,path,times):
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=times,loop=0,disposal=2,optimize=False)

def main():
    fs,ts=load(); donor=plate(fs);OUT.mkdir(parents=True,exist_ok=True)
    donor.save(OUT/'desk-plate-from-original-F49.png')
    out=[];records=[]
    for n,im in enumerate(fs,1):
        if n<50:
            p=im.quantize(colors=256,method=Image.Quantize.MAXCOVERAGE,dither=Image.Dither.NONE)
            assert p.convert('RGB').tobytes()==im.tobytes()
        else:
            p,mask,protect,alpha=repair(im,donor,'r1')
            rgb=p.convert('RGB');rgb.save(OUT/f'candidate-{n:02}.png')
            for label,arr in [('allowed-mask',mask*255),('protected-mask',protect*255),('alpha',alpha*255)]:
                Image.fromarray(arr.astype('uint8')).save(OUT/f'{label}-{n:02}.png')
            layer=donor.convert('RGBA');layer.putalpha(Image.fromarray(np.rint(alpha*255).astype('uint8')));layer.save(OUT/f'local-layer-{n:02}.png')
            records.append({'frame':n,'duration_ms':ts[n-1],'donor_frame':49,'changed_pixels':int(np.any(np.asarray(rgb)!=np.asarray(im),axis=2).sum()),'variant':'r1','allowed_bounds':[8,688,760,756]})
        out.append(p)
    save_gif(out,OUT/'11-v10-CANDIDATE-master-768.gif',ts)
    rgb=[p.convert('RGB') for p in out]
    previews=[im.resize((112,112),Image.Resampling.LANCZOS).quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE) for im in rgb]
    save_gif(previews,OUT/'11-v10-CANDIDATE-preview-112.gif',ts)
    compare=[]
    for n,(before,after) in enumerate(zip(fs,rgb),1):
        c=Image.new('RGB',(640,342),'#eeeeee');d=ImageDraw.Draw(c)
        d.text((6,5),f'Original  F{n:02}  {ts[n-1]} ms',fill='black');d.text((326,5),'v10 desk candidate',fill='black')
        c.paste(before.resize((320,320),Image.Resampling.LANCZOS),(0,22));c.paste(after.resize((320,320),Image.Resampling.LANCZOS),(320,22));compare.append(c.quantize(colors=256,dither=Image.Dither.NONE))
    save_gif(compare,OUT/'11-original-v10-comparison-320.gif',ts)
    contact=Image.new('RGB',(8*120,7*132),'#eeeeee');d=ImageDraw.Draw(contact)
    for j,p in enumerate(previews):
        x=j%8*120;y=j//8*132;contact.paste(p.convert('RGB'),(x+4,y));d.text((x+3,y+114),f'{j+1:02} {ts[j]}ms',fill='black')
    contact.save(OUT/'all-54-frames-at-112.png')
    c=Image.new('RGB',(1536,7*118),'#eeeeee');d=ImageDraw.Draw(c)
    for j,n in enumerate([49,50,51,52,53,54,1]):
        for k,im in enumerate([fs[n-1],rgb[n-1]]):
            x=k*768;y=j*118;c.paste(im.crop((0,670,768,768)),(x,y+20));d.text((x+4,y+3),f'F{n:02} '+('original' if k==0 else 'v10'),fill='black')
    c.save(OUT/'desk-native-boundaries-and-loop.png')
    (OUT/'construction.json').write_text(json.dumps({'version':'v10-desk-r1','method':'same-frame-count local F49 desk pixel donor, foreground silhouettes protected','original_source_commit':'76051cf96bffc57200f90a6e4d88ed1ae9812287','recovered_original_animation':False,'frames':records},indent=2)+'\n')
    print(OUT)

if __name__=='__main__':main()
