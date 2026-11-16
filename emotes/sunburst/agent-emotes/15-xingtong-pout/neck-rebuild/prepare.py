"""Prepare an exact 1024px frame-17 Images API trial and conservative RGBA mask."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import cv2 as cv
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
SHOT=HERE.parent
sys.path.insert(0,str(SHOT/'sources/raised-fists'))
import finish as old

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    src=HERE/'sources';src.mkdir(parents=True,exist_ok=True)
    g=Image.open(SHOT/'versions/01-original/master.gif');g.seek(16);main=g.convert('RGB')
    ref=Image.open(SHOT.parent/'10-pout/master.gif');ref.seek(16)
    main.resize((1024,1024),Image.Resampling.LANCZOS).save(src/'xingtong-17-1024.png')
    ref.convert('RGB').resize((1024,1024),Image.Resampling.LANCZOS).save(src/'nailu-17-1024.png')
    poly=[(0,507),(53,520),(98,541),(141,539),(179,546),(212,583),(218,621),(261,638),(324,647),(397,650),(431,679),(492,709),(538,746),(538,768),(0,768)]
    region=Image.new('L',(768,768),0);ImageDraw.Draw(region).polygon(poly,fill=255)
    a=np.array(main).astype(np.int16);r,g,b=a.transpose(2,0,1)
    skin=np.uint8((r-g>10)&(g-b>0)&(r>180)&(g>100));_,labels,stats,_=cv.connectedComponentsWithStats(skin);face=labels==(1+np.argmax(stats[1:,4]))
    protect=cv.dilate(np.uint8(face),np.ones((3,3),np.uint8))>0
    opened=np.array(region);opened[protect]=0
    editable=Image.fromarray(opened).resize((1024,1024),Image.Resampling.NEAREST)
    mask=Image.new('RGBA',(1024,1024),(255,255,255,255));mask.putalpha(Image.fromarray(255-np.array(editable)));mask.save(src/'mask-17-1024.png')
    view=np.array(main.resize((1024,1024),Image.Resampling.LANCZOS));weight=np.array(editable)/255*.40
    tint=np.zeros_like(view);tint[:]=[255,45,65];overlay=view*(1-weight[...,None])+tint*weight[...,None]
    Image.fromarray(np.uint8(np.rint(overlay))).resize((768,768),Image.Resampling.LANCZOS).save(HERE/'mask-review.jpg',quality=94)
    inputs={p.name:{'sha256':sha(p),'size':list(Image.open(p).size),'mode':Image.open(p).mode} for p in [src/'xingtong-17-1024.png',src/'nailu-17-1024.png',src/'mask-17-1024.png']}
    report=dict(frame=17,input_commit='4ef01476009277a97aa1823ffee1262b6f53a688',source_frame_size=[768,768],input_transform={'scale':4/3,'offset':[0,0]},mask_convention='RGBA alpha=0 editable; alpha=255 protected',editable_pixels=int((np.array(editable)>0).sum()),protected_face_pixels=int(protect.sum()),mask_polygon_768=poly,inputs=inputs)
    (HERE/'prepared-input.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
