#!/usr/bin/env python3
"""Local, reversible v8 trials. No API and no full-frame regeneration."""
from pathlib import Path
import sys,json,hashlib,argparse
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import distance_transform_edt,map_coordinates
ROOT=Path(__file__).resolve().parents[3]
DOC=Path(__file__).resolve().parent
sys.path.insert(0,str(DOC.parent/'20261113-emote-local-patch-review'))
from motion_registration import match_translation
from local_contour_layers import bezier
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)

def base(name):return ROOT/'emotes/sunburst/agent-emotes'/name/'versions/20261113-local-patch-review'
def frames(path):
    out=[];times=[]
    with Image.open(path) as g:
        for k in range(g.n_frames):g.seek(k);out.append(g.convert('RGB'));times.append(g.info['duration'])
    return out,times
def polygon(points):
    im=Image.new('L',(768,768));ImageDraw.Draw(im).polygon([tuple(p) for p in points],fill=255);return np.array(im)>0
def protect(name,n):
    sub='dynamic-candidate' if name.startswith('02') else 'dynamic-candidate-r1'
    p=base(name)/'v6-contour-and-motion'/sub/f'protected-{n:02d}.png'
    return np.array(Image.open(p))>0 if p.exists() else np.zeros((768,768),bool)
def quantize_exact_outside(before,after,mask):
    p=before.quantize(colors=256,method=Image.Quantize.MAXCOVERAGE,dither=Image.Dither.NONE)
    assert p.convert('RGB').tobytes()==before.tobytes()
    q=after.quantize(palette=p,dither=Image.Dither.NONE)
    p.paste(q,(0,0),Image.fromarray(mask.astype('uint8')*255))
    assert np.array_equal(np.array(p.convert('RGB'))[~mask],np.array(before)[~mask])
    return p
def compose(a,paint,mask,feather=1.5):
    alpha=np.minimum(distance_transform_edt(mask)/feather,1)*mask
    return np.rint(a*(1-alpha[:,:,None])+paint*alpha[:,:,None]).clip(0,255).astype('uint8')

def stripe(im,n):
    a=np.array(im);S=4;layer=Image.new('RGBA',(768*S,768*S));dr=ImageDraw.Draw(layer)
    moves={24:(3,0),25:(0,0),26:(-1,0),27:(0,1),28:(-2,0)}
    dx,dy=moves[n]
    pts=bezier((626,536),[((633,533),(637,535),(643,538)),((650,541),(659,537),(665,535))])
    pts=[(x+dx,y+dy) for x,y in pts]
    dr.line([(x*S,y*S) for x,y in pts],fill=(239,242,236,255),width=round(2.4*S),joint='curve')
    layer=layer.resize((768,768),Image.Resampling.LANCZOS);raw=np.array(layer)
    mask=(raw[:,:,3]>0)&~protect('02-butterfly',n)
    alpha=raw[:,:,3]/255*mask
    b=np.rint(a*(1-alpha[:,:,None])+raw[:,:,:3]*alpha[:,:,None]).astype('uint8')
    return b,mask,{'kind':'authored narrow stripe continuation','stroke_width':2.4,'path':pts,'offset':[dx,dy]}

def collar(im,n,variant='r0'):
    a=np.array(im);p=base('03-awake');original=Image.open(p/'original-decoded'/f'{n:02d}.png').convert('RGB')
    records={r['frame']:r for r in json.loads((p/'v6-contour-and-motion/dynamic-candidate-r1/validation.json').read_text())['frames']}
    dx=records[n]['construction']['shoulder']['placement']['dx'];dy=records[n]['construction']['shoulder']['placement']['dy']
    if n<=4:
        donor=Image.open(p/'original-decoded/54.png').convert('RGB')
        loc=match_translation(donor,original,[190,530,300,575],[-8,8],[-8,8]);ox,oy=loc['dx'],loc['dy']
        coeff=np.array([[1,0],[0,1],[-ox,-oy]],float)
        pts=np.array([[239,512],[244,488],[249,470],[251,458],[262,452],[275,455],[288,462],[299,474],[311,486],[321,500],[308,514],[286,522],[258,535],[235,536]])+[ox,oy]
        details={'donor_frame':54,'translation':loc}
    else:
        donor=Image.open(p/'original-decoded/28.png').convert('RGB')
        sp=np.array([[257,459],[308,477],[249,524]],float)
        tp=np.array([[269,477],[315,500],[246,528]],float)+[dx,dy]
        pts=np.array([[231,535],[238,515],[248,495],[264,480],[279,474],[296,485],[310,501],[322,509],[326,522],[314,530],[300,523],[280,532],[258,540]])+[dx,dy]
        transition=None
        if 22<=n<=27:
            loc=match_translation(donor,original,[285,540,335,580],[-6,6],[-6,6]);ox,oy=loc['dx'],loc['dy']
            t=(n-21)/6
            tp=tp*(1-t)+(sp+[ox,oy])*t
            natural=np.array([[231,538],[238,515],[246,481],[254,460],[274,457],[296,467],[313,481],[324,499],[329,521],[315,536],[300,538],[280,539],[258,540]])+[ox,oy]
            pts=pts*(1-t)+natural*t
            transition={'toward_normal_F28':t,'normal_coat_registration':loc,'method':'interpolate garment landmarks only; never blend hands or whole frames'}
        coeff=np.linalg.solve(np.column_stack([tp,np.ones(3)]),sp)
        details={'donor_frame':28,'source_points':sp.tolist(),'target_points':tp.tolist()}
        if transition:details['transition']=transition
    yy,xx=np.indices(a.shape[:2]);coords=np.stack([xx,yy,np.ones_like(xx)],-1)@coeff
    src=np.array(donor);paint=np.stack([map_coordinates(src[:,:,c].astype(float),[coords[:,:,1],coords[:,:,0]],order=1,mode='nearest') for c in range(3)],-1)
    mask=polygon(pts)&~protect('03-awake',n)
    # Preserve all color calibration and both characters' heads above the collar.
    mask[:450]=False
    b=compose(a,paint,mask,2)
    return b,mask,{'kind':'normal-frame collar donor, wider natural fall',**details,'polygon':pts.tolist(),'inverse_coefficients':coeff.tolist()}

