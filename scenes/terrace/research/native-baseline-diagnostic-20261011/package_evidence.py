from pathlib import Path
import zipfile,hashlib,json
P=Path(__file__).resolve().parent;D=P/'delivery';D.mkdir(exist_ok=True)
common=['报告_先读这里.md','FROZEN_INPUTS.json','structural_audit.json','structural_projections.json','scene_audit.json','sun_path_audit.json','optional_current_audit.json','edge_diagnostic.json','sun_path_diagram.png','render_fixed.py','inspect_scene.py','audit_structure.py','audit_sun_paths.py','audit_optional.py','make_overlays.py','build_analysis.py','package_evidence.py','source/native/terrace/source-manifest.json','source/native/terrace/README_中文.txt']
common += [str(x.relative_to(P)) for x in sorted((P/'history').iterdir())]
frames={'main':'terrace-main-front-BV1g64y1P7VV-t5586.011739-native.png','low':'terrace-autumn-low-BV1g64y1P7VV-t2751.636134-native.png'}
manifest={'scope':'Two semantic per-view evidence packages, each under 18,000,000 bytes. No model or altered source included. Merge into one directory for all-view reproduction.','files':[]}
for key,frame in frames.items():
 files=common+[f'source/native/terrace/frames/{frame}']+[f'renders/{key}/{n}' for n in ['render_raw.png','render_oidn.png','overlay_50_source_raw.png','comparison_preview.jpg','camera_render_manifest.json','overlay_validation.json']]
 if key=='main':files+=['source_floor_probe_guide.jpg']
 entries=[]
 for f in files:
  p=P/f;assert p.is_file();entries.append({'path':f,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 pm={'view':key,'manifest_resolution':[1920,1080],'entries':entries,'omitted_reproducible_intermediates':['render_raw_linear.exr','render_raw_linear.pfm','render_oidn_linear.pfm'],'omitted_optional_overlay':'overlay_50_source_oidn.png can be recreated by make_overlays.py from included original source and OIDN PNG. Exact raw overlay is included.','original_source_manifest_scope':'Original source manifest describes both frames; this per-view package contains only the named view. The other semantic package contains its counterpart.','models':'Only frozen URLs and SHA references, no duplicate model file.','scene_inventory_note':'Optional hidden object world bounds corrected with local TRS audit because disabled collection matrix_world can be stale.'}
 meta=json.dumps(pm,ensure_ascii=False,indent=2).encode()
 name={'main':'露台_主机位原生1920冻结核验_20261011.zip','low':'露台_秋态低机位原生1920结构核验_20261011.zip'}[key];zp=D/name
 with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for f in files:z.write(P/f,f)
  z.writestr(f'PACKAGE_CONTENTS_{key}.json',meta)
  z.writestr(f'SHA256SUMS_{key}.txt','\n'.join(e['sha256']+'  '+e['path'] for e in entries)+'\n')
 assert zp.stat().st_size<18000000,(zp,zp.stat().st_size)
 with zipfile.ZipFile(zp) as z:
  assert z.testzip() is None
  for e in entries:assert hashlib.sha256(z.read(e['path'])).hexdigest()==e['sha256']
 manifest['files'].append({'view':key,'file':name,'bytes':zp.stat().st_size,'sha256':hashlib.sha256(zp.read_bytes()).hexdigest(),'member_count':len(files)+2,'crc_verified':True,'member_sha256_verified':True})
 print(manifest['files'][-1])
(D/'PACKAGING_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
