from pathlib import Path
from PIL import Image
import shutil,json,hashlib,zipfile
R=Path('/workspace/scratch/fa58bfcf0425/ktv_fixed_visibility_20261010');D=R/'delivery';D.mkdir(exist_ok=True)
for sub in ['audit','scripts','references','renders','comparisons','qa']:
 (D/sub).mkdir(exist_ok=True)
 for p in (R/sub).iterdir():
  if not p.is_file() or p.name=='source_historical_contact.jpg':continue
  shutil.copy2(p,D/sub/p.name)
shutil.copy2(R/'README_中文.md',D/'README_中文.md')
for name in ['Final_Textured_Empty_Stage_clean.png','Final_Textured_Telescope_Detail_clean.png']:
 (D/'historical').mkdir(exist_ok=True);shutil.copy2(R/'historical/qa_package/renders'/name,D/'historical'/name)
images=[]
for p in sorted(D.rglob('*')):
 if not p.is_file() or p.suffix.lower() not in ['.png','.jpg']:continue
 rel=p.relative_to(D).as_posix();im=Image.open(p);name=p.name;time=None;source=None;cam=None
 if rel.startswith('references/'):
  role='original_source_frame';time={'frame_4529_crop.png':'01:15:29','frame_2117_crop.png':'00:35:17','frame_7119_crop.png':'01:58:39'}[name];source='https://www.bilibili.com/video/BV1ru41147sn/';cam={'frame_4529_crop.png':'MATCH_A_01h15m29s','frame_2117_crop.png':'MATCH_B_00h35m17s','frame_7119_crop.png':'MATCH_D_01h58m39s_empty'}[name];caption='原始源裁图；解码分辨率/登录状态未知；不是新采高清帧'
 elif rel.startswith('historical/'):
  role='retained_historical_render';caption='旧包原图，隐藏沙发和黄色星伙伴；仅历史证据，不计统一可见性通过'
 elif name.startswith('Source_'):
  role='source_temporal_state_composite';source='https://www.bilibili.com/video/BV1ru41147sn/';time='A 01:15:29; B 00:35:17; D 01:58:39';caption='三个不同时间来源；人物遮挡、动态道具与布置状态分开记录'
 elif 'render_only_50pct' in name:
  role='render_to_render_overlay';caption='渲染间直接50%叠图；不含来源图，不是来源匹配证明'
 elif 'source_' in name and '50pct' in name:
  role='source_direct_50pct_overlay';time='01:58:39';source='https://www.bilibili.com/video/BV1ru41147sn/';caption='D原帧与指定模型状态直接50%叠图；同1188×668；无变形、裁切、遮罩'
 elif rel.startswith('comparisons/'):
  role='labelled_comparison_board';caption=('渲染间固定可见性回归对照；无对应源帧；板内每格有状态标签；未验收' if name=='Telescope_Detail_fixed_visibility_regression.jpg' else '来源/固定可见性技术回归对照；板内每格有状态标签；未验收')
 else:
  role='fixed_visibility_regression_render' if 'historical_hidden' not in name else 'historical_hidden_control_render';caption='固定seed/2线程/48样本的控制渲染；raw与去噪版分别保留'
 if 'Empty_Stage' in name:
  cam='MATCH_D_01h58m39s_empty'
  if source is None and role not in ['render_to_render_overlay']:time='01:58:39';source='https://www.bilibili.com/video/BV1ru41147sn/'
 if 'Telescope_Detail' in name:
  cam='DETAIL_Telescope_Lamp';source=None;time=None;caption+='；合成诊断相机，没有对应来源帧'
 images.append({'relative_path':rel,'width':im.width,'height':im.height,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'role':role,'source_url':source,'source_time':time,'camera':cam,'caption_zh':caption,'source_acceptance':False,'video_decode_resolution':'unknown' if source else 'not applicable','new_source_capture':False})
json.dump(images,open(D/'image_evidence_manifest.json','w'),indent=2,ensure_ascii=False)
frozen=json.load(open(R/'audit/frozen_inputs_sha256.json'));unchanged=[]
for x in frozen:
 p=Path('/workspace/scratch/fa58bfcf0425')/x['path'];now=hashlib.sha256(p.read_bytes()).hexdigest();unchanged.append({'path':x['path'],'before_sha256':x['sha256'],'after_sha256':now,'unchanged':now==x['sha256']})
