"""Deterministic local composition. No image-generation service is used."""
from pathlib import Path
import sys,json,hashlib
import cv2 as cv
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
SHOT=HERE.parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(SHOT/'sources/raised-fists'))
import finish as f

def reference_motion(frames):
    base=frames[0]; rows=[]
    for i,a in enumerate(frames):
        r,g,b=a.astype('int16').transpose(2,0,1)
        skin=np.uint8((r-g>7)&(g-b>0)&(r>190)&(g>145));skin[:580]=0
        n,labels,stats,centers=cv.connectedComponentsWithStats(skin)
        hands=[(s,c) for s,c in zip(stats[1:],centers[1:]) if 610<s[1]<675 and 80<s[2]<126 and 80<s[3]<122 and s[4]>2500]
        hands=sorted(hands,key=lambda z:z[1][0])
        if len(hands)!=2:raise ValueError((i+1,[s.tolist() for s,c in hands]))
        pts=np.array([c for s,c in hands]);peaks=np.array([[c[0],s[1]] for s,c in hands])
        template=base[691:735,381:418]
        scores=cv.matchTemplate(a[651:768,281:478],template,cv.TM_CCOEFF_NORMED)
        _,score,_,loc=cv.minMaxLoc(scores)
        collar=np.array([loc[0]-100,loc[1]-40],dtype=float)
        if i==0:neutral=pts.copy();angle0=np.arctan2(*(neutral[1]-neutral[0])[::-1])
        angle=np.arctan2(*(pts[1]-pts[0])[::-1])-angle0
        rows.append(dict(frame=i+1,nailu_fist_centroids=pts.tolist(),nailu_fist_peaks=peaks.tolist(),nailu_collar_delta=collar.tolist(),collar_match_score=score,angle_rad=float(angle)))
    # Three-frame triangular filter reduces palette-threshold jitter, retaining endpoints.
    raw=np.array([[*r['nailu_collar_delta'],r['angle_rad']] for r in rows])
    smooth=raw.copy();smooth[1:-1]=(raw[:-2]+2*raw[1:-1]+raw[2:])/4
    smooth[0]=0
    for row,(dx,dy,angle) in zip(rows,smooth):
        rot=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
        pivot=np.array([400.,710.]);m=np.column_stack((rot,pivot+np.array([dx,dy])-rot@pivot))
        row['body_matrix']=m.tolist()
    return rows

def compose(i,native,first,body,fists,clean,m,row):
    if i==0:return native.astype(np.uint8)
    s=f.TRACK['frames'][i];t=f.mapping(s['nailu_eyes']);inv=cv.invertAffineTransform(t)
    nx=inv[0,0]*f.U+inv[0,1]*f.V+inv[0,2];ny=inv[1,0]*f.U+inv[1,1]*f.V+inv[1,2]
    roof=f.body_roof(s)
    patch=f.warp(f.ease(f.Y,roof-23,roof-14).astype('float32'),t,768)
    patch=np.maximum(patch,((ny>438)&((nx<2)|(nx>510)|(ny>510))).astype('float32'))
    dx1=s['left'][0];dx2=s['right'][0]
    dx=np.interp(f.X[0],[90,192,315,417],[dx1,dx1,dx2,dx2]).astype('float32');falloff=f.ease(f.Y,330,399)
    donor=cv.remap(clean,f.X-dx*falloff,f.Y-(s['chin']-391)*falloff,cv.INTER_LINEAR)
    lower=f.warp(donor,t,768)
    far=np.clip(f.ease(f.X,365+dx2,421+dx2)+1-f.ease(f.X,74+dx1,128+dx1),0,1);far=f.warp(far,t,768)
    ink=1-f.ease(native.min(2),159,204)
    alpha=lower[:,:,3]/255.*(1-far*(1-ink))
    # Retain donor hair alpha even where the old cuff/background was white.
    # Match the neck overlap to the real jaw at the moving collar's x.
    # Reference motion controls lateral movement and rotation; this vertical
    # registration accommodates Xingtong's different chin/neck proportions.
    moving=cv.warpAffine(body,m,(768,768),flags=cv.INTER_LINEAR,borderMode=cv.BORDER_REPLICATE)
    cx=int(round((m@np.array([400.,680.,1.]))[0]))
    rr,gg,bb=native.transpose(2,0,1)
    skin=np.uint8((rr-gg>10)&(gg-bb>0)&(rr>180)&(gg>100))
    _,labels,stats,_=cv.connectedComponentsWithStats(skin)
    face_id=1+np.argmax(stats[1:,4]);skin=labels==face_id
    jaw=[];tops=[]
    for x in range(cx-6,cx+7):
        ys=np.where(skin[560:720,x])[0]
        if len(ys):jaw.append(ys[-1]+560)
        r,g,b=moving[:,:,0],moving[:,:,1],moving[:,:,2]
        ys=np.where(((r-g>12)&(g-b>2)&(r>180))[610:720,x])[0]
        if len(ys):tops.append(ys[0]+610)
    correction=float(np.clip(np.median(jaw)-np.median(tops)-4,-85,12)) if jaw and tops else 0.
    m=m.copy();m[1,2]+=correction
    row['jaw_registration_dy']=correction
    row['final_body_matrix']=m.tolist()
    row['jaw_y']=float(np.median(jaw)) if jaw else None
    row['neck_top_before_y']=float(np.median(tops)) if tops else None
    moving=cv.warpAffine(body,m,(768,768),flags=cv.INTER_LINEAR,borderMode=cv.BORDER_REPLICATE)
    # The neck is in front of rear hair, below the moving jaw; the lateral locks stay outside.
    neck=np.zeros((768,768),np.uint8);cv.fillPoly(neck,[np.int32([[357,647],[445,647],[448,728],[356,728]])],1)
    neck=f.warp(neck.astype('float32'),m,768)*f.ease(ny,s['chin']-2,s['chin']+2)
    alpha*=1-neck
    cover=f.mix(moving,lower[:,:,:3],alpha)
    cover=f.mix(cover,native,far*ink*(1-f.ease(ny,418,435)))
    result=f.mix(native,cover,patch)
    # Move complete fist/cuff/shoulder surfaces together. No isolated knuckle warp.
    front=cv.warpAffine(fists,m,(768,768),flags=cv.INTER_LINEAR,borderMode=cv.BORDER_REPLICATE)
    result=f.mix(result,moving,front)
    return np.uint8(np.clip(np.rint(result),0,255))

