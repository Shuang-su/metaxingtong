#!/usr/bin/env python3
"""Explicit garment-only trials from a shared real F54 donor. No new frames."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import map_coordinates
ROOT=Path(__file__).resolve().parents[3];DOC=Path(__file__).resolve().parent
sys.path.insert(0,str(DOC.parent/'20261115-emote-boundary-refinement'))
from refine_local import frames,base,protect,polygon,compose,quantize_exact_outside
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)

def patch(im,n,variant):
    a=np.array(im);b=base('03-awake');source=Image.open(b/'original-decoded/54.png').convert('RGB')
    rec=json.loads((b/'v6-contour-and-motion/dynamic-candidate-r1/validation.json').read_text())['frames'][n-1]['construction']['shoulder']['placement'];dx,dy=rec['dx'],rec['dy']
    sp=np.array([[264,458],[302,478],[247,514]],float)
    if variant=='A_translation':tp=sp+[0,10]
    elif variant=='B_landmarks':tp=np.array([[270,481],[310,498],[241,528]],float)+[dx,dy]
    elif variant=='C_narrow_fall':tp=np.array([[270,481],[309,495],[244,526]],float)+[dx,dy]
    else:raise ValueError(variant)
    coef=np.linalg.solve(np.column_stack([tp,np.ones(3)]),sp)
    yy,xx=np.indices(a.shape[:2]);co=np.stack([xx,yy,np.ones_like(xx)],-1)@coef;src=np.array(source)
    paint=np.stack([map_coordinates(src[:,:,c].astype(float),[co[:,:,1],co[:,:,0]],order=1,mode='nearest') for c in range(3)],-1)
    old=np.array(Image.open(b.parent/'20261115-boundary-refinement/v8-local-r2'/f'allowed-mask-{n:02d}.png'))>0
    pts=np.array([[230,535],[236,515],[246,495],[263,482],[277,475],[296,484],[311,499],[322,508],[326,523],[314,532],[300,528],[280,537],[257,541]])+[dx,dy]
    mask=(old|polygon(pts))&~protect('03-awake',n);mask[:450]=False;mask[550:]=False
    arr=compose(a,paint,mask,2);im2=quantize_exact_outside(im,Image.fromarray(arr),mask).convert('RGB')
    assert not np.any(np.any(a!=np.array(im2),axis=-1)&(~mask|protect('03-awake',n)))
    return im2,mask,{'variant':variant,'donor_frame':54,'source_points':sp.tolist(),'target_points':tp.tolist(),'inverse_affine':coef.tolist(),'polygon':pts.tolist()}

def main():
    src=base('03-awake').parent/'20261115-boundary-refinement/v8-local-r2/03-v8-CANDIDATE-master-768.gif';ims,_=frames(src);out=DOC/'prototype-r0';out.mkdir(exist_ok=False)
    for n in [5,17]:
        box=(225,450,340,545);w=230;h=190;sheet=Image.new('RGB',(w*4,h+25),'#ddd');dr=ImageDraw.Draw(sheet)
        sheet.paste(ims[n-1].crop(box).resize((w,h),Image.Resampling.NEAREST),(0,25));dr.text((3,3),f'F{n} v8',font=FONT,fill='black')
        for i,v in enumerate(['A_translation','B_landmarks','C_narrow_fall'],1):
            im,m,details=patch(ims[n-1],n,v);stem=f'F{n:02d}-{v}';im.save(out/(stem+'.png'));Image.fromarray(m.astype('uint8')*255).save(out/(stem+'-mask.png'));(out/(stem+'.json')).write_text(json.dumps(details,indent=2)+'\n');sheet.paste(im.crop(box).resize((w,h),Image.Resampling.NEAREST),(i*w,25));dr.text((i*w+3,3),v,font=FONT,fill='black')
        sheet.save(out/f'F{n:02d}-comparison.png')
if __name__=='__main__':main()
