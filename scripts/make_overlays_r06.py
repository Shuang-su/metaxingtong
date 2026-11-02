from pathlib import Path
from PIL import Image
import hashlib,json
R=Path(__file__).resolve().parents[1];O=R/'stages/r06-review-candidate';cfgs=json.loads((O/'source-cameras.json').read_text());manifest=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for cfg in cfgs:
    source=R/cfg['file'];a=Image.open(source).convert('RGB');assert list(a.size)==cfg['size'];assert sha(source)==cfg['source_sha256']
    for state in ['white','material']:
        render=O/'source-renders'/cfg['id']/(state+'.png')
        if not render.exists():continue
        b=Image.open(render).convert('RGB');assert a.size==b.size,'No resizing is permitted for native direct overlays'
        out=render.with_name(state+'-direct50.png');Image.blend(a,b,.5).save(out)
        manifest.append({'id':cfg['id'],'state':state,'source':cfg['file'],'source_sha256':sha(source),'render':str(render.relative_to(R)),'render_sha256':sha(render),'overlay':str(out.relative_to(R)),'overlay_sha256':sha(out),'bytes':out.stat().st_size,'dimensions':list(a.size),'operation':'Pillow Image.blend(source RGB, render RGB, alpha=0.5) in encoded RGB; no rescale, crop, warp, local alignment, masking or retouch','status':'CONDITIONAL SOURCE COMPARISON; not source acceptance'})
(O/'overlay-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
front=next(c for c in cfgs if c['id']=='preview-front');source=R/front['file'];a=Image.open(source).convert('RGB');outdir=O/'object-crops';outdir.mkdir(exist_ok=True)
crops={'top-drum':[765,190,1220,345],'outer-ring':[580,270,1410,410],'saucer':[740,405,1260,500],'left-support':[675,470,1000,720],'right-support':[980,470,1310,720],'left-chevrons':[545,540,835,705],'right-chevrons':[1140,540,1440,705],'platform-front':[480,675,1520,780]};crop_rows=[]
for name,box in crops.items():
    ap=outdir/(name+'-source.png');a.crop(box).save(ap);row={'id':name,'source':front['file'],'original_dimensions':list(a.size),'crop_xyxy':box,'display_resampling':'none','source_crop':str(ap.relative_to(R)),'source_crop_sha256':sha(ap),'conditional_camera':True,'not_new_source_angle':True}
    for state in ['white','material']:
        p=O/'source-renders/preview-front'/(state+'.png')
        if p.exists():
            b=Image.open(p).convert('RGB');q=outdir/(name+'-'+state+'.png');b.crop(box).save(q);ov=outdir/(name+'-'+state+'-direct50.png');Image.blend(a.crop(box),b.crop(box),.5).save(ov);row[state]={'render_crop':str(q.relative_to(R)),'render_crop_sha256':sha(q),'overlay':str(ov.relative_to(R)),'overlay_sha256':sha(ov)}
    crop_rows.append(row)
(O/'object-crops-manifest.json').write_text(json.dumps(crop_rows,ensure_ascii=False,indent=2))
print('DIRECT_NATIVE_OVERLAYS_READY',len(manifest),'LOCAL_CROPS',len(crop_rows))