def knee(im,n):
    a=np.array(im);p=base('03-awake')
    record=next(r for r in json.loads((p/'v6-contour-and-motion/registration.json').read_text()) if r['frame']==n)
    dx,dy=record['knee']['dx'],record['knee']['dy'];yy,xx=np.indices(a.shape[:2],dtype=float);x=xx-dx;y=yy-dy
    oldmask=np.array(Image.open(p/'v6-contour-and-motion/dynamic-candidate-r1'/f'allowed-mask-{n:02d}.png'))>0
    mask=oldmask&(y>570)&(y<636)&(x>478)&(x<568)&(a[:,:,0]>220)&(a[:,:,1]>208)&(a[:,:,2]>201)&~protect('03-awake',n)
    t=np.clip((y-563)/73,0,1)
    left=526-23*t;right=544+9*t
    fold1=np.exp(-.5*((x-left)/(1.8+3*t))**2)*(5+12*t)
    fold2=np.exp(-.5*((x-right)/(1.5+2.8*t))**2)*(4+9*t)
    highlight=np.exp(-.5*((x-(left+7))/(3+2*t))**2)*3
    depth=fold1+fold2-highlight+1.4*t
    paint=np.stack([246-depth,237-depth*.96,231-depth*.9],-1)
    b=compose(a,paint,mask,3)
    return b,mask,{'kind':'continuous local cream pleats; replaces repeated tile texture only','placement':[dx,dy],'formula':'two tapered Gaussian folds, 5-17 and 4-13 levels, 3px inward feather','reconstruction_not_recovered_source':True}

def comparison(before,after,box,path):
    crop=[im.crop(box) for im in [before,after]];w,h=crop[0].size
    canvas=Image.new('RGB',(w*6,(h*3)+28),'#ddd');d=ImageDraw.Draw(canvas)
    for k,im in enumerate(crop):canvas.paste(im.resize((w*3,h*3),Image.Resampling.NEAREST),(k*w*3,28));d.text((k*w*3+4,4),'v7' if k==0 else 'v8 prototype',font=FONT,fill='black')
    canvas.save(path)

def prototype():
    out=DOC/'prototype-r1';out.mkdir(exist_ok=False)
    for name,n,method,box in [('02-butterfly',25,stripe,(600,510,685,560)),('03-awake',1,collar,(230,450,340,545)),('03-awake',17,collar,(230,465,340,550)),('03-awake',17,knee,(460,550,580,645))]:
        ims,_=frames(base(name)/'v7-green-local-r2/CANDIDATE-color-master-768.gif');im=ims[n-1];arr,mask,details=method(im,n);candidate=Image.fromarray(arr)
        q=quantize_exact_outside(im,candidate,mask).convert('RGB');changed=np.any(np.array(im)!=np.array(q),axis=-1)
        assert not np.any(changed&protect(name,n));assert not np.any(changed&~mask)
        label=f'{name}-F{n:02d}-{method.__name__}';q.save(out/(label+'.png'));Image.fromarray(mask.astype('uint8')*255).save(out/(label+'-mask.png'))
        comparison(im,q,box,out/(label+'-comparison.png'));(out/(label+'.json')).write_text(json.dumps(details,indent=2)+'\n')
        print(label,int(changed.sum()),flush=True)
if __name__=='__main__':prototype()
