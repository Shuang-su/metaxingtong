"""Restore the first portrait and animate it above a stationary pair of hands."""
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
SOURCES = HERE.parent
SHOT = SOURCES.parent
REFS = SHOT.parent / "references"
sys.path.insert(0, str(SOURCES / "fixed-hands"))
from render import digest, encode, read, save

LANCZOS = Image.Resampling.LANCZOS
MOUTHS = [(257,316,19,12), (253,308,24,16), (218,308,17,15),
          (225,305,18,14), (258,304,23,15), (290,310,19,10),
          (261,318,17,21), (258,320,18,22), (261,315,19,13)]
CHANGES = [0, 5, 9, 14, 21, 30, 36, 42, 48]


def ease(value):
    t = np.clip(value, 0, 1)
    return t*t*(3-2*t)


def restore_head():
    original = Image.open(SOURCES / "previous-portrait.png").convert("RGB")
    repair = np.asarray(Image.open(HERE / "fill.png").convert("RGB"))
    yy, xx = np.mgrid[:1024, :1024].astype(np.float32)
    # Place the newly exposed underside of the jaw at the height of the old chin.
    # Only the lower clean-up plate is sampled here; the original is copied on top.
    chin = 45 * ease((yy-700)/80) * ease((xx-267)/192) * ease((756-xx)/192)
    repair = cv2.remap(repair, xx, yy+chin, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    protected = Image.open(HERE / "mask.png").getchannel("A").filter(ImageFilter.GaussianBlur(2))
    head = np.array(Image.composite(original, Image.fromarray(repair), protected))
    low = head.min(2)
    outside = (low > 203).astype(np.uint8)
    cv2.floodFill(outside, None, (0, 0), 2)
    exterior = outside == 2
    opacity = np.ones(low.shape, np.float32)
    opacity[exterior] = np.clip((250.0-low[exterior])/200.0, 0, 1)
    rgb = 255-(255.-head)/np.maximum(opacity[...,None], 1/255)
    return Image.fromarray(np.uint8(np.dstack((np.clip(rgb,0,255), np.round(opacity*255)))))


def correct_paints(layer, fabric=False):
    rgb = np.asarray(layer.convert("RGB"), dtype=np.float32)
    r, g, b = rgb.transpose(2,0,1)
    # Work at constant luminance. Original highlights, individual strands, and
    # delicate ink lines retain the value differences that give them their shape.
    lum = .2126*r + .7152*g + .0722*b
    if fabric:
        area = ease((b-g-7)/32) * ease((b-r-4)/22) * ease((lum-62)/80)
        target = np.stack((lum-1, lum+.6, np.minimum(lum+33,255)), axis=-1)
    else:
        # Blue eyes and the deliberately violet headband have substantially higher chroma.
        area = (ease((b-g-2)/10) * (1-ease((b-g-41)/31)) *
                (1-ease((b-r-15)/40)) * ease((lum-47)/55))
        target = np.stack((lum+.9,lum-.9,lum+5.1),axis=-1)
    output = rgb + (target-rgb)*area[...,None]*.96
    result = Image.fromarray(np.uint8(np.clip(np.round(output),0,255)))
    result.putalpha(layer.getchannel("A"))
    return result


def original_expressions(head):
    sheet = Image.open(SOURCES / "keys.png").convert("RGB")
    neutral = np.array(head.convert("RGB"))
    # Remove only the existing mouth ink before placing an exposed replacement.
    old = neutral[661:705,503:548]
    ink = np.uint8((old.min(2)<220) & (old[:,:,0].astype(int)-old[:,:,1]>14))*255
    mask = np.zeros(neutral.shape[:2],np.uint8)
    mask[661:705,503:548] = cv2.dilate(ink, np.ones((5,5),np.uint8))
    cleared = cv2.inpaint(neutral, mask, 3, cv2.INPAINT_TELEA).astype(float)
    heads = []
    for i,(x,y,w,h) in enumerate(MOUTHS):
        if i in (0,8):
            heads.append(head)
            continue
        x += (i%3)*512
        y += (i//3)*512
        margin = 7
        patch = sheet.crop((x-margin,y-margin,x+w+margin,y+h+margin))
        patch = patch.resize((round(patch.width*1.89), round(patch.height*1.89)), LANCZOS)
        pix = np.array(patch, dtype=float)
        ring = np.concatenate([pix[:4].reshape(-1,3),pix[-4:].reshape(-1,3)])
        delta = pix - np.median(ring,axis=0)
        # Copy just source mouth ink and fill, with clean edges on the original skin tone.
        strength = ease((-np.min(delta,axis=2)-9)/28)
        rgb = cleared.copy()
        px, py = 525-patch.width//2, 683-patch.height//2
        tile = rgb[py:py+patch.height,px:px+patch.width]
        tile += delta*strength[...,None]
        cel = Image.fromarray(np.uint8(np.clip(rgb,0,255)))
        cel.putalpha(head.getchannel("A"))
        heads.append(cel)
    return heads


def compose(head,body,angle,bob,size):
    # A shallow tabletop pose keeps the choker and pearls visible under the chin.
    scale = size/768
    def px(v):
        return round(v*scale)
    canvas = Image.new("RGBA",(size,size),"white")
    canvas.alpha_composite(body.resize((px(594),px(488)),LANCZOS),(px(87),px(303)))
    moving = Image.new("RGBA",(size,size))
    moving.alpha_composite(head.resize((px(671),px(671)),LANCZOS),(px(48.5),px(6+bob)))
    moving = moving.rotate(-angle,Image.Resampling.BICUBIC,center=(px(384),px(510)))
    canvas.alpha_composite(moving)
    return canvas.convert("RGB")


def render():
    samples = read(SOURCES / "fixed-hands/motion-input.json")["samples"]
    timings = [s["duration_ms"] for s in samples]
    observed = []
    for s in samples:
        a,b = s["eyes"]
        observed.append(math.degrees(math.atan2(b[1]-a[1],b[0]-a[0])))
    head = restore_head()
    # Identity check before grading or posing: original RGB in the face and bangs.
    original = Image.open(SOURCES / "previous-portrait.png").convert("RGB")
    proof = []
    for name,box in [("eyes_and_cheeks",(269,546,726,662)),("bangs",(332,243,648,464))]:
        before = original.crop(box).tobytes()
        after = head.convert("RGB").crop(box).tobytes()
        assert before == after
        proof.append(dict(area=name,box=box,sha256=digest(after)))
    heads = original_expressions(correct_paints(head))
    body = correct_paints(Image.open(HERE / "arms.png").convert("RGBA"), fabric=True)
    frames, review, motion = [], [], []
    for i,s in enumerate(samples):
        angle = sum(w*observed[(i+j-3)%len(samples)] for j,w in enumerate((1,2,3,4,3,2,1)))/16*.81
        bob = 1.5*math.sin(2*math.pi*sum(timings[:i])/sum(timings)-.4)
        key = max(k for k,v in enumerate(CHANGES) if i>=v)
        frames.append(compose(heads[key],body,angle,bob,768))
        if i==0:
            compose(heads[key],body,angle,bob,1024).save(REFS / "xingtong-detailed.png")
        src = dict(original_mouth_cell=key+1,clockwise_deg=round(angle,6),head_y_offset=round(bob,5))
        if i in CHANGES:
            src["key"] = key+1
        motion.append(dict(frame=i+1,reference_frame=i+1,nailu_eyes=s["eyes"],**src))
        review.append(dict(frame=i+1,file=f"frames/{i+1:02d}.png",source=src,duration_ms=timings[i]))
    assets = [encode(SHOT / fn,frames,width,timings) for fn,width in [("master.gif",768),("chat.gif",320)]]
    contact = Image.new("RGB",(1024,1036),"#edeae7")
    pen = ImageDraw.Draw(contact)
    with Image.open(SHOT / "master.gif") as g:
        assert g.n_frames == len(frames)
        for i,row in enumerate(review):
            g.seek(i)
            f = g.convert("RGB")
            f.save(SHOT / row["file"])
            row["pixel_sha256"] = digest(f.tobytes())
            x,y = i%8*128,i//8*148
            contact.paste(f.resize((128,128),LANCZOS),(x,y))
            pen.text((x+4,y+130),f"{i+1:02}  {timings[i]} ms",fill="#313039")
    contact.save(SHOT / "frames.jpg",quality=94)
    save(SHOT / "matched-motion.json",dict(partner="10-pout",method="仅头和表情移动，双手与衣身保持固定。",frames=motion))
    receipt = read(SOURCES / "previous-portrait.json")
    receipt["file"] = "sources/previous-portrait.png"
    cli = {}
    for name,refs in [("arms",["sources/previous-portrait.png","sources/fixed-hands/body.png"]),
                      ("fill",["sources/previous-portrait.png"])]:
        cli[name] = dict(tool="imagegen CLI edit",model=receipt["model"],size="1024x1024",quality="high",
                         background="transparent" if name=="arms" else "opaque",reference_files=refs,
                         file=str((HERE/(name+".png")).relative_to(SHOT)),
                         prompt=(HERE/(name+".txt")).read_text().strip(),sha256=digest((HERE/(name+".png")).read_bytes()))
    cli["fill"]["mask"] = "sources/restored-detail/mask.png"
    save(SHOT/"manifest.json",dict(title="星瞳·鼓脸晃头",file="master.gif",chat_file="chat.gif",
          sha256=assets[0]["sha256"],size=[768,768],frames=len(review),
          different_frames=len({x["pixel_sha256"] for x in review}),total_ms=sum(timings),loop=0,
          frame_durations_ms=timings,assets=assets,sync_source="10-pout",storyboard="storyboard.json",
          images_api=dict(portrait=receipt,keys=read(HERE/"keys-receipt.json")),images_cli=cli,
          identity_before_color_grade=proof,frame_review=review,
          method="从初版 1024 原画保留面部、刘海与外轮廓，嘴形引自初版分镜。仅补齐下颌和发尾遮挡，手与衣身单独固定。"))
    save(REFS/"xingtong-detailed.json",dict(file="xingtong-detailed.png",size=[1024,1024],sha256=digest((REFS/"xingtong-detailed.png").read_bytes()),
          source_portrait_sha256=receipt["sha256"],source_receipts="../15-xingtong-pout/manifest.json",model=receipt["model"]))


if __name__=="__main__":
    render()
