#!/usr/bin/env python3
"""Audit original captures and make labelled contact sheets; does not alter source JPGs/models.
Run from the original cloud workspace: python scripts/freeze_source_evidence.py --workspace PATH
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import argparse,json,hashlib,math
ap=argparse.ArgumentParser();ap.add_argument('--workspace',type=Path,required=True);args=ap.parse_args()
root=Path(__file__).resolve().parents[1]; workspace=args.workspace
url='https://www.bilibili.com/video/BV1ru41147sn/'
def load(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stamp(t):return f'{int(t//3600):02}:{int(t%3600//60):02}:{t%60:06.3f}'
frames={p.stem:load(p) for p in sorted((root/'captures').glob('*.json'))}
raw=[]
for name,m in frames.items():
 p=root/'captures'/f'{name}.jpg'; b,a=m['before'],m['after'];assert p.exists()
 assert b['readyState']==a['readyState']==4 and b['decoded']==a['decoded']==[1920,1080]
 assert math.floor(b['time'])==math.floor(a['time']) and a['time']>=b['time']
 size=list(Image.open(p).size);assert size==[1180,757]
 continuous=m['kind'] in ['D_natural_playback','Sofa_boundary_playback']
 if continuous:assert not b['paused'] and not a['paused'] and b['playbackRate']==a['playbackRate']==1
 kind=m['kind'];label={'D_natural_playback':'D附近自然播放连续链的离散采样','Sofa_boundary_playback':'沙发布置边界自然播放连续链的离散采样','paused_source_frame':'D附近独立暂停源帧','paused_trial_not_continuity':'失败连续尝试中的单一暂停帧；不计连续覆盖','layout_probe':'UI seek定位的独立暂停探测帧；不计连续覆盖'}.get(kind,'独立源图定位样本；不计连续覆盖')
 raw.append(dict(file=f'captures/{name}.jpg',sha256=sha(p),bytes=p.stat().st_size,pixels=size,role=kind,caption=f'{label}；BV1ru41147sn {stamp(b["time"])}；前/后读数 {b["time"]:.6f}/{a["time"]:.6f}秒。',source_url=url,source_timestamp_before_seconds=b['time'],source_timestamp_after_seconds=a['time'],timestamp_note='视频currentTime前/后读取区间，不是逐帧PTS',decoded_dimensions_before=b['decoded'],decoded_dimensions_after=a['decoded'],ready_state_before=b['readyState'],ready_state_after=a['readyState'],paused_before=b['paused'],paused_after=a['paused'],playback_rate=b['playbackRate'],continuous_chain_member=continuous,metadata_file=f'captures/{name}.json',transform='Original cloud-browser screenshot JPEG bytes unchanged; no crop or resize'))
assert len(raw)==115
chains={}
for name,expected in [('D_natural_playback',44),('Sofa_boundary_playback',62)]:
 d=load(root/(name+'_log.json'));v=[r for r in d['samples'] if r['valid']];assert len(v)==expected
 assert all(v[i]['before']['time']<v[i+1]['before']['time'] for i in range(len(v)-1))
 for r in v:
  assert r['name'] in frames
  assert r['before']==frames[r['name']]['before'] and r['after']==frames[r['name']]['after']
  assert not r['before']['paused'] and not r['after']['paused']
 chains[name]=dict(attempts=len(d['samples']),valid_saved_samples=len(v),excluded_attempts=len(d['samples'])-len(v),first_before_seconds=v[0]['before']['time'],last_before_seconds=v[-1]['before']['time'],last_after_seconds=v[-1]['after']['time'],max_sample_start_gap_seconds=max(b['before']['time']-a['before']['time'] for a,b in zip(v,v[1:])),monotonic=True,all_ready4_same_integer_second_1920x1080_playing_1x=True,internal_seek_actions=False,method=d['method'],files=[r['name'] for r in v])
failed=load(root/'D_continuous_capture_log.json');assert failed['valid_continuity'] is False
assert len(set(r['before']['time'] for r in failed['samples']))==1
assert all(r['before']['paused'] and r['after']['paused'] for r in failed['samples'])
qa={'scope':'Captured metadata and screenshot integrity; no automatic geometry/source acceptance','all_originals_pass_metadata_integrity':True,'raw_image_count':len(raw),'continuous_images':106,'isolated_seek_probes':7,'other_paused_images':2,'chains':chains,'failed_paused_trial':{'attempts':len(failed['samples']),'continuous_coverage':False,'time_seconds':failed['samples'][0]['before']['time'],'retained_unique_images':1},'acceptance':{'source_geometry_fidelity':False,'user_acceptance':False}}
write(root/'qa/continuity_integrity.json',qa)
models={
 'ktv_fullroom/source/restored/models/Xingtong_KTV_Textured.blend':'08aa390ad3dbb88d4a93bd88f9b0585ee39062c59829a2af303a42514fbc5098',
 'ktv_fullroom/delivery/models/KTV_Complete_Open_Stage.blend':'abf9a4d970e5a7319d64f2c10eb8c3fa822a2bd60c283bfce946ed14ff33cf94',
 'ktv_fullroom/delivery/models/KTV_Complete_Open_Stage_White.blend':'c94786c4e9b38eeb6861db86fa8532e0aa947f0dfbbd1ace6ca33fb88b983b70',
 'ktv_fullroom/delivery/models/KTV_Complete_Open_Stage.glb':'de766c72c4d6f99e9aefdfb580e4e5f83ef2d7c5a3f8584795453b92f30ceb1c'}
checks=[]
for p,expected in models.items():
 actual=sha(workspace/p);assert actual==expected
 checks.append({'path':p,'frozen_phase1_sha256':expected,'actual_sha256':actual,'unchanged':True})
write(root/'qa/model_inputs_unchanged.json',{'all_unchanged':True,'new_model_version':False,'model_checks':checks,'glb_note':'No new export; actual roundtrip already audited in phase1 current_actual_glb_roundtrip.json'})
fontfile='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
f=ImageFont.truetype(fontfile,20);small=ImageFont.truetype(fontfile,16);titlefont=ImageFont.truetype(fontfile,27)
boards=[]
def board(filename,title,names,cols=2,width=590,notes=None):
 panelh=round(757*width/1180);labelh=55;header=76
 im=Image.new('RGB',(cols*width,header+math.ceil(len(names)/cols)*(panelh+labelh)),(18,21,27));dr=ImageDraw.Draw(im)
 dr.text((14,6),title,font=titlefont,fill='white');dr.text((14,43),'BV1ru41147sn | 1080P 解码；原截图 1180×757 | 标签为截图前/后视频时间',font=small,fill='#aacee6')
 for i,name in enumerate(names):
  m=frames[name];p=root/'captures'/f'{name}.jpg';x=i%cols*width;y=header+i//cols*(panelh+labelh)
  pic=Image.open(p).convert('RGB').resize((width,panelh),Image.Resampling.LANCZOS);im.paste(pic,(x,y))
  dr.text((x+7,y+panelh+2),f'{m["before"]["time"]:.6f} – {m["after"]["time"]:.6f} s',font=small,fill='white')
  if notes:dr.text((x+7,y+panelh+27),notes[i],font=small,fill='#ffdc84')
 p=root/filename;im.save(p,quality=92,subsampling=0)
 boards.append(dict(file=filename,sha256=sha(p),bytes=p.stat().st_size,pixels=list(im.size),role='labelled_source_contact_sheet',caption=title+'；原始截图另存。',source_url=url,source_frames=[{'file':f'captures/{n}.jpg','before_seconds':frames[n]['before']['time'],'after_seconds':frames[n]['after']['time']} for n in names],source_decoded_dimensions=[1920,1080],source_screenshot_pixels=[1180,757],transform='Whole original screenshot uniformly resized by panel width; labelled margins added; no geometry crop/warp/content edits'))
def evenly(names,n):return [names[round(i*(len(names)-1)/(n-1))] for i in range(n)]
D=chains['D_natural_playback']['files'];S=chains['Sofa_boundary_playback']['files']
board('D_continuity_contact.jpg','D附近连续采样总览：角色离画，舞台延续',evenly(D,16),4,395)
board('D_exit_detailed_contact.jpg','黄色伙伴向左离画；人物随后向右离画',[n for n in D if 7110<=frames[n]['before']['time']<7118],2,590)
board('Sofa_boundary_contact.jpg','沙发布置变化连续采样总览：先站起、拉远，再变为空场',evenly(S,16),4,395)
board('Sofa_boundary_detail.jpg','沙发最后有 / 首次无：采样边界 6626.598—6627.319 秒',[n for n in S if 6625<=frames[n]['before']['time']<6628],2,590)
def nearest(names,t):return min(names,key=lambda n:abs(frames[n]['before']['time']-t))
key=[nearest(S,6626.598),nearest(S,6627.319),nearest(D,7112.819),nearest(D,7113.428),nearest(D,7116.543),nearest(D,7117.139)]
board('Source_state_key_events.jpg','同场时间布置变化与动态角色离画：两种独立现象',key,2,590,['最后有沙发；黄色伙伴仍在','首次无沙发；黄色伙伴仍在','黄色伙伴穿过左边界','黄色伙伴已离画','人物穿过右边界','人物已离画；气球狗仍运动'])
write(root/'image_evidence_manifest.json',{'stage':'KTV source continuity; no model changes','source_url':url,'image_count':len(raw)+len(boards),'raw_image_count':len(raw),'composite_image_count':len(boards),'images':raw+boards})
write(root/'qa/source_state_ledger.json',{'source_url':url,'prior_reference_ledger':[{'id':'A','time_hms':'01:15:29','seconds':4529,'old_crop_pixels':[1188,668],'decoded_dimensions':'unknown','new_hd_capture_this_stage':False},{'id':'B','time_hms':'00:35:17','seconds':2117,'old_crop_pixels':[1188,668],'decoded_dimensions':'unknown','new_hd_capture_this_stage':False},{'id':'D','time_hms':'01:58:39','seconds':7119,'old_crop_pixels':[1188,668],'decoded_dimensions':'unknown','new_hd_nearby_continuity':'D_natural_playback_log.json'}], 'sofa_layout':{'last_visible_sample_before':6626.597822,'last_visible_sample_after':6626.686632,'first_absent_sample_before':6627.319120,'first_absent_sample_after':6627.396357,'sample_label_interval_seconds':[6626.598,6627.319],'conservative_interval_including_screenshot_duration_seconds':[6626.597822,6627.396357],'precise_frame_known':False,'same_stage_identity_supported':True,'physical_removal_observed':False,'production_switch_or_edit_mechanism':'unknown','star_companion_still_present_across_layout_change':True}, 'dynamic_exits':{'yellow_companion':{'direction':'left','inside_sample':7112.204957,'crossing_frame_edge_sample':7112.819021,'outside_sample':7113.428253},'person':{'direction':'right','turning_sample':7115.917794,'crossing_frame_edge_sample':7116.543366,'outside_sample':7117.139134},'red_balloon_dog':'continues moving; not a fixed calibration anchor'}, 'model_layers':['shared_static_stage','explicit_time_based_furnishing_state','dynamic_characters_props'],'current_models_modified':False,'new_state_variant_created':False,'geometry_acceptance':False})
print(json.dumps({'images':len(raw)+len(boards),'qa_pass':True,'continuous':106,'all_models_unchanged':True},ensure_ascii=False))
