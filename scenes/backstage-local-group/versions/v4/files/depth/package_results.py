from pathlib import Path
import json,shutil,hashlib
p=Path(__file__).resolve().parent;d=Path('/workspace/shared/depth-backstage-report-20261104');d.mkdir(exist_ok=True)
for n in ['009','011','012']:shutil.copytree(p/f'report-image-{n}',d/f'report-image-{n}',dirs_exist_ok=True)
shutil.copytree(p/'provenance',d/'provenance',dirs_exist_ok=True);shutil.copy2(p.parent/'depth-observatory-20261104/provenance/packages-freeze.txt',d/'provenance/packages-freeze.txt')
(d/'sources').mkdir(exist_ok=True)
for n in ['009','011','012']:shutil.copy2(p.parent/f'new-event-source-20261104/backstage-{n}.png',d/'sources'/f'backstage-{n}.png')
shutil.copy2(p.parent/'new-event-source-20261104/backstage-manifest.json',d/'sources/source-manifest.json')
for f in ['run_depth.py','run_batch.py','package_results.py']:shutil.copy2(p/f,d/f)
shutil.copy2(p.parent/'depth-observatory-20261104/fetch_model.py',d/'fetch_model.py');(d/'model').mkdir(exist_ok=True)
for f in ['config.json','preprocessor_config.json','README.md']:shutil.copy2(p/'model'/f,d/'model'/f)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();files=[{'path':str(f.relative_to(d)),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(d.rglob('*')) if f.is_file() and f.name!='manifest.json'];(d/'manifest.json').write_text(json.dumps(files,indent=2))
for f in files:assert sha(d/f['path'])==f['sha256']
for n in ['009','011','012']:
 r=json.loads((d/f'report-image-{n}/report.json').read_text());assert sha(d/f'sources/backstage-{n}.png')==r['source']['sha256'];print(n,r['range'],r['method']['raw_shape'])
print(d,len(files),sum(f['bytes'] for f in files),'hash readback PASS')
