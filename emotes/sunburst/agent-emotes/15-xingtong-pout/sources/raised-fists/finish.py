"""Color the approved picture in place and register its first fists on the original GIF."""
import sys
from pathlib import Path

import cv2 as cv
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SOURCES = HERE.parent
SHOT = SOURCES.parent
ORIGINAL = SHOT / "versions/01-original"
REFS = SHOT.parent / "references"
sys.path.insert(0, str(SOURCES / "restored-detail"))
from restore import restore_head
from render import digest, read, save

TRACK = read(HERE / "tracking.json")
NEUTRAL = np.array(TRACK["reference_eyes"])
Y, X = np.mgrid[:512, :512].astype("float32")
V, U = np.mgrid[:768, :768].astype("float32")


def ease(value, low, high):
    t = np.clip((value-low)/(high-low), 0, 1)
    return t*t*(3-2*t)


def mix(a, b, weight):
    return a+(b-a)*weight[..., None]


def ink_grade(colors, hair_region=1, sleeve_region=1):
    """Retain the old luminance gradients and shift only purple-leaning paints."""
    a = colors.astype(np.float32)
    r,g,b = np.moveaxis(a,-1,0)
    y = .2126*r+.7152*g+.0722*b
    # Low-chroma silver, distinct from the saturated purple headband and blue eyes.
    hair = (ease(b-g,1,10) * (1-ease(b-g,41,73)) * (1-ease(b-r,14,30))
            * ease(b-r,-1,3) * ease(y,47,109) * hair_region)
    # Blue-lilac knit is more saturated than the base color of the hair.
    sleeve = (ease(b-g,10,33) * ease(b-r,10,27) * (1-ease(r-g,31,53))
              * (1-ease(b-g,67,103)) * ease(y,91,158) * sleeve_region)
    silver = np.stack((y+.9,y-.9,y+5.1),axis=-1)
    blue = np.stack((y-2.8,y-.9,np.minimum(255,y+31)),axis=-1)
    corrected = mix(a,silver,.96*hair)
    corrected = mix(corrected,blue,.96*sleeve)
    return np.uint8(np.clip(np.rint(corrected),0,255))


def portrait():
    raw = np.array(Image.open(SOURCES/"previous-portrait.png").convert("RGB"))
    y,x = np.mgrid[:1024,:1024]
    # Collar, skin, eyes and the colored mascot are protected geographically.
    hair_bottom = np.interp(x[0],[0,130,185,266,324,355,675,705,790,855,990,1024],
                             [787,841,793,770,743,697,697,742,766,809,809,790])
    hair = 1-ease(y,hair_bottom-6,hair_bottom+2)
    for l,t,r,b in [(266,540,458,644),(563,528,763,638),(600,20,795,175)]:
        hair[t:b,l:r]=0
    # A soft boundary inside the knit keeps the white fur collar intact.
    sleeve_top=np.interp(x[0],[0,175,220,273,313,357,400,475,510,550,600,650,716,770,822,875,1023],
                         [1025,966,904,887,827,820,840,864,956,874,849,822,849,879,900,960,1025])
    sleeve=ease(y,sleeve_top-3,sleeve_top+7)
    edited=ink_grade(raw,hair,sleeve)
    Image.fromarray(edited).save(REFS/"xingtong-detailed.png")
    same=(raw==edited).all(2)
    for x1,y1,x2,y2 in [(300,560,453,634),(583,557,681,626),(384,752,440,801),(585,757,625,805)]:
        assert same[y1:y2,x1:x2].all()
    return dict(source_sha256=digest((SOURCES/"previous-portrait.png").read_bytes()),
                result_sha256=digest((REFS/"xingtong-detailed.png").read_bytes()),
                size=[1024,1024],pixels_changed_by_color=int((~same).sum()),coordinate_transform="identity")


def mapping(eyes):
    a=NEUTRAL[1]-NEUTRAL[0]
    target=np.array(eyes)*1.5
    b=target[1]-target[0]
    theta=np.arctan2(b[1],b[0])-np.arctan2(a[1],a[0])
    m=np.linalg.norm(b)/np.linalg.norm(a)*np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
    return np.column_stack((m,target[0]-m@NEUTRAL[0]))


def warp(a,t,size,background=0):
    return cv.warpAffine(a,t,(size,size),flags=cv.INTER_LINEAR,borderValue=background)