assert all(x['unchanged'] for x in unchanged)
json.dump(unchanged,open(D/'audit/inputs_unchanged_after_regression.json','w'),indent=2)
qa=json.load(open(D/'audit/blender_visibility_audit.json'));imp=json.load(open(D/'qa/current_actual_glb_roundtrip.json'))
render_checks=[]
for model in ['legacy','current','current_white']:
 for view in ['Empty_Stage','Telescope_Detail']:
  for state in (['historical_hidden','fixed'] if model=='legacy' else ['fixed']):
   tag=f'{model}_{view}_{state}';meta=json.load(open(D/'qa'/f'{tag}.json'));p=D/'renders'/f'{tag}.png'
   assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['output_sha256']
   assert Image.open(p).size==(1188,668) and not meta['geometry_edits'] and not meta['model_saved']
   render_checks.append({'tag':tag,'output_sha_matches':True,'input_sha256':meta['input_sha256'],'visibility_sha256':meta['visibility_sha256'],'dimensions':[1188,668]})
assert len(render_checks)==8
assert len({x['visibility_sha256'] for x in render_checks if x['tag'].startswith('current')})==1
ovs=json.load(open(D/'qa/overlay_pixel_verification.json'));assert len(ovs)==8 and all(x['pixel_mismatch_count']==0 for x in ovs)
json.dump(render_checks,open(D/'qa/render_file_integrity.json','w'),indent=2)

validation={'current_model_modified':False,'new_model_version_created':False,'inputs_unchanged':True,'current_all_18_cameras_same_geometry':qa['current']['all_camera_geometry_equal'],'current_all_18_cameras_same_visibility':qa['current']['all_camera_visibility_equal'],'white_geometry_matches_current':qa['current']['initial']['geometry_sha256']==qa['current_white']['initial']['geometry_sha256'],'white_visibility_matches_current':qa['current']['initial']['visibility_sha256']==qa['current_white']['initial']['visibility_sha256'],'legacy_cameras_unchanged_in_current':all(qa['legacy']['cameras'][n]['matrix_world']==qa['current']['cameras'][n]['matrix_world'] for n in qa['legacy']['cameras']),'legacy_camera_intrinsics_unchanged_in_current':all(all(qa['legacy']['cameras'][n][k]==qa['current']['cameras'][n][k] for k in ['lens_mm','sensor_width','sensor_fit','shift_x','shift_y','type']) for n in qa['legacy']['cameras']),'actual_glb_imported':True,'glb_missing_objects':imp['missing'],'glb_extra_objects':imp['extra'],'glb_triangles_equal':imp['triangles_before']==imp['triangles_after'],'glb_max_bidirectional_vertex_distance':imp['vertex_distance_max'],'source_acceptance':False,'image_count':len(images),'new_render_count':8,'new_capture_count':0,'all_eight_render_files_hash_verified':True,'all_eight_overlays_pixel_exact':True,'telescope_detail_source_frame':None}
json.dump(validation,open(D/'validation_summary.json','w'),indent=2)
files=[{'relative_path':p.relative_to(D).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(D.rglob('*')) if p.is_file() and p.name!='file_manifest.json']
json.dump(files,open(D/'file_manifest.json','w'),indent=2,ensure_ascii=False)
bundles=[]
for num,kind in [(1,'sources_and_legacy_controls'),(2,'current_and_comparisons')]:
 dest=R/f'KTV_fixed_visibility_0{num}_{kind}.zip'
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(D.rglob('*')):
   if not p.is_file():continue
   rel=p.relative_to(D).as_posix()
   common=p.suffix.lower() not in ['.png','.jpg']
   group1=rel.startswith(('references/','historical/')) or (rel.startswith('renders/') and p.name.startswith('legacy_')) or (rel.startswith('comparisons/') and (p.name.startswith('Source_') or 'source_legacy_' in p.name or 'legacy_hidden_fixed' in p.name))
   if common or (num==1 and group1) or (num==2 and not group1):z.write(p,rel)
 with zipfile.ZipFile(dest) as z:assert z.testzip() is None
 assert dest.stat().st_size<18000000,(dest,dest.stat().st_size)
 bundles.append({'path':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'zip_crc_valid':True})
json.dump(bundles,open(R/'bundle_manifest.json','w'),indent=2)
print(json.dumps({'validation':validation,'bundles':bundles},indent=2))
