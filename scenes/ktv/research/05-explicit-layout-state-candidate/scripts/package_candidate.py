from pathlib import Path
import json,shutil,hashlib,zipfile,datetime
root=Path(__file__).resolve().parents[1];workspace=root.parent;out=root/'delivery';out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
m=json.loads((root/'layout_state_manifest.json').read_text())
for asset in [m['base_blend'],m['shared_glb']]:assert sha(workspace/asset['workspace_relative_path'])==asset['sha256']
a=json.loads((root/'qa/state_contract_audit.json').read_text());h=json.loads((root/'historical_18_target_diagnostic/qa/state_contract_audit.json').read_text());assert a['immutable_baseline']==h['immutable_baseline']
assert a['target_count']==26 and a['all_36_camera_state_combinations_pass']
for state in ['furnished','unfurnished']:
 q=json.loads((root/f'qa/render_{state}.json').read_text());assert q['manifest_sha256']==sha(root/'layout_state_manifest.json');assert q['state_module_sha256']==sha(root/'scripts/layout_states.py');assert len(q['state_switch']['allowed_targets'])==26
current=json.loads((root/'image_evidence_manifest.json').read_text());assert current['image_count']==16
old=json.loads((root/'historical_18_target_diagnostic/image_evidence_manifest.json').read_text());assert old['image_count']==16
all_images=[]
for label,prefix,manifest in [('final_18_plus_8','',current),('historical_18_only','historical_18_target_diagnostic/',old)]:
 for row in manifest['images']:
  row=dict(row);row['file']=prefix+row['file'];row['revision']=label;row['caption']=('最终18沙发+8推断附件候选；' if not prefix else '历史仅18沙发初稿，残垫问题已在最终候选修订；')+row['caption']
  if row.get('source_reference'):row['source_reference']=prefix+row['source_reference']
  if row.get('parents'):row['parents']=[prefix+p for p in row['parents']]
  if row.get('source_references'):row['source_references']=[dict(x,file=prefix+x['file']) for x in row['source_references']]
  assert sha(root/row['file'])==row['sha256'];all_images.append(row)
images_on_disk={str(p.relative_to(root)) for folder in ['references','renders','comparisons','historical_18_target_diagnostic'] for p in (root/folder).rglob('*') if p.suffix.lower() in ['.jpg','.png']}
assert images_on_disk=={r['file'] for r in all_images}
pads=json.loads((root/'qa/residual_floor_details.json').read_text());assert not any(x['name'].startswith('INFERRED_furniture_contact_pad') and x['name'] in m['inferred_attachment_groups'][0]['objects'] for x in pads['candidates'])
dump(root/'qa/final_freeze_checks.json',{'base_asset_hashes_unchanged':True,'historical_vs_final_all_geometry_material_transform_fingerprints_equal':True,'final_manifest_and_state_script_match_both_render_receipts':True,'target_scope':{'furniture':18,'inferred_furniture_attachments':8},'all_images_manifested':32,'residual_sofa_pads_not_visible_in_final_projection_check':True,'source_geometry_accepted':False,'camera_calibration_accepted':False,'models_saved_or_reexported':False})
for folder in ['scripts','qa','references','renders','comparisons','logs','historical_18_target_diagnostic']:
 shutil.copytree(root/folder,out/folder,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
for n in ['README_中文.md','layout_state_manifest.json','glb_binding_contract.json','issue_comment_draft.md']:shutil.copy2(root/n,out/n)
shutil.copy2(root/'image_evidence_manifest.json',out/'current_image_evidence_manifest.json')
dump(out/'image_evidence_manifest.json',{'image_count':32,'final_images':16,'historical_diagnostic_images':16,'images':all_images})
files=sorted(p for p in out.rglob('*') if p.is_file() and p.name!='FILE_MANIFEST.json')
dump(out/'FILE_MANIFEST.json',{'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'models_duplicated':False,'files':[{'path':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]})
files=sorted(p for p in out.rglob('*') if p.is_file());curr=[p for p in files if p.relative_to(out).parts[0]!='historical_18_target_diagnostic'];historical=[p for p in files if p.relative_to(out).parts[0]=='historical_18_target_diagnostic'];common=[out/'README_中文.md',out/'FILE_MANIFEST.json',out/'image_evidence_manifest.json']
packages=[]
for name,selected in [('KTV_explicit_states_01_final_candidate.zip',curr),('KTV_explicit_states_02_historical_diagnostic.zip',historical+common)]:
 p=root/name
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for f in sorted(set(selected)):z.write(f,'KTV_explicit_layout_states/'+str(f.relative_to(out)))
 with zipfile.ZipFile(p) as z:assert z.testzip() is None
 assert p.stat().st_size<18000000
 packages.append({'file':name,'bytes':p.stat().st_size,'sha256':sha(p),'crc_test':'pass'})
receipt={'frozen':True,'image_count':32,'file_count':len(files),'models_duplicated':False,'CURRENT_changed':False,'file_manifest_sha256':sha(out/'FILE_MANIFEST.json'),'packages':packages};dump(root/'freeze_receipt.json',receipt);print(json.dumps(receipt,ensure_ascii=False,indent=2))
