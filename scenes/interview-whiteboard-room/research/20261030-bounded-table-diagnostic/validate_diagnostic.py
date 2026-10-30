"""Validate numeric projections and read every frozen Git blob's current bytes."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from PIL import Image
from diagnose import HERE, ROOT, CFG, G, T0, FROZEN_HEAD, project, table_corners, table_feet

repo=ROOT.parents[1]
prefix=ROOT.relative_to(repo).as_posix()
records=subprocess.check_output(['git','ls-tree','-r',FROZEN_HEAD,'--',prefix],cwd=repo,text=True).splitlines()
frozen=[]
for line in records:
    metadata,name=line.split('\t',1);blob=metadata.split()[2]
    data=(repo/name).read_bytes()
    actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    frozen.append(dict(path=name,expected_git_blob=blob,actual_git_blob=actual,size=len(data),unchanged=blob==actual))
assert all(a['unchanged'] for a in frozen)
b=json.loads((HERE/'blender-readonly-baseline.json').read_text())
projection_errors={}
for view in ['front','oblique']:
    a=project(np.r_[table_corners(T0),table_feet(T0)],np.array(CFG[view]))
    error=float(np.max(np.abs(a-np.array(b['views'][view]['projections_px']))))
    assert error<.002
    projection_errors[view]=error
topbox=np.array(b['boxes'][0]['bounds'])
expected=np.array([[G['table_x']-G['table_width']/2,G['table_y']-G['table_depth']/2,G['table_z']-.028],
                   [G['table_x']+G['table_width']/2,G['table_y']+G['table_depth']/2,G['table_z']]])
assert abs(topbox-expected).max()<1e-6
assert all(abs(a['bounds'][0][2])<1e-6 for a in b['boxes'] if '.pad-' in a['object'])
images=[]
for p in sorted((HERE/'figures').iterdir()):
    with Image.open(p) as im:im.load();size=list(im.size)
    assert size==([1920,2320] if p.suffix=='.jpg' else [1920,1160])
    if p.suffix=='.jpg':assert p.stat().st_size<900*1024
    images.append(dict(path=p.relative_to(ROOT).as_posix(),size=size,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
table=json.loads((HERE/'shared-table-results.json').read_text())
for family in ['r05','failed_camera_only']:
    assert len(table[family]['optimization_trials'])==12
    assert len(table[family]['coarse_grid'])==243
    for a in table[family]['optimization_trials']:
        assert a['oblique_top_intrusion_area_fraction']<=a['table']['oblique_wrong_table_fraction']+.015
source_hashes={}
for name,sha in [('BV14ioLBAEDt_1283.813032_front.png','e6b3d5a0a73be033387fc66775eca6eabb6849ea45f146c4252c311f1164a7e4'),('BV14ioLBAEDt_1505.632497_oblique.png','91ecd4d0c43d80a9f0422356383e4e1a2488d209b31ed8daef2882dd3550baff')]:
    actual=hashlib.sha256((ROOT/'sources'/name).read_bytes()).hexdigest();assert actual==sha;source_hashes[name]=actual
report=dict(recorded_at_utc=datetime.now(timezone.utc).isoformat(),frozen_head=FROZEN_HEAD,
            frozen_files_count=len(frozen),frozen_file_mismatches=0,frozen_files=frozen,
            actual_blender_vs_numpy_max_absolute_pixel_error=projection_errors,
            actual_table_bbox_max_error=float(abs(topbox-expected).max()),actual_front_pad_ground_contact=True,
            sources=source_hashes,images=images,table_optimizations=24,coarse_grid_trials=486,
            model_changed=False,scene_rendered=False,new_model_accepted=False,
            limitations=['projection diagnostic only; conservative boxes and manual landmark tolerances','no revised mesh exists: no new mesh collision or GLB check was claimed','frozen R05 acceptance remains candidate'])
(HERE/'validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['frozen_files','images','sources']},indent=2))
