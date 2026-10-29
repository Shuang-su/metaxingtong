"""One bounded sky anti-aliasing trial; reproduce R09 sky before higher-resolution sampling.
No native source images enter this operation. Original R09 files are never written.
"""
from pathlib import Path
import json,copy,hashlib
import numpy as np
from scipy.ndimage import gaussian_filter
R=Path(__file__).resolve().parents[1];Q=R/'qa/r10/diagnosis';OUT=R/'textures/r10_trial';OUT.mkdir(parents=True,exist_ok=True)
original=R/'scripts/make_environment_textures.py';source=original.read_text();marker='h,w=512,1024;y,x='
prefix,sky_tail=source.split(marker,1)
# Preserve the original random draws before sky construction, but suppress map writes.
prefix=prefix.replace("OUT=ROOT/'textures/r09'", "OUT=ROOT/'textures/r10_trial'")
prefix=prefix.replace("def save(name,a):Image.fromarray(np.uint8(np.clip(a,0,1)*255)).save(OUT/name)","def save(name,a):pass")
ns={'__file__':str(original)};exec(compile(prefix,str(original),'exec'),ns);state=copy.deepcopy(ns['rng'].bit_generator.state)
# Baseline is written to trial folder only and must reproduce both existing HDR hashes.
full='h,w=512,1024;y,x='+sky_tail.split("manifest={'origin'")[0]
exec(compile(full,'R09_sky_only','exec'),ns)
checks={}
for label in ['S40_sunset','S105_bluehour']:
 old=R/'textures/r09'/f'{label}.hdr';repro=OUT/f'{label}.hdr';a=hashlib.sha256(old.read_bytes()).hexdigest();b=hashlib.sha256(repro.read_bytes()).hexdigest();assert a==b,(label,a,b);checks[label]={'R09_sha256':a,'reproduced_sha256':b};repro.rename(OUT/f'{label}_R09_reproduced.hdr')
ns['rng'].bit_generator.state=state
trial=full.replace('h,w=512,1024','h,w=1024,2048')
# Low-pass the exact shared cloud alpha in angular texture space; no camera or state condition.
trial=trial.replace(";azdist=np.arctan2", ";mask=gaussian_filter(mask,sigma=(1.2,1.2),mode=('nearest','wrap'));azdist=np.arctan2")
ns['gaussian_filter']=gaussian_filter
exec(compile(trial,'R10_antialias_trial','exec'),ns)
for label in ['S40_sunset','S105_bluehour']:
 p=OUT/f'{label}.hdr';checks[label]['trial_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();checks[label]['trial_bytes']=p.stat().st_size
(Q/'sky-resampling-trial.json').write_text(json.dumps({'baseline_reproduction_exact':True,'random_field_and_coefficients_unchanged':True,'original_dimensions':[1024,512],'trial_dimensions':[2048,1024],'mask_prefilter_sigma_texels':[1.2,1.2],'environment_interpolation_trial':'Cubic','state_or_camera_specific_warp':False,'checks':checks},indent=2)+'\n');print('SKY_TRIAL_READY')
