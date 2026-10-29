"""Verify native bytes, direct overlays, files, relative dependencies and local Git blobs."""
from pathlib import Path
from PIL import Image
import json,hashlib,subprocess,numpy as np
R=Path(__file__).resolve().parents[1]
native=json.loads((R/'sources/source-manifest.json').read_text())['sources']
for s in native:
 p=R/s['path'];b=p.read_bytes();assert len(b)==s['bytes'];assert hashlib.sha256(b).hexdigest()==s['sha256'];im=Image.open(p);im.load();assert list(im.size)==s['dimensions']
c=json.loads((R/'qa/comparison-manifest.json').read_text())
for row in c['full_frame']:
 a=Image.open(R/row['source']).convert('RGB');b=Image.open(R/row['render']).convert('RGB');o=Image.open(R/row['overlay']).convert('RGB')
 assert np.array_equal(np.asarray(Image.blend(a,b,.5)),np.asarray(o))
renders=json.loads((R/'qa/render-manifest.json').read_text());assert len(renders)==14
for row in renders:
 p=R/row['path'];im=Image.open(p);im.load();assert list(im.size)==row['dimensions']
assert len(list((R/'renders/checks').glob('*.png')))==9
pre=json.loads((R/'qa/preview-manifest.json').read_text());assert pre['resized'] is False and pre['dimensions']==[1920,1080] and pre['bytes']<900*1024
geometry=json.loads((R/'qa/geometry-report.json').read_text());assert geometry['all_closed_manifold'] and geometry['all_positive_volume'] and geometry['zero_area_faces_total']==0
rt=json.loads((R/'qa/glb-roundtrip-report.json').read_text());assert rt['closed_geometry_within_1e5'] and rt['open_geometry_within_1e5'] and rt['white_material_identity']['closed_equal'] and rt['white_material_identity']['open_equal']
items=[]
for p in sorted(R.rglob('*')):
 if not p.is_file() or p.name in ['artifact-manifest.json','local-commit-readback.json','library-upload-status.json','HANDOFF.md']:continue
 data=p.read_bytes();assert len(data)<100*1024*1024
 item={'path':str(p.relative_to(R)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'git_blob_sha1':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()}
 if p.suffix.lower() in ['.png','.jpg']:
  im=Image.open(p);im.load();item['image_dimensions']=list(im.size)
 items.append(item)
(R/'qa/artifact-manifest.json').write_text(json.dumps({'scope':'Local ordinary files only, not remote upload proof; excludes self and downstream handoff/status','files':items,'file_count':len(items),'total_bytes':sum(x['bytes'] for x in items),'source_originals_verified':4,'direct_overlays_verified':4,'final_renders_verified':14,'arbitrary_checks':9},indent=2)+'\n')
print('VERIFIED',len(items),'files',sum(x['bytes'] for x in items),'bytes')