def main():
    orig,ds,pal=f.read_gif(f.ORIGINAL/'master.gif');nailu,nds,_=f.read_gif(SHOT.parent/'10-pout/master.gif');assert ds==nds
    motion=reference_motion(nailu)
    (HERE/'motion.json').write_text(json.dumps(motion,indent=2)+'\n')
    first=orig[0].astype('float32');body,fists=f.paint_first_body(first)
    plate=np.array(Image.open(f.HERE/'underlap.png').convert('RGB')).astype('float32')
    extended=cv.warpAffine(plate,np.array(f.TRACK['body_to_first']),(768,960),flags=cv.INTER_LINEAR,borderValue=(255,255,255))
    extended[:768]=body;body=extended
    clean=np.array(f.restore_head().resize((512,512),Image.Resampling.LANCZOS))
    fixed=[compose(i,a.astype('float32'),first,body,fists,clean,np.array(row['body_matrix']),row) for i,(a,row) in enumerate(zip(orig,motion))]
    (HERE/'motion.json').write_text(json.dumps(motion,indent=2)+'\n')
    f.indexed(fixed,orig,pal,HERE/'master.gif',ds)
    g=Image.open(HERE/'master.gif');decoded=[]
    for i in range(54):g.seek(i);decoded.append(g.convert('RGB').copy())
    if '--draft' in sys.argv:
        inds=[0,10,16,17,18,19,20,24];sheet=Image.new('RGB',(768,len(inds)*276),'white');d=ImageDraw.Draw(sheet)
        for r,i in enumerate(inds):
            for c,img in enumerate([Image.fromarray(f.ink_grade(orig[i])),decoded[i],Image.fromarray(nailu[i])]):sheet.paste(img.resize((256,256)),(c*256,r*276))
            d.text((4,r*276+256),str(i+1),fill='black')
        sheet.save(HERE/'draft.jpg',quality=92)
        return
    def save(images,path):images[0].save(path,save_all=True,append_images=images[1:],duration=ds,loop=0,disposal=1,optimize=False)
    chats=[a.resize((320,320),Image.Resampling.LANCZOS) for a in decoded];save(chats,HERE/'chat.gif')
    paired=[]
    for a,b in zip(chats,nailu):
        im=Image.new('RGB',(640,320),'white');im.paste(a,(0,0));im.paste(Image.fromarray(b).resize((320,320),Image.Resampling.LANCZOS),(320,0));paired.append(im)
    save(paired,HERE/'paired.gif')
    save([a.resize((112,112),Image.Resampling.LANCZOS) for a in decoded],HERE/'review-112.gif')
    sheet=Image.new('RGB',(768,54*280),'white');d=ImageDraw.Draw(sheet)
    for i,(a,b,c) in enumerate(zip(orig,decoded,nailu)):
        for col,img in enumerate([Image.fromarray(a),b,Image.fromarray(c)]):sheet.paste(img.resize((256,256),Image.Resampling.LANCZOS),(col*256,i*280))
        d.text((4,i*280+258),f'{i+1:02}  {ds[i]}ms   original / repaired / nailu',fill='black')
    sheet.save(HERE/'pose-comparison.jpg',quality=93)
    annotated=Image.new('RGB',(640,4*344),'white');pen=ImageDraw.Draw(annotated)
    for k,i in enumerate([0,10,16,17,18,19,20,24]):
        row=motion[i];m=np.array(row.get('final_body_matrix',row['body_matrix']))
        image=decoded[i].copy();draw=ImageDraw.Draw(image)
        # Source-layer anchors are marked as transformed predictions, not independent detections.
        for name,point,color in [('collar',(400,718),'#00a060'),('L peak',(300,675),'#e04020'),('R peak',(490,660),'#e04020'),('L cuff',(270,753),'#2060e0'),('R cuff',(502,749),'#2060e0')]:
            x,y=m@np.array([*point,1]);draw.ellipse((x-4,y-4,x+4,y+4),fill=color);draw.text((x+6,y-15),name,fill=color)
        cx=(m@np.array([400,680,1]))[0];cy=row.get('jaw_y',685)
        draw.ellipse((cx-4,cy-4,cx+4,cy+4),fill='#ff00aa');draw.text((cx+6,cy-18),'jaw sample',fill='#ff00aa')
        x=k%2*320;y=k//2*344;annotated.paste(image.resize((320,320),Image.Resampling.LANCZOS),(x,y));pen.text((x+4,y+322),f'frame {i+1}: jaw sample / layer anchors',fill='black')
    annotated.save(HERE/'key-poses.jpg',quality=94)
    sums=[]
    for name in ['master.gif','chat.gif','paired.gif','review-112.gif','pose-comparison.jpg','motion.json','generate.py','key-poses.jpg']:
        p=HERE/name;sums.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+name)
    (HERE/'SHA256SUMS').write_text('\n'.join(sums)+'\n')
if __name__=='__main__':main()
