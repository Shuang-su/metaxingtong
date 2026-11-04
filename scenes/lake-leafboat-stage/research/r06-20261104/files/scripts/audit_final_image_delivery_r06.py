from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,datetime
R=Path(__file__).resolve().parents[1];Q=R/'qa/r06';sources=['SOURCE_092142973_SIDE','SOURCE_100762992_TOP','SOURCE_108755584_OBLIQUE','AUX_006585758_REAR'];checks=['CHECK_%02d'%i for i in range(1,9)];mhash=hashlib.sha256((R/'models/lakeleaf-r06-material.blend').read_bytes()).hexdigest();whash=hashlib.sha256((R/'models/lakeleaf-r06-white.blend').read_bytes()).hexdigest();rows=[]
for folder,cams,size,sha in [('source',sources,(3840,2160),mhash),('checks',checks,(1280,720),mhash),('main',['HERO'],(1600,900),mhash),('white-source',sources,(3840,2160),whash),('white-checks',checks,(1280,720),whash),('white',['HERO'],(1600,900),whash)]:
 for c in cams:
  p=R/'renders/r06'/folder/(c+'.png');im=Image.open(p);im.load();meta=json.loads(p.with_suffix('.json').read_text());assert im.size==size;assert meta['model_sha256']==sha;assert meta['sha256']==hashlib.sha256(p.read_bytes()).hexdigest();assert not meta['denoising'] and meta['resolution_percentage']==100
  expected_samples=32 if folder=='main' else (16 if folder in ['source','white-source'] else 12);expected_threads=2 if folder=='source' else 6
  assert meta['samples']==expected_samples and meta['threads']==expected_threads
  rows.append({'path':str(p.relative_to(R)),'size':list(im.size),'bytes':p.stat().st_size,'sha256':meta['sha256'],'model_sha256':sha,'samples':meta['samples'],'threads':meta['threads'],'denoising':meta['denoising'],'camera':c})
for c in sources:
 a=json.loads((R/'renders/r06/source'/(c+'.json')).read_text());b=json.loads((R/'renders/r06/white-source'/(c+'.json')).read_text());assert a['camera_matrix']==b['camera_matrix'] and a['lens']==b['lens']
for c in checks:
 a=json.loads((R/'renders/r06/checks'/(c+'.json')).read_text());b=json.loads((R/'renders/r06/white-checks'/(c+'.json')).read_text());assert a['camera_matrix']==b['camera_matrix'] and a['lens']==b['lens']
a=json.loads((R/'renders/r06/main/HERO.json').read_text());b=json.loads((R/'renders/r06/white/HERO.json').read_text());assert a['camera_matrix']==b['camera_matrix'] and a['lens']==b['lens']
ovs=[]
for fname,render_key in [('comparison-manifest.json','render'),('white-comparison-manifest.json','white_render')]:
 d=json.loads((Q/fname).read_text())
 for item in d['overlays']:
  a=Image.open(R/item['source']).convert('RGB');b=Image.open(R/item[render_key]).convert('RGB');o=Image.open(R/item['overlay']).convert('RGB');expected=Image.blend(a,b,.5);assert ImageChops.difference(expected,o).getbbox() is None
  ovs.append({'overlay':item['overlay'],'size':list(o.size),'direct_50_percent_pixels_exact':True,'bytes':(R/item['overlay']).stat().st_size,'sha256':hashlib.sha256((R/item['overlay']).read_bytes()).hexdigest()})
frames=json.loads((R/'sources/capture-manifest.json').read_text())['native_frames'];sr=[]
for f in frames:
 p=R/'sources'/f['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'];assert list(Image.open(p).size)==[3840,2160];sr.append({'file':f['file'],'source_sha_matches':True})
models=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'under_100_MiB':p.stat().st_size<104857600,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (R/'models').glob('*') if p.is_file() and p.suffix in ['.blend','.glb']];assert all(x['under_100_MiB'] for x in models)
report={'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actual_final_render_count':len(rows),'actual_native_size_source_renders':8,'source_views':'3 primary source hypotheses and 1 auxiliary, each material and white; not eight original source views','actual_native_size_direct_overlays':len(ovs),'inspection_angles':8,'inspection_images':16,'inspection_coverage_limit':'Upper/oblique/near-side views; no clear complete underside view and no complete shore validation','hero_images':2,'all_material_white_cameras_equal':True,'source_frames_validated':sr,'renders':rows,'overlays':ovs,'models':models,'source_accepted':False,'user_accepted':False};(Q/'final-image-delivery-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Verified26 actual renders,8 direct native-size overlays,8 inspection angles x material/white,2 heroes. Source/user acceptance remains false.')
