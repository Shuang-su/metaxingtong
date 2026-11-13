#!/usr/bin/env python3
"""Build reversible dynamic review candidates after the user's broad approval.

02: propagate registered clothing repair over all five affected frames.
03: propagate collar patches and author only the redundant knee hand area.
Original GIF timelines and pixels outside explicit per-frame masks stay exact.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.interpolate import LinearNDInterpolator
from scipy.ndimage import map_coordinates,distance_transform_edt,label
import numpy as np,json,hashlib,argparse
from try_local_candidates import ROOT,mask_polygon
from local_contour_layers import build_knee_layer

FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)

def skin_protection(im,seed_box,dilate=3):
    a=np.array(im,dtype=int);r,g,b=[a[:,:,c] for c in range(3)]
    skin=(r>170)&(g<235)&(r-g>12)&(r-b>18)
    labs,_=label(skin)
    x0,y0,x1,y1=seed_box;ids=np.unique(labs[y0:y1,x0:x1]);ids=ids[ids>0]
    selected=np.isin(labs,ids)
    return distance_transform_edt(~selected)<=dilate

def shift(im,dx,dy,resample):
    return im.transform(im.size,Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),resample=resample)

def patch02(original,base,record):
    p=base/'v5-registered-donor/trial-23-refit'
    config=json.loads((p/'registration.json').read_text())
    source=Image.open(base/'original-decoded/23.png').convert('RGB');a=np.array(original);src=np.array(source)
    sp=np.array(config['source_points']);tp=np.array(config['target_points'])
    hem,stripe=record['hem'],record['stripe']
    def move(points):
        points=np.array(points,float);t=np.clip((points[:,1]-506)/37,0,1)
        return points+np.stack([hem['dx']+(stripe['dx']-hem['dx'])*t,hem['dy']+(stripe['dy']-hem['dy'])*t],-1)
    tp=move(tp);poly=move(config['requested_polygon'])
    yy,xx=np.indices(a.shape[:2],dtype=float);coords=LinearNDInterpolator(tp,sp)(xx,yy)
    valid=np.isfinite(coords).all(-1);coords[~valid]=0
    donor=np.stack([map_coordinates(src[:,:,c].astype(float),[coords[:,:,1],coords[:,:,0]],order=1,mode='nearest') for c in range(3)],-1)
    allowed=(np.array(mask_polygon(original.size,poly.tolist()))>0)&valid
    protected=skin_protection(original,(651,486,720,534),3)
    protected[468:545,450:530]=True
    allowed&=~protected
    alpha=np.minimum(distance_transform_edt(allowed)/2,1)*allowed
    b=np.rint(a*(1-alpha[:,:,None])+donor*alpha[:,:,None]).clip(0,255).astype('uint8')
    return Image.fromarray(b),allowed,protected,{'method':'frame-specific registered donor clothing','registration':record,'target_points':tp.tolist(),'mask_polygon':poly.tolist()}

def patch03(original,base,record,n,refine_early_shoulder=False):
    a=np.array(original);b=a.copy();allowed=np.zeros(a.shape[:2],bool);protected=np.zeros_like(allowed);details={}
    # Connected skin components touching the actual reach region, plus outlines.
    reach=skin_protection(original,(330,410,435,550),3)
    if n<=27:
        placement=dict(record['shoulder'])
        overrides={1:(0,-15),2:(1,-15),3:(0,-16),4:(-1,-16),22:(-5,-9),23:(-5,-10),24:(-4,-10),25:(-2,-9),26:(-1,-9),27:(0,-10)}
        if n in overrides:
            placement.update({'dx':overrides[n][0],'dy':overrides[n][1],'manual_override':'Reviewed against finger/shoulder landmarks; rejected face-biased automatic match.'})
        dx,dy=placement['dx'],placement['dy']
        source=base/'v5-donor-assessment/shoulder-trial-refit'
        patch=shift(Image.open(source/'candidate-frame17.png').convert('RGB'),dx,dy,Image.Resampling.BICUBIC)
        sm=shift(Image.open(source/'allowed-mask.png').convert('L'),dx,dy,Image.Resampling.NEAREST)
        m=(np.array(sm)>0)&~reach
        b[m]=np.array(patch)[m];allowed|=m;protected|=reach
        details['shoulder']={'placement':placement,'base':'v5 shoulder-trial-refit as broadly accepted by user'}
        if refine_early_shoulder and n<=4:
            # Native-size review found a remaining skin tip below the collar.
            # Use the same verified clean F28 donor, with a small explicit
            # extension of the mask; no whole shoulder redraw or sleeve fill.
            config=json.loads((source/'registration.json').read_text())
            transform=np.array(config['inverse_affine_coefficients'])
            yy,xx=np.indices(a.shape[:2],dtype=float)
            coords=np.stack([xx-dx,yy-dy,np.ones_like(xx)],-1)@transform
            donor=np.array(Image.open(base/'original-decoded/28.png').convert('RGB'))
            pixels=np.stack([map_coordinates(donor[:,:,c].astype(float),[coords[:,:,1],coords[:,:,0]],order=1,mode='nearest') for c in range(3)],-1)
            poly=np.array([[257,509],[272,506],[282,510],[284,517],[274,522],[260,522],[254,516]])+np.array([dx,dy])
            remnant=(np.array(mask_polygon(original.size,poly.tolist()))>0)&~reach
            alpha=np.minimum(distance_transform_edt(remnant)/2,1)*remnant
            b=np.rint(b*(1-alpha[:,:,None])+pixels*alpha[:,:,None]).clip(0,255).astype('uint8')
            allowed|=remnant
            details['shoulder']['lower_fragment_refinement']={'donor_frame':28,'polygon':poly.tolist(),'method':'small extension using existing clean registered collar/sleeve donor'}
    if 10<=n<=33:
        dx,dy=record['knee']['dx'],record['knee']['dy']
        aligned=original.transform(original.size,Image.Transform.AFFINE,(1,0,dx,0,1,dy),resample=Image.Resampling.BICUBIC)
        layer,km,kdetails=build_knee_layer(aligned,narrow=True)
        layer=shift(layer,dx,dy,Image.Resampling.BICUBIC);km=shift(km,dx,dy,Image.Resampling.NEAREST)
        raw=np.array(layer);alpha=raw[:,:,3].astype(float)/255
        m=np.array(km)>0
        other_hand=skin_protection(original,(580,583,650,636),3)
        yy,xx=np.indices(m.shape)
        # Protect the real extended sleeve where it approaches the knee panel.
        if n<=12:
            edge=np.interp(xx,[460,470,480,490,500,510,520],[576,575,570,560,546,536,534])
        elif n>=28:
            edge=np.interp(xx,[460,470,480,490,500,510,520],[587,586,580,574,562,546,535])
        else:edge=np.full(m.shape,545)
        arm=(xx>=330)&(xx<=520)&(yy<=edge+2)&(yy>=425)
        pk=other_hand|reach|arm
        m&=~pk;alpha*=m
        b=np.rint(b*(1-alpha[:,:,None])+raw[:,:,:3]*alpha[:,:,None]).clip(0,255).astype('uint8')
        allowed|=m;protected|=pk
        details['knee']={'placement':record['knee'],'method':'new local cloth/hem contour layer plus same-frame leggings pixels',**kdetails}
    # Reassert every protected source pixel after composing both independent layers.
    b[protected]=a[protected];allowed&=~protected
    return Image.fromarray(b),allowed,protected,details

def save_loop(frames,durations,path):
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=2,optimize=False)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='dynamic-candidate');parser.add_argument('--refine-early-shoulder',action='store_true');parser.add_argument('--emotes',nargs='+',choices=['02-butterfly','03-awake'],default=['02-butterfly','03-awake']);args=parser.parse_args()
    for name in args.emotes:
        source=ROOT/'emotes/sunburst/agent-emotes'/name;base=source/'versions/20261113-local-patch-review'
        folder=base/'v6-contour-and-motion';out=folder/args.output;out.mkdir(exist_ok=False)
        manifest=json.loads((source/'manifest.json').read_text());durations=manifest['frame_durations_ms']
        registrations={r['frame']:r for r in json.loads((folder/'registration.json').read_text())}
        originals=[];candidates=[];paletted=[];masks=[];protections=[];records=[]
        for n in range(1,len(durations)+1):
            original=Image.open(base/'original-decoded'/f'{n:02d}.png').convert('RGB');originals.append(original)
            relevant=(24<=n<=28) if name=='02-butterfly' else n<=33
            if relevant:
                candidate,mask,protect,details=patch02(original,base,registrations[n]) if name=='02-butterfly' else patch03(original,base,registrations[n],n,args.refine_early_shoulder)
            else:
                candidate=original.copy();mask=np.zeros((768,768),bool);protect=mask.copy();details={}
            a=np.array(original);b=np.array(candidate);changed=np.any(a!=b,axis=-1)
            assert not np.any(changed&~mask) and not np.any(changed&protect)
            if relevant:
                candidate.save(out/f'candidate-{n:02d}.png');Image.fromarray(mask.astype('uint8')*255).save(out/f'allowed-mask-{n:02d}.png');Image.fromarray(protect.astype('uint8')*255).save(out/f'protected-{n:02d}.png')
                rgba=np.dstack([b,mask.astype('uint8')*255]);Image.fromarray(rgba).save(out/f'local-layer-{n:02d}.png')
            palette=original.quantize(colors=256,method=Image.Quantize.MAXCOVERAGE,dither=Image.Dither.NONE)
            assert palette.convert('RGB').tobytes()==original.tobytes()
            q=candidate.quantize(palette=palette,dither=Image.Dither.NONE);palette.paste(q,(0,0),Image.fromarray(mask.astype('uint8')*255))
            paletted.append(palette);masks.append(mask);protections.append(protect)
            records.append({'frame':n,'duration_ms':durations[n-1],'changed_pixels_before_quantization':int(changed.sum()),'mask_pixels':int(mask.sum()),'outside_mask_changed_pixels':0,'protected_region_changed_pixels':0,'construction':details})
        master=out/'CANDIDATE-master-768.gif';save_loop(paletted,durations,master)
        with Image.open(master) as gif:
            assert gif.n_frames==len(durations)
            for k in range(gif.n_frames):
                gif.seek(k);im=gif.convert('RGB');candidates.append(im)
                a=np.array(originals[k]);b=np.array(im);diff=np.any(a!=b,axis=-1)
                assert gif.info['duration']==durations[k] and not np.any(diff&~masks[k]) and not np.any(diff&protections[k])
                records[k]['gif_changed_pixels']=int(diff.sum())
        save_loop([im.resize((112,112),Image.Resampling.LANCZOS) for im in candidates],durations,out/'CANDIDATE-preview-112.gif')
        paired=[]
        for original,candidate in zip(originals,candidates):
            im=Image.new('RGB',(640,344),'#eee');d=ImageDraw.Draw(im);d.text((8,4),'ORIGINAL',font=FONT,fill='black');d.text((328,4),'CANDIDATE - review pending',font=FONT,fill='black')
            im.paste(original.resize((320,320),Image.Resampling.LANCZOS),(0,24));im.paste(candidate.resize((320,320),Image.Resampling.LANCZOS),(320,24));paired.append(im)
        save_loop(paired,durations,out/'comparison-motion-320.gif')
        ids=list(range(23,30)) if name=='02-butterfly' else list(range(1,35))
        for crop,label_name,size in [(None,'native-112',(112,112)),((550,470,690,565) if name=='02-butterfly' else (240,445,650,645),'detail',(280,190) if name=='02-butterfly' else (328,160))]:
            cols=7 if name=='02-butterfly' else 6;tw,th=size;sheet=Image.new('RGB',(cols*tw,((len(ids)+cols-1)//cols)*(th+22)),'#eee');d=ImageDraw.Draw(sheet)
            for k,n in enumerate(ids):
                im=candidates[n-1].crop(crop) if crop else candidates[n-1];x=k%cols*tw;y=k//cols*(th+22);sheet.paste(im.resize(size,Image.Resampling.LANCZOS),(x,y+22));d.text((x+3,y+3),f'F{n} / {durations[n-1]}ms',font=FONT,fill='black')
            sheet.save(out/f'candidate-contact-{label_name}.png')
        report={'status':'dynamic_candidate_not_final_acceptance','user_feedback_basis':'Latest 02/03 local comparisons broadly acceptable; prioritize obvious remnants and motion, do not reject over minor local variation.',
            'frame_count':len(durations),'total_ms':sum(durations),'frame_durations_ms':durations,'original_master_sha256':hashlib.sha256((source/'master.gif').read_bytes()).hexdigest(),'candidate_master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),
            'all_gif_pixels_outside_masks_unchanged':True,'all_protected_regions_unchanged':True,'browser_playback':'not attempted; earlier explicit policy block remains',
            'new_artwork_disclosure':'03 knee cloth panel/hem is authored local reconstruction; not historical source pixels.', 'frames':records}
        (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(name,'built',len(durations),'frames',sum(durations),'ms; exact protected pixels pass',flush=True)

if __name__=='__main__':main()
