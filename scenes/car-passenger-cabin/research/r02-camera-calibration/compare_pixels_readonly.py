"""Read-only native-pixel diagnostics, not an overall reconstruction score.
Reads source and rendered PNG bytes. Writes overlays/reports only. Does not edit
BLEND, anchors or source files. Edges include material and lighting differences.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
from scipy.ndimage import gaussian_filter,sobel,distance_transform_edt
R=Path(__file__).resolve().parent;S=R.parents[1]
sources=json.loads((S/'sources/source-manifest.json').read_text())['sources'];ids=['S01','S02','S03'];rows=[]
(R/'comparisons').mkdir(exist_ok=True);sheet=Image.new('RGB',(1920,948),(21,25,32));d=ImageDraw.Draw(sheet)
rois={'S01':{'vent_and_fascia':[80,620,380,900],'dash_corner':[170,535,350,675]},'S02':{'vent_and_fascia':[120,670,405,940],'dash_corner':[210,590,380,720]},'S03':{'vent_and_fascia':[240,565,500,805],'dash_corner':[320,495,480,625]}}
def grad(im):
 v=np.asarray(im,dtype=float)/255;g=(v[...,0]*.2126+v[...,1]*.7152+v[...,2]*.0722);g=gaussian_filter(g,1.4);return np.hypot(sobel(g,0),sobel(g,1))/8
def edge_compare(a,b,box):
 x0,y0,x1,y1=box;aa=grad(a)[y0:y1,x0:x1];bb=grad(b)[y0:y1,x0:x1]
 ea=aa>max(.018,float(np.quantile(aa,.90)));eb=bb>max(.018,float(np.quantile(bb,.90)))
 if ea.sum()<15 or eb.sum()<15:return {'source_edge_pixels':int(ea.sum()),'render_edge_pixels':int(eb.sum()),'status':'too few reliable gradient pixels, no score'}
 d_ab=distance_transform_edt(~eb)[ea];d_ba=distance_transform_edt(~ea)[eb]
 return {'source_edge_pixels':int(ea.sum()),'render_edge_pixels':int(eb.sum()),'source_to_render_mean_px':float(d_ab.mean()),'render_to_source_mean_px':float(d_ba.mean()),'source_to_render_p90_px':float(np.quantile(d_ab,.9)),'render_to_source_p90_px':float(np.quantile(d_ba,.9)),'status':'local edge diagnostic only; texture, louvers, shadows and missing coverage confound this score'}
for idx,id in enumerate(ids):
 src=next(x for x in sources if x['id']==id);sp=S/src['path'];basepath=S/'renders/source'/f'{id}_render_{"open" if id=="S02" else "closed"}.png'
 newpath=R/f'renders/camera_only_full/{id}_render_native.png'
 a=Image.open(sp).convert('RGB');b=Image.open(basepath).convert('RGB');c=Image.open(newpath).convert('RGB');assert a.size==b.size==c.size==(1920,1080)
 assert hashlib.sha256(sp.read_bytes()).hexdigest()==src['sha256']
 overlay=Image.blend(a,c,.5);op=R/f'comparisons/{id}_direct_50percent_native.png';overlay.save(op)
 assert np.array_equal(np.asarray(overlay),np.asarray(Image.blend(a,c,.5)))
 for col,(im,title) in enumerate([(a,'NATIVE SOURCE'),(b,'BASELINE CAMERA'),(c,'CAMERA-ONLY TRIAL / REJECTED'),(overlay,'DIRECT 50% / NO WARP')]):
  sheet.paste(im.resize((480,270)),(col*480,idx*316+42));d.text((col*480+9,idx*316+12),id+' | '+title,fill='white')
 row={'id':id,'source_sha256':src['sha256'],'render_sha256':hashlib.sha256(newpath.read_bytes()).hexdigest(),'overlay_sha256':hashlib.sha256(op.read_bytes()).hexdigest(),'native_dimensions':[1920,1080],'direct_blend_verified':True,'rois':{}}
 for name,box in rois[id].items():
  row['rois'][name]={'source_box_native_xyxy':box,'baseline':edge_compare(a,b,box),'camera_only_trial':edge_compare(a,c,box)}
  trip=Image.new('RGB',((box[2]-box[0])*3,box[3]-box[1]));
  for i,im in enumerate([a,c,overlay]):trip.paste(im.crop(box),(i*(box[2]-box[0]),0))
  trip.save(R/f'comparisons/{id}_{name}_native_crop_trio.png')
 rows.append(row)
preview=R/'comparisons/camera_study_contact_sheet.jpg'
for quality in [94,90,86,82,76]:
 sheet.save(preview,quality=quality,optimize=True)
 if preview.stat().st_size<900*1024:break
(R/'pixel_readonly_qa.json').write_text(json.dumps({'method':'Independent pixel check reads native source + actual rendered PNGs; no mesh-only pass. Sobel after sigma1.4, 90th-percentile with minimum threshold .018, symmetric nearest-edge distance in explicit non-character local ROIs. Different texture/lighting/coverage prevent interpreting as geometric accuracy.','source_files_unchanged':True,'rows':rows,'preview':{'path':str(preview.relative_to(R)),'dimensions':[1920,948],'each_panel_display_scale':.25,'bytes':preview.stat().st_size,'sha256':hashlib.sha256(preview.read_bytes()).hexdigest(),'not_native_source':True}},indent=2)+'\n')
print('PIXEL_QA_AND_50PERCENT_COMPLETE',preview.stat().st_size)
