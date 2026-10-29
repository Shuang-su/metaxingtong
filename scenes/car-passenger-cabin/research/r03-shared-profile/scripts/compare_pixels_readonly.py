"""Independent local pixel implementation: no fitter/BLEND reads or mutations.
Same native ROI edge tests for original B0, frozen-camera B1 and shared profile D1.
This is independent implementation, not independent source data or user acceptance.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
from scipy.ndimage import gaussian_filter,sobel,distance_transform_edt
R=Path(__file__).resolve().parents[1];S=R.parents[1]
sources=json.loads((S/'sources/source-manifest.json').read_text())['sources'];ids=['S01','S02','S03'];rows=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source_integrity=[]
for src in sources:
 p=S/src['path'];im=Image.open(p);actual=sha(p);assert actual==src['sha256'];assert im.size==(1920,1080)
 source_integrity.append({'id':src['id'],'sha256':actual,'bytes':p.stat().st_size,'dimensions':list(im.size),'role':'context_only_excluded' if src['id']=='S04' else 'side_source'})
rois={'S01':{'vent_fascia':[80,620,380,900],'dash_turn':[170,535,350,675],'heldout_mirror_region':[350,320,800,610],'A_region':[200,220,800,580],'heldout_roof':[1380,140,1780,290]},'S02':{'vent_fascia':[120,670,405,940],'dash_turn':[210,590,380,720],'A_region':[220,270,800,630]},'S03':{'vent_fascia':[240,565,500,805],'dash_turn':[320,495,480,625],'heldout_mirror_region':[500,320,850,570],'A_region':[350,200,840,540],'heldout_roof':[1380,140,1780,280]}}
def grad(im):
 v=np.asarray(im,dtype=float)/255;g=v@np.array([.2126,.7152,.0722]);g=gaussian_filter(g,1.4);return np.hypot(sobel(g,0),sobel(g,1))/8
def compare(a,b,box):
 x0,y0,x1,y1=box;aa=a[y0:y1,x0:x1];bb=b[y0:y1,x0:x1];ea=aa>max(.018,float(np.quantile(aa,.9)));eb=bb>max(.018,float(np.quantile(bb,.9)))
 row={'source_edge_pixels':int(ea.sum()),'render_edge_pixels':int(eb.sum())}
 if ea.sum()<15 or eb.sum()<15:return dict(row,status='insufficient reliable edges')
 ab=distance_transform_edt(~eb)[ea];ba=distance_transform_edt(~ea)[eb]
 return dict(row,source_to_render_mean_px=float(ab.mean()),render_to_source_mean_px=float(ba.mean()),source_to_render_p90_px=float(np.quantile(ab,.9)),render_to_source_p90_px=float(np.quantile(ba,.9)))
sheet=Image.new('RGB',(1920,768),(20,25,31));draw=ImageDraw.Draw(sheet)
for idx,id in enumerate(ids):
 src=next(x for x in sources if x['id']==id);im=Image.open(S/src['path']).convert('RGB');paths={'B0_original':S/'renders/source'/f'{id}_render_{"open" if id=="S02" else "closed"}.png','B1_frozen_camera':R/f'renders/full/B1_{id}.png','D1_shared_profile':R/f'renders/full/D1_{id}.png'}
 ims={k:Image.open(p).convert('RGB') for k,p in paths.items()};assert all(x.size==(1920,1080) for x in ims.values());g=grad(im);grads={k:grad(v) for k,v in ims.items()};blends={};blend_rows=[]
 for stage in ['B1_frozen_camera','D1_shared_profile']:
  blend=Image.blend(im,ims[stage],.5);path=R/f'comparisons/{id}_{stage}_direct_50percent_native.png';blend.save(path)
  reread=np.asarray(Image.open(path));expected=np.floor((np.asarray(im,dtype=float)+np.asarray(ims[stage],dtype=float))*.5).astype(np.uint8);assert np.array_equal(reread,expected)
  blends[stage]=blend;blend_rows.append({'stage':stage,'path':str(path.relative_to(R)),'exact_half_pixel_formula_verified':True,'sha256':sha(path)})
 panel=[(im,'SOURCE'),(ims['B0_original'],'B0 ORIGINAL'),(ims['B1_frozen_camera'],'B1 FROZEN CAMERA'),(ims['D1_shared_profile'],'D1 SHARED / DIAGNOSTIC'),(blends['D1_shared_profile'],'D1 DIRECT 50%')]
 for col,(pic,label) in enumerate(panel):sheet.paste(pic.resize((384,216),Image.Resampling.LANCZOS),(col*384,idx*256+40));draw.text((col*384+6,idx*256+12),id+' | '+label,fill='white')
 rr={}
 for name,box in rois[id].items():
  rr[name]={'native_xyxy':box,'stages':{k:compare(g,v,box) for k,v in grads.items()}}
  if name in ['vent_fascia','dash_turn','heldout_mirror_region']:
   w,h=box[2]-box[0],box[3]-box[1];strip=Image.new('RGB',(w*4,h))
   for i,pic in enumerate([im,ims['B1_frozen_camera'],ims['D1_shared_profile'],blends['D1_shared_profile']]):strip.paste(pic.crop(box),(w*i,0))
   strip.save(R/f'comparisons/{id}_{name}_native_crop_quartet.png')
 rows.append({'id':id,'source_sha256':src['sha256'],'render_sha256':{k:sha(p) for k,p in paths.items()},'rois':rr,'blends':blend_rows})
preview=R/'comparisons/r03_contact_sheet.jpg';sheet.save(R/'comparisons/r03_contact_sheet.png')
for quality in [94,90,86,82,76]:
 sheet.save(preview,quality=quality,optimize=True)
 if preview.stat().st_size<900*1024:break
report={'method':'Standalone native PNG pixel QA; no fitting functions or model coordinates imported. Gaussian sigma1.4+Sobel, local 90th percentile/min .018 edges, symmetric distances. Explicit unwarped source/render rectangles exclude character for evaluated interior features. Mirror/A ROIs also contain neighboring edges, lighting and texture; these are local image diagnostics, not object-specific geometry scores. Same source data as fitting, not independent evidence. No overall score.','all_four_native_sources_verified':source_integrity,'rows':rows,'preview':{'path':str(preview.relative_to(R)),'dimensions':[1920,768],'panel_scale':.2,'bytes':preview.stat().st_size,'sha256':sha(preview)}}
(R/'qa/pixel_readonly_qa.json').write_text(json.dumps(report,indent=2)+'\n')
print('PIXEL_QA',preview.stat().st_size)
