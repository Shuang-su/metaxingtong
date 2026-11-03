from pathlib import Path
import json,subprocess
p=Path(__file__).resolve().parent;s=Path('/workspace/shared/20261103-source');mf=json.loads((s/'fan4k-capture-manifest.json').read_text())
# Fractional ROIs based on visually inspected full frame, converted to native coordinates.
rois={149.870324: {'person':[.37,.20,.54,1],'window':[[.44,0],[1,0],[1,.69],[.37,.68]],'beam':[.27,0,.68,1]},55.04896:{'person':[.50,.40,.76,.92],'window':[[.54,0],[1,0],[1,.85],[.48,.76]],'beam':None},193.097193:{'person':[.43,.38,.54,.87],'window':[[.40,0],[.82,0],[.88,.56],[.97,.77],[.29,.75],[.30,.43]],'beam':[.36,0,.63,.90]}}
for f in mf['frames']:
 t=f['media_time_seconds'];r=rois[t];w,h=f['dimensions'];rect=lambda a:[round(a[0]*w),round(a[1]*h),round(a[2]*w),round(a[3]*h)]
 ex=[{'shape':'polygon','points':[[round(x*w),round(y*h)] for x,y in r['window']],'class':3,'description':'Conservative night city/window, possible texture/backdrop/reflection; no metric geometry'},{'shape':'rectangle','points':rect(r['person']),'class':1,'description':'Conservative moving performer region includes some prop/background; not segmentation'},{'shape':'rectangle','points':[0,0,110,65],'class':4,'description':'Bilibili live watermark overlay, non-scene graphics'}]
 if r['beam']:ex.append({'shape':'rectangle','points':rect(r['beam']),'class':2,'description':'Volumetric spotlight/bloom/ground light conservative region, not solid geometry'})
 m={'BV':'BV1q711BqE4K','part':1,'url':mf['source_url'],'uploader':mf['uploader'],'source_kind':mf['source_kind'],'time_seconds':t,'sha256':f['sha256'],'capture_record':f,'quality':mf['selected_quality'],'native_decode':'3840x2160 native saved PNG confirmed; upstream render resolution or pre-upload upsampling unknown','independence':'Same performance, separate upload; not later-date scene validation','dark_rgb_max_threshold':25,'dark_mask_definition':'255 where all original RGB channels <=25. Low signal warning only, NOT depth or calibrated confidence.','exclusions':ex}
 meta=p/'provenance'/f'fan4k-{t}-metadata.json';meta.write_text(json.dumps(m,ensure_ascii=False,indent=2))
 with (p/'provenance'/f'fan4k-{t}.log').open('w') as log:
  subprocess.run([str(p/'venv/bin/python'),str(p/'run_depth_frame.py'),'--source',str(s/f['file']),'--metadata',str(meta),'--out',str(p/f'fan4k-{t}')],stdout=log,stderr=subprocess.STDOUT,check=True)
 print(t,'complete',flush=True)
