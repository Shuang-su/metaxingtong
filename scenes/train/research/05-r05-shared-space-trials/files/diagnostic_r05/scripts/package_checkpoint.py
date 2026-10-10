from pathlib import Path
import zipfile,json,hashlib,shutil
R=Path(__file__).resolve().parents[1];O=R/'checkpoint_r05c';P=R/'packages_r05c';P.mkdir(exist_ok=True);m=json.load(open(O/'checkpoint_manifest.json'));rows=[]
def package(name,files,purpose):
 uniq={arc:p for p,arc in files};items=[]
 with zipfile.ZipFile(P/name,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for arc,p in sorted(uniq.items()):
   assert p.is_file(),p;z.write(p,arc);items.append({'file':arc,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  z.writestr('CONTENTS_SHA256.json',json.dumps({'status':m['status'],'purpose':purpose,'files':items},ensure_ascii=False,indent=2))
 with zipfile.ZipFile(P/name) as z:assert z.testzip() is None
 p=P/name;row={'file':str(p),'purpose':purpose,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'under18MB':p.stat().st_size<18_000_000,'zip_crc_pass':True,'contents_count':len(items)};rows.append(row);print(name,row['bytes'],row['under18MB']);assert row['under18MB']
common=['检查点说明_中文.md','checkpoint_manifest.json','texture_reference_manifest.json','texture_glb_resource_check.json']
for kind in ['material','white']:
 files=[(Path(x['file']),Path(x['file']).name) for x in m['blends']+m['exports'] if x['kind']==kind]+[(O/f,f) for f in common]+[(O/f'{kind}_roundtrip_detail.json',f'{kind}_roundtrip_detail.json')]
 package(f'train_r05c_{kind}_checkpoint.zip',files,f'{kind} complete shared geometry checkpoint; not accepted source reconstruction; does not replace r03')
files=[(O/f,f'checkpoint/{f}') for f in common]
for root,arc in [(O/'textures','current_textures'),(O/'preview_denoised','inspection_previews'),(R/'review_c','source_comparisons'),(R/'renders_c','raw_renders_and_input_sidecars'),(R/'independent_qa','independent_qa'),(R/'scripts','scripts')]:
 for p in root.rglob('*'):
  if p.is_file():files.append((p,f'{arc}/{p.relative_to(root)}'))
for p in O.glob('*.json'):files.append((p,'checkpoint/'+p.name))
for p in O.glob('*.png'):files.append((p,'inspection_raw/'+p.name))
for p in (R/'analysis').rglob('*.json'):files.append((p,'analysis/'+str(p.relative_to(R/'analysis'))))
files.append((R/'共享空间诊断与试验_中文.md','共享空间诊断与试验_中文.md'))
for rel in ['train_hd_recapture_20261010/A2_clean_HD_viewport.jpg','train_hd_recapture_20261010/B2_clean_HD_viewport.jpg','train_hd_recapture_20261010/D2_clean_HD_viewport.jpg','train_motion_sources_20261010/J_empty_window_clean_paused.jpg','train_motion_sources_20261010/Dseq_03_clean_paused.jpg','train_motion_sources_20261010/Door_wide_59m53_paused.jpg','train_hd_recapture_20261010/manifest.json','train_motion_sources_20261010/manifest.json']:
 p=R.parents[1]/rel;files.append((p,'source_evidence/'+rel))
package('train_r05c_diagnostics_textures.zip',files,'Source comparisons, actual current texture resources, raw render provenance, structural/roundtrip and independent QA; NOT a replacement model package')
main=R/'review_c/denoised/INSPECT_01_forward_aisle.png';dest=P/'train_r05c_main_unaccepted_checkpoint.png';shutil.copyfile(main,dest);rows.append({'file':str(dest),'purpose':'Normal model main view, not a source-matched camera; candidate not accepted','bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'under18MB':dest.stat().st_size<18_000_000})
(P/'delivery_manifest.json').write_text(json.dumps({'status':m['status'],'uploaded':False,'replace_r03':False,'source_fidelity_pass':False,'items':rows},ensure_ascii=False,indent=2))
