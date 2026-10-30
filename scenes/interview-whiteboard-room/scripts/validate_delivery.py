"""Final artifact checks. No geometry rebuild, render, network, or acceptance inference."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1];QA=ROOT/'qa/r05'
checks={};images=[]
jobs=json.loads((QA/'render-jobs.json').read_text())
checks['thirteen_completed_render_jobs']=len(jobs)==13
for job in jobs:
 p=QA/job['name'];im=Image.open(p);im.load();assert list(im.size)==job['resolution']
 images.append({'path':str(p.relative_to(ROOT)),'size':list(im.size),'decode':'pass'})
checks['all_final_renders_decode_at_recorded_size']=len(images)==13
for role,name in [('front','BV14ioLBAEDt_1283.813032_front.png'),('oblique','BV14ioLBAEDt_1505.632497_oblique.png')]:
 a=Image.open(ROOT/'sources'/name).convert('RGB');b=Image.open(QA/f'source-{role}-render.png').convert('RGB');out=Image.open(QA/f'source-{role}-overlay50.png').convert('RGB')
 checks[role+'_direct_overlay_exact_pixels']=ImageChops.difference(out,Image.blend(a,b,.5)).getbbox() is None and out.size==(1920,1080)
checks['main_png_exact_original_render_bytes']=(QA/'main.png').read_bytes()==(QA/'source-front-render.png').read_bytes()
jpgs={}
for n in ['main.jpg','source-contact.jpg','inspection-contact.jpg']:
 p=QA/n;im=Image.open(p);im.load();jpgs[n]={'bytes':p.stat().st_size,'size':list(im.size)}
checks['three_display_jpegs_under_900_KiB']=all(x['bytes']<900*1024 for x in jpgs.values())
checks['nine_separate_diagnostic_angles']=len(list(QA.glob('check-??.png')))==9
checks['source_hash_and_size_pass']=all(x['expected_hash_match'] and x['size_match'] for x in json.loads((QA/'source-byte-verification.json').read_text()))
checks['listed_geometry_checks_pass']=json.loads((QA/'geometry-validation.json').read_text())['all_listed_checks_pass']
checks['no_cross_furniture_surface_intersections']=json.loads((QA/'furniture-intersections.json').read_text())['cross_furniture_pass']
current=json.loads((ROOT/'models/CURRENT.json').read_text())
checks['current_models_present']=all((ROOT/'models'/current[k]).is_file() for k in ['material_blend','white_blend','material_glb','white_glb'])
checks['no_new_zip']=not any(ROOT.rglob('*.zip'))
out={'checks':checks,'all_delivery_checks_pass':all(checks.values()),'images':images,'display_jpegs':jpgs,
 'source_acceptance':False,'user_acceptance':False,'source_fidelity_report':'../../docs/visual-review.md',
 'limitations':'Successful delivery/geometric checks do not establish whole-scene source fidelity. No external publication or remote-byte claim.'}
(QA/'delivery-validation.json').write_text(json.dumps(out,indent=2));print(json.dumps({'checks':checks,'jpgs':jpgs},indent=2))
assert all(checks.values())
