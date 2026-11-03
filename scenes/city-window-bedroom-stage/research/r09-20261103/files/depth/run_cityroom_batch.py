from pathlib import Path
import json,subprocess
p=Path(__file__).resolve().parent;s=Path('/workspace/shared/20261103-source');manifest=json.loads((s/'capture-manifest.json').read_text())
# Conservative ROIs based on actual native pixels inspected 2026-11-03. Not segmentation.
regions={1352.177747: {'person':[760,410,1075,970],'window':[[706,0],[1870,0],[1919,613],[1714,850],[538,854],[531,495]],'beam':None},1308.663295:{'person':[844,307,1134,963],'window':[[598,0],[1498,0],[1588,511],[548,572],[514,302]],'beam':[660,0,1240,957]},1214.175651:{'person':[710,426,1048,969],'window':[[350,0],[1570,0],[1716,580],[1348,837],[176,859],[141,404]],'beam':[528,0,1262,990]},1356.934381:{'person':[478,170,1040,1079],'window':[[753,0],[1919,0],[1919,951],[689,929],[594,439]],'beam':None}}
for f in manifest['frames'][1:]:
 t=f['media_time_seconds'];ro=regions[t];ex=[{'shape':'polygon','points':ro['window'],'class':3,'description':'Conservative night-city/window region, possible texture/backdrop/reflection, not metric geometry'},{'shape':'rectangle','points':ro['person'],'class':1,'description':'Conservative moving performer ROI includes some prop/background; not segmentation'}]
 if ro['beam']:ex.append({'shape':'rectangle','points':ro['beam'],'class':2,'description':'Conservative volumetric spotlight and bloom ROI; not a solid surface, overlaps other exclusions'})
 m={'BV':'BV1ic12BMEk6','url':manifest['source']['url'],'uploader':manifest['source']['uploader'],'title':manifest['source']['title'],'time_seconds':t,'sha256':f['sha256'],'capture_record':f,'quality':manifest['source']['selected_quality'],'4K_in_menu':False,'dark_rgb_max_threshold':25,'dark_mask_definition':'255 where all original RGB channels <=25 (8 bit). Low-signal heuristic only, NOT depth or model confidence.','exclusions':ex,'provenance':'Native source capture-manifest.json; original PNG hash and size independently rechecked by depth script. Full source acquisition evidence retained separately.'}
 meta=p/'provenance'/f'cityroom-{t}-metadata.json';meta.write_text(json.dumps(m,ensure_ascii=False,indent=2))
 with (p/'provenance'/f'cityroom-{t}.log').open('w') as log:
  subprocess.run([str(p/'venv/bin/python'),str(p/'run_depth_frame.py'),'--source',str(s/f['file']),'--metadata',str(meta),'--out',str(p/f'cityroom-{t}')],stdout=log,stderr=subprocess.STDOUT,check=True)
 print(t,'complete',flush=True)