def paint_first_body(first):
    plate=np.array(Image.open(HERE/"underlap.png").convert("RGB"))
    back=warp(plate,np.array(TRACK["body_to_first"]),768,(252,252,252)).astype("float32")
    # Inside the original two cuffs and collar keep the native first-frame texture.
    x=[0,66,76,84,99,111,129,151,175,205,224,245,261,278,297,319,331,351,375,401,423,438,451,468,494,516,530,551,564,582,603,622,641,661,678,695,710,723,767]
    y=[830,794,758,752,726,715,708,705,706,699,696,690,686,680,673,676,690,698,703,702,697,688,681,670,656,661,668,686,690,697,690,686,681,689,701,707,733,780,830]
    boundary=np.interp(U[0],x,y)
    body=mix(back,first,ease(V,boundary+3,boundary+8)*ease(U,197,234)*(1-ease(U,554,597)))
    fist=np.array(Image.open(HERE/"first-fists.png")).astype("float32")/255.
    fist=cv.GaussianBlur(fist,(3,3),.55)
    for l,r in [(234,379),(419,561)]:
        fist[:,l:r]=np.maximum.accumulate(fist[:,l:r],axis=0)
    return body,fist


def body_roof(sample):
    dx1,dy1=sample["left"]
    dx2,dy2=sample["right"]
    chin=sample["chin"]
    x=np.array([-80,22,58,74,86,99,122,146,163,176,185,194,201,209,221,232,247,257,270,281,292,303,314,323,334,348,370,393,405,418,430,445,479,585])
    y=np.array([540,508,446,421,409,402,394,391,390,394,387,382,381,382,388,394,397,398,397,393,386,382,381,383,389,395,394,397,403,412,435,459,515,555])
    mx=(dx1+dx2)/2
    my=(dy1+dy2)/2
    ox=np.interp(x,[20,117,201,309,400,500],[mx,dx1,dx1,dx2,dx2,mx])
    oy=np.interp(x,[10,118,201,253,309,395,500],[my,dy1,dy1,chin-398,dy2,dy2,my])
    return np.minimum(np.interp(X[0],x+ox,y+oy),440)


def repair(i, native, first, body, fists, clean):
    if i==0:
        return native.copy()
    s=TRACK["frames"][i]
    t=mapping(s["nailu_eyes"])
    inv=cv.invertAffineTransform(t)
    nx=inv[0,0]*U+inv[0,1]*V+inv[0,2]
    ny=inv[1,0]*U+inv[1,1]*V+inv[1,2]
    roof=body_roof(s)
    patch=warp(ease(Y,roof-23,roof-14).astype("float32"),t,768)
    patch=np.maximum(patch,((ny>438)&((nx<2)|(nx>510)|(ny>510))).astype("float32"))
    dx1=s["left"][0];dx2=s["right"][0]
    dx=np.interp(X[0],[90,192,315,417],[dx1,dx1,dx2,dx2]).astype("float32")
    falloff=ease(Y,330,399)
    donor=cv.remap(clean,X-dx*falloff,Y-(s["chin"]-391)*falloff,cv.INTER_LINEAR)
    lower=warp(donor,t,768)
    far=np.clip(ease(X,365+dx2,421+dx2)+1-ease(X,74+dx1,128+dx1),0,1)
    far=warp(far,t,768)
    ink=1-ease(native.min(2),159,204)
    alpha=lower[:,:,3]/255.*(1-far*(1-ink))
    # A donor lock cannot extend the old hair silhouette into the original white background.
    edgewhite=np.pad(np.uint8(native.min(2)>249),1,constant_values=1)
    cv.floodFill(edgewhite,None,(0,0),2)
    alpha[edgewhite[1:-1,1:-1]==2]=0
    cover=mix(body,lower[:,:,:3],alpha)
    cover=mix(cover,native,far*ink*(1-ease(ny,418,435)))
    result=mix(mix(native,cover,patch),first,fists)
    return np.uint8(np.clip(np.rint(result),0,255))


def packed(a):
    return a.astype(np.int32)@np.array([65536,256,1],dtype=np.int32)


