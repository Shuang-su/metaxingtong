#!/usr/bin/env python3
"""Reversible local olive-green corrections grounded in the archived Bilibili PNG.

Only existing bang/iris pixels are eligible. Body, skin, white flowers, brown
base hair, Xingtong, and all earlier hand repairs remain outside the new masks.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import distance_transform_edt,label
import numpy as np,json,hashlib,sys,argparse,shutil
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'20261113-emote-local-patch-review'))
from motion_registration import match_translation

ROOT=Path(__file__).resolve().parents[3];DOC=Path(__file__).resolve().parent
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
XYZ=np.array([[.4124564,.3575761,.1804375],[.2126729,.7151522,.0721750],[.0193339,.1191920,.9503041]])
WHITE=np.array([.95047,1.,1.08883])
def lab(rgb):
    x=np.asarray(rgb,float)/255;x=np.where(x>.04045,((x+.055)/1.055)**2.4,x/12.92);x=x@XYZ.T/WHITE
    f=np.where(x>(6/29)**3,np.cbrt(x),x/(3*(6/29)**2)+4/29)
    return np.stack([116*f[...,1]-16,500*(f[...,0]-f[...,1]),200*(f[...,1]-f[...,2])],-1)
def rgb(l):
    fy=(l[...,0]+16)/116;f=np.stack([fy+l[...,1]/500,fy,fy-l[...,2]/200],-1)
    x=np.where(f>6/29,f**3,3*(6/29)**2*(f-4/29))*WHITE;x=x@np.linalg.inv(XYZ).T
    x=np.where(x>.0031308,1.055*np.maximum(x,0)**(1/2.4)-.055,12.92*x)
    return np.rint(np.clip(x,0,1)*255).astype('uint8')
def polygon(points):
    m=Image.new('L',(768,768));ImageDraw.Draw(m).polygon(points,fill=255);return np.array(m)>0
def palette_preserve(original,candidate,mask):
    a=np.array(original);b=np.array(candidate);outside=np.unique(a[~mask],axis=0);slots=256-len(outside)
    if not mask.any():return original.quantize(colors=256,method=Image.Quantize.MAXCOVERAGE,dither=Image.Dither.NONE),slots
    assert slots>=2,('insufficient palette slots',slots)
    pixels=b[mask];p=Image.fromarray(pixels[None,:,:]).quantize(colors=slots,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    colors=np.array(p.getpalette(),dtype=np.uint8).reshape(-1,3)[:slots]
    packed=(outside[:,0].astype(np.uint32)<<16)|(outside[:,1].astype(np.uint32)<<8)|outside[:,2]
    values=(a[:,:,0].astype(np.uint32)<<16)|(a[:,:,1].astype(np.uint32)<<8)|a[:,:,2]
    indices=np.searchsorted(packed,values).clip(0,len(outside)-1).astype('uint8')
    indices[mask]=np.array(p)[0]+len(outside)
    result=Image.fromarray(indices,'P');pal=np.vstack([outside,colors]);pal=np.pad(pal,((0,256-len(pal)),(0,0)))
    result.putpalette(pal.flatten().tolist());assert np.array_equal(np.array(result.convert('RGB'))[~mask],a[~mask])
    return result,slots

CENTERS02=[570]*9+[555]*5+[527,459,377,343,267,254,226,199,206]+[185]*5+[192]*5+[240,309,384,377,398,411,453,521,535,569]+[570]*10+[576]*5

def masks02(original,n):
    a=np.array(original,dtype=int);r,g,b=[a[:,:,c] for c in range(3)];yy,xx=np.indices(r.shape);cx=CENTERS02[n-1]
    # Existing pale-olive pixels are separable from pink skin and silver-blue X.
    eligible=(r>95)&(g>95)&(b>60)&(np.abs(r-g)<15)&(g-b>10)&(g-b<65)
    upper=eligible&(yy>=100)&(yy<=380);components,count=label(upper);choices=[];sizes=np.bincount(components.ravel())
    for i in range(1,count+1):
        if sizes[i]<120:continue
        ys,xs=np.where(components==i)
        if len(xs)>=120 and ys.max()-ys.min()>35 and ys.max()-ys.min()>1.4*(xs.max()-xs.min()) and ys.mean()<320:
            choices.append((len(xs),i,float(xs.mean()),int(ys.max())))
    stripe=np.zeros(r.shape,bool)
    if choices:
        _,index,center,bottom=max(choices);cx=round(center);stripe=components==index;eye_y=max(285,bottom-12)
    else:eye_y=300
    # Use the stripe only to follow the head, not to discard disconnected color
    # islands across the original highlight texture. The initial fixed bounds
    # missed F38-F40; the first component-only revision missed small highlights.
    region=(xx>=cx-105)&(xx<=cx+105)&(yy>=100)&(yy<=380)
    mask=eligible&region
    components,count=label(mask);sizes=np.bincount(components.ravel());keep=sizes>=16;keep[0]=False;mask=keep[components]
    return {'existing_olive_bang_iris':mask},{'head_center_x':cx,'region':[cx-105,100,cx+105,380],'selection':'track actual stripe position, retain existing olive color islands in central bang/iris region; no brown-hair replacement'}

def masks03(original,frames,n):
    a=np.array(original,dtype=int);r,g,b=[a[:,:,c] for c in range(3)]
    frontal=n<=4 or n>=40
    reference=frames[0 if frontal else 16]
    if frontal:
        reference_box=[510,180,552,312]
        raw_points=[[541,179],[533,198],[524,220],[519,248],[520,270],[526,296],[535,308],[532,279],[534,255],[535,224],[540,194]]
        eyes=[('left_iris',[455,310,523,375],[468,323,511,363]),('right_iris',[570,310,640,375],[583,322,626,362])]
    else:
        reference_box=[505,190,550,330]
        raw_points=[[544,188],[535,206],[526,231],[519,254],[516,282],[516,314],[522,329],[527,321],[530,295],[531,263],[535,232],[539,209]]
        eyes=[('left_iris',[439,329,486,385],[451,339,477,375]),('right_iris',[548,339,599,393],[559,350,588,386])]
    m=match_translation(reference,original,reference_box,[-35,35],[-24,24]);dx,dy=m['dx'],m['dy']
    points=np.array(raw_points)+np.array([dx,dy])
    bang=polygon([tuple(x) for x in points])&(r>160)&(b>135)&(r-g<35)&(g-b<30)
    masks={'bang_streak':bang};details={'reference_frame':1 if frontal else 17,'bang':m,'bang_polygon':points.tolist(),'eyes_closed':34<=n<=39}
    if not 34<=n<=39:
        eye_records={}
        for name,box,ellipse in eyes:
            loc=match_translation(reference,original,box,[-35,35],[-24,24]);ex,ey=loc['dx'],loc['dy'];e=Image.new('L',(768,768));ed=ImageDraw.Draw(e);ed.ellipse((ellipse[0]+ex,ellipse[1]+ey,ellipse[2]+ex,ellipse[3]+ey),fill=255)
            masks[name]=(np.array(e)>0)&(np.minimum(np.minimum(r,g),b)>90)&(np.maximum(np.maximum(r,g),b)<215)&(r-g<35)&(g-b<30)
            eye_records[name]=loc
        details['eyes']=eye_records
    return masks,details

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='v7-green-local-candidate');parser.add_argument('--prototype',action='store_true');parser.add_argument('--frames',nargs='+',type=int);parser.add_argument('--emotes',nargs='+',default=['02-butterfly','03-awake'],choices=['02-butterfly','03-awake']);parser.add_argument('--reuse-unchanged-from');parser.add_argument('--changed-frames',nargs='+',type=int,default=[]);args=parser.parse_args()
    ref_path=DOC/'references/source-a850fb4/n-static-laugh.png';ref=np.array(Image.open(ref_path).convert('RGB'))
    targets={'bang':np.median(ref[69:72,75:78].reshape(-1,3),axis=0),'iris':np.median(ref[105:108,93:96].reshape(-1,3),axis=0)}
    target_lab={k:lab(v)[1:] for k,v in targets.items()}
    for name,v in [('02-butterfly','dynamic-candidate'),('03-awake','dynamic-candidate-r1')]:
        if name not in args.emotes:continue
        base=ROOT/'emotes/sunburst/agent-emotes'/name/'versions/20261113-local-patch-review'
        out=base/args.output;out.mkdir(exist_ok=False)
        src=base/'v6-contour-and-motion'/v/'CANDIDATE-master-768.gif';frames=[];times=[]
        with Image.open(src) as gif:
            for k in range(gif.n_frames):gif.seek(k);frames.append(gif.convert('RGB'));times.append(gif.info['duration'])
        ids=[27] if name.startswith('02') else [17]
        if not args.prototype:ids=list(range(1,len(frames)+1))
        elif args.frames:ids=args.frames
        previous_frames=[];previous_rows={}
        if args.reuse_unchanged_from:
            previous=base/args.reuse_unchanged_from
            previous_rows={x['frame']:x for x in json.loads((previous/'construction.json').read_text())['frames']}
            with Image.open(previous/'CANDIDATE-color-master-768.gif') as gif:
                for k in range(gif.n_frames):gif.seek(k);previous_frames.append(gif.convert('RGB'))
        pframes=[];rows=[];newframes=[]
        for n in ids:
            if args.reuse_unchanged_from and n not in args.changed_frames:
                im=previous_frames[n-1];q=im.quantize(colors=256,method=Image.Quantize.MAXCOVERAGE,dither=Image.Dither.NONE)
                assert q.convert('RGB').tobytes()==im.tobytes()
                pframes.append(q);newframes.append(im);rows.append(previous_rows[n])
                for prefix in ['candidate','color-mask','color-layer']:shutil.copyfile(previous/f'{prefix}-{n:02d}.png',out/f'{prefix}-{n:02d}.png')
                continue
            original=frames[n-1];a=np.array(original);l=lab(a)
            masks,details=masks02(original,n) if name.startswith('02') else masks03(original,frames,n)
            mask=np.zeros(a.shape[:2],bool)
            for region,m in masks.items():
                mask|=m;alpha=np.minimum(distance_transform_edt(m)/1.5,1)
                target=target_lab['iris' if 'iris' in region and region!='existing_olive_bang_iris' else 'bang']
                strength=.75 if name.startswith('03') else .65
                l[:,:,1:]=l[:,:,1:]*(1-strength*alpha[:,:,None])+target*(strength*alpha[:,:,None])
            b=rgb(l);b[~mask]=a[~mask];candidate=Image.fromarray(b)
            q,slots=palette_preserve(original,candidate,mask);pframes.append(q);decoded=q.convert('RGB');newframes.append(decoded)
            assert np.array_equal(np.array(decoded)[~mask],a[~mask])
            candidate.save(out/f'candidate-{n:02d}.png');Image.fromarray(mask.astype('uint8')*255).save(out/f'color-mask-{n:02d}.png')
            rgba=np.dstack([b,mask.astype('uint8')*255]);Image.fromarray(rgba).save(out/f'color-layer-{n:02d}.png')
            rows.append({'frame':n,'mask_pixels':int(mask.sum()),'palette_new_color_slots':slots,'outside_mask_changes':0,'regions':{k:int(m.sum()) for k,m in masks.items()},'placement':details})
        if not args.prototype:
            pframes[0].save(out/'CANDIDATE-color-master-768.gif',save_all=True,append_images=pframes[1:],duration=times,loop=0,disposal=2,optimize=False)
            previews=[im.resize((112,112),Image.Resampling.LANCZOS) for im in newframes]
            previews[0].save(out/'CANDIDATE-color-preview-112.gif',save_all=True,append_images=previews[1:],duration=times,loop=0,disposal=2,optimize=False)
        cols=6;tw,th=256,278;sheet=Image.new('RGB',(cols*tw,((len(ids)+cols-1)//cols)*th),'#eee');d=ImageDraw.Draw(sheet)
        for i,(n,im,row) in enumerate(zip(ids,newframes,rows)):
            x=i%cols*tw;y=i//cols*th;sheet.paste(im.resize((256,256),Image.Resampling.LANCZOS),(x,y+22));d.text((x,y),f'F{n} mask {row["mask_pixels"]}',font=FONT,fill='black')
        sheet.save(out/'candidate-contact-256.png')
        report={'status':'pending_visual_review','source_v6_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'reference_sha256':hashlib.sha256(ref_path.read_bytes()).hexdigest(),'reference_source':'Archived n-static-laugh.png documented as Bilibili original in source a850fb4; not the model-generated six-panel sample','targets_rgb':{k:v.tolist() for k,v in targets.items()},'transform':'Preserve per-pixel Lab L*, move a*/b* toward sampled original-pack olive, strength 0.65 (02) or 0.75 (03), 1.5px inward feather; quantize only mask into unused palette slots.','frame_durations_ms':times,'frames':rows}
        (out/'construction.json').write_text(json.dumps(report,indent=2)+'\n');print(name,len(rows),'frames; slots min',min(x['palette_new_color_slots'] for x in rows),flush=True)

if __name__=='__main__':main()