def indexed(frames, native_frames, palette, path, timings):
    # Exact palette indices for untouched original drawing pixels. Only newly
    # exposed small patches need nearest-color assignment.
    old=packed(palette)
    order=np.argsort(old)
    keys=old[order]
    cube=np.indices((64,64,64),dtype=np.float32).reshape(3,-1).T.copy()*4+1.5
    _,match=cv.batchDistance(cube,palette.astype(np.float32),cv.CV_32F,K=1)
    table=match.reshape(64,64,64).astype(np.uint8)
    target=ink_grade(palette)
    images=[]
    retained=[]
    for arr,orig in zip(frames,native_frames):
        same=(arr==orig).all(2)
        color=packed(arr)
        at=np.minimum(len(keys)-1,np.searchsorted(keys,color))
        exact=keys[at]==color
        rr,gg,bb=(arr//4).transpose(2,0,1)
        idx=np.where(exact,order[at],table[rr,gg,bb]).astype(np.uint8)
        assert exact[same].all()
        image=Image.fromarray(idx);image.putpalette(target.ravel().tolist())
        images.append(image)
        retained.append(round(float(same.mean()),5))
    images[0].save(path,save_all=True,append_images=images[1:],duration=timings,loop=0,disposal=1,optimize=False)
    return retained


def read_gif(path):
    with Image.open(path) as g:
        pal=np.asarray(g.getpalette(),dtype=np.uint8).reshape(-1,3)
        frames=[];timings=[]
        for i in range(g.n_frames):
            g.seek(i);frames.append(np.array(g.convert("RGB")));timings.append(g.info["duration"])
        return frames,timings,pal


def render():
    static=portrait()
    frames,ds,pal=read_gif(ORIGINAL/"master.gif")
    small,other,small_pal=read_gif(ORIGINAL/"chat.gif")
    assert ds==other==read(SHOT.parent/"10-pout/manifest.json")["frame_durations_ms"]
    first=frames[0].astype("float32")
    body,fists=paint_first_body(first)
    clean=np.array(restore_head().resize((512,512),Image.Resampling.LANCZOS))
    fixes=[repair(i,f.astype("float32"),first,body,fists,clean).astype(np.uint8) for i,f in enumerate(frames)]
    # Work in original chat pixels away from the repaired area, including the
    # original crop and first frame. Place its own first-frame fists on top.
    size=(320,320)
    front=cv.resize(fists,size,interpolation=cv.INTER_AREA)
    chats=[]
    for old,large,fix in zip(small,frames,fixes):
        changed=np.any(large!=fix,axis=2).astype("float32")
        touched=cv.resize(cv.dilate(changed,np.ones((5,5),np.uint8)),size,interpolation=cv.INTER_AREA)
        patched=np.array(Image.fromarray(fix).resize(size,Image.Resampling.LANCZOS)).astype("float32")
        updated=mix(old.astype("float32"),patched,touched)
        chats.append(np.uint8(np.rint(mix(updated,small[0],front))))
    reviewed=read(HERE/"source-records.json")
    assets=[];fractions={}
    for name,source,corrected,colors in [("master.gif",frames,fixes,pal),("chat.gif",small,chats,small_pal)]:
        p=SHOT/name
        fractions[name]=indexed(corrected,source,colors,p,ds)
        assets.append(dict(file=name,size=list(source[0].shape[:2]),bytes=p.stat().st_size,sha256=digest(p.read_bytes())))
    rows=[]
    sheet=Image.new("RGB",(1024,1036),"#eeebe8");pen=ImageDraw.Draw(sheet)
    with Image.open(SHOT/"master.gif") as g:
        assert g.n_frames==54
        for i,sample in enumerate(TRACK["frames"]):
            g.seek(i);fr=g.convert("RGB");fn=f"frames/{i+1:02}.png";fr.save(SHOT/fn)
            src=dict(original_frame=i+1,original_file="versions/01-original/master.gif")
            if i%6==0:src["key"]=i//6+1
            rows.append(dict(frame=i+1,file=fn,source=src,duration_ms=ds[i],pixel_sha256=digest(fr.tobytes())))
            x=i%8*128;y=i//8*148;sheet.paste(fr.resize((128,128),Image.Resampling.LANCZOS),(x,y));pen.text((x+4,y+130),f"{i+1:02}  {ds[i]} ms",fill="#302f37")
    sheet.save(SHOT/"frames.jpg",quality=93)
    cli=dict(method="Sunburst imagegen CLI edit",model="gpt-image-2.6-sunburst",source="sources/previous-portrait.png",file="sources/raised-fists/underlap.png",prompt=(HERE/"underlap.txt").read_text().strip(),mask="sources/raised-fists/underlap-mask.png",sha256=digest((HERE/"underlap.png").read_bytes()))
    save(SHOT/"manifest.json",dict(title="星瞳·鼓脸晃头",file="master.gif",chat_file="chat.gif",sha256=assets[0]["sha256"],size=[768,768],frames=54,different_frames=len({r["pixel_sha256"] for r in rows}),total_ms=sum(ds),loop=0,frame_durations_ms=ds,assets=assets,frame_review=rows,images_api=reviewed,images_cli=dict(hidden_body=cli),clean_jaw_source="sources/restored-detail/fill.png",sync_source="10-pout",storyboard="storyboard.json",method="在初版 GIF 原帧上校色，只修理偏头时跟着侧飞的双拳、袖口及其遮挡区域。",static=static,original_pixel_fraction_before_color=fractions))
    save(SHOT/"matched-motion.json",dict(partner="10-pout",method="沿用原 GIF 的相机、头部、眼线和每帧时值，双拳取初版首帧。",frames=TRACK["frames"]))
    save(REFS/"xingtong-detailed.json",dict(file="xingtong-detailed.png",sha256=static["result_sha256"],size=[1024,1024],source="../15-xingtong-pout/sources/previous-portrait.png",source_sha256=static["source_sha256"],method="同坐标局部色彩变换"))


if __name__=="__main__":
    render()
