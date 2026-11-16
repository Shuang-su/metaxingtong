#!/usr/bin/env python3
"""Independent decoded-frame, source hash, geometry, and timing checks."""
import json,hashlib,csv,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import repair_v12 as r
from build_v12 import OUT03,OUT11
DOC=r.DOC;ROOT=r.ROOT
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def geo_stats(rows):
 return {k:{'min':float(np.min([x[k] for x in rows])),'max':float(np.max([x[k] for x in rows])),'range':float(np.ptp([x[k] for x in rows])),'std':float(np.std([x[k] for x in rows]))} for k in ['base_center','base_width','top_y','bottom_y']}
def main():
 result={'version':'v12 prop-r6; 03 mouth-phase-r3 retained but not adopted','api_calls':0,'api_cost_usd':0,'new_frame_insertion':False,'originals_verified':[],'results':[]};allrows=[]
 for e in json.loads((ROOT/'docs/changes/20261113-emote-local-patch-review/intake-verification.json').read_text())['files_verified']:
  p=ROOT/e['path'];assert sha(p)==e['sha256'];result['originals_verified'].append(e['path'])
 refs=ROOT/'docs/changes/20261115-user-color-reference-v11/references'
 for name,h in [('OpenAI Playground 2026-11-05 at 12.43.45.png','01ed7bcb93b3868bc11a65cd70d393b9ec8df5038f8d45c07dd1e0dda4df6aa3'),('naigreen-not-angry.gif','fdf70c25d163d202b84cd8fda911f41b1c43a66d63496ba8cadecd72753aaa52')]:
  assert sha(refs/name)==h;result['originals_verified'].append(str((refs/name).relative_to(ROOT)))
 provenance=json.loads((DOC/'source-provenance.json').read_text());assert sha(ROOT/provenance['local_path'])==provenance['sha256'];result['originals_verified'].append(provenance['local_path'])
 for code,source,out,manifest in [('03',r.SRC03,OUT03,ROOT/'emotes/sunburst/agent-emotes/03-awake/manifest.json'),('11',r.SRC11,OUT11,ROOT/'docs/changes/20261115-remaining-emotes-review/source-previews/11-count/manifest.json')]:
  old,times=r.load(source);master=out/f'{code}-v12-CANDIDATE-master-768.gif';new,nt=r.load(master);assert times==nt==json.loads(manifest.read_text())['frame_durations_ms'];assert len(old)==len(new)==54
  frame_review=json.loads(manifest.read_text())['frame_review'];rows=[];beforegeo=[];aftergeo=[]
  for n,(a,b) in enumerate(zip(old,new),1):
   aa=np.array(a);bb=np.array(b);change=np.any(aa!=bb,axis=2);mp=out/f'allowed-{n:02}.png';mask=np.array(Image.open(mp))>0 if mp.exists() else np.zeros((768,768),bool)
   assert not (change&~mask).any()
   if code=='03':
    assert not change[:,330:].any();assert not change[500:].any();assert not change[:450].any();protected_changed=0
    if n!=5:assert not change.any()
   else:
    protect=np.array(Image.open(out/f'protected-hair-{n:02}.png'))>0;assert not (change&protect).any();assert not change[:,:505].any();protected_changed=0
    beforegeo.append(r.wood_geometry(a)[0]);aftergeo.append(r.wood_geometry(b)[0])
   rows.append({'emote':code,'frame':n,'source_cell':frame_review[n-1]['source'],'duration_ms':nt[n-1],'changed_pixels':int(change.sum()),'outside_mask_changed_pixels':0,'protected_changed_pixels':protected_changed})
  gifchecks=[]
  for p in sorted(out.glob('*.gif')):
   ff,tt=r.load(p);assert len(ff)==54 and tt==times and Image.open(p).info.get('loop')==0
   gifchecks.append({'path':str(p.relative_to(ROOT)),'size_bytes':p.stat().st_size,'sha256':sha(p),'frames':54,'duration_ms':sum(tt),'frame_times_exact':True,'size':list(ff[0].size),'loop':0})
  bound=[]
  for x,y in [(4,5),(5,6),(54,1)]:
   for name,box in [('whole',(0,0,768,768)),('mouth' if code=='03' else 'prop',(171,460,250,497) if code=='03' else (515,410,740,733)),('base',(515,642,740,720))] if code=='11' else [('whole',(0,0,768,768)),('mouth',(171,460,250,497))]:
    metric=lambda fs:float(np.abs(np.array(fs[x-1].crop(box)).astype(float)-np.array(fs[y-1].crop(box)).astype(float)).mean())
    bound.append({'frames':[x,y],'region':name,'before_mae':metric(old),'after_mae':metric(new)})
  transitions=[]
  for i in range(54):
   j=(i+1)%54;box=(515,642,740,720) if code=='11' else (0,0,768,768)
   metric=lambda fs:float(np.abs(np.array(fs[i].crop(box)).astype(float)-np.array(fs[j].crop(box)).astype(float)).mean())
   transitions.append({'from_frame':i+1,'to_frame':j+1,'before_mae':metric(old),'after_mae':metric(new)})
  item={'emote':code,'source':str(source.relative_to(ROOT)),'source_sha256':sha(source),'affected_frames':[x['frame'] for x in rows if x['changed_pixels']>0],'affected_duration_ms':sum(x['duration_ms'] for x in rows if x['changed_pixels']>0),'decoded_pixel_protection_pass':True,'gifs':gifchecks,'boundaries':bound,'all_loop_transitions':transitions,'distinct_decoded_frames':len({hashlib.sha256(x.tobytes()).hexdigest() for x in new}),'frames':rows}
  if code=='11':
   item['casing_geometry_before']=geo_stats(beforegeo);item['casing_geometry_after']=geo_stats(aftergeo)
   angles=np.linspace(-math.pi/2,math.pi/2,1001);params=json.loads((out/'construction.json').read_text())['frames']
   item['affine_only_direction_change_bound_degrees']=float(max(np.max(np.abs(np.arctan2(np.sin(angles)*p['scale_x'],np.cos(angles)*p['scale_y'])-angles))*180/math.pi for p in params))
   item['pointer']='Every frame retains its own source pointer under local registration, attenuated smoothly within20px of protected foreground. No donor pointer, frozen pointer, or inserted frame. Angular bound applies only to the fully affine region, not the foreground transition.'
   (out/'geometry-per-frame.json').write_text(json.dumps([{'frame':i+1,'before':a,'after':b} for i,(a,b) in enumerate(zip(beforegeo,aftergeo))],indent=2)+'\n')
  result['results'].append(item);allrows+=rows
 original11=ROOT/'docs/changes/20261115-remaining-emotes-review/source-originals/11-count/master.gif'
 assert sha(original11)=='6f9ce30aed6ec701370b76411eb4b73669a9327ba4af4d0fd8271a32389ae791';result['originals_verified'].append(str(original11.relative_to(ROOT)))
 result['visual_status']={'native_static_review':'11 all54 prop crops reviewed in six sheets; original hands, sleeves and head retained. 03 F5 mouth edge clean but pose continuity not improved; trial NOT ADOPTED.','112_contact_review':'11 all54 frames reviewed in three before/after sheets; looping GIFs encoded and decoded with exact times; static review is not timed playback.','actual_timed_playback':'NOT VERIFIED; previously managed browser route was blocked; not retried or bypassed','remaining_03':'Original F4 to F5 lowered-head pose jump and original loop pose jump remain. Production 03 remains v11-color-r5.','remaining_11':'Internal casing, pendulum appearance and shadow texture still vary between original drawings. Minor restored-shadow texture differences remain at native size. Pointer phase and actor pose transitions are not resynthesized.'}
 (DOC/'v12-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 with (DOC/'v12-frame-audit.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(allrows[0]),lineterminator='\n');w.writeheader();w.writerows(allrows)
 print(json.dumps([{k:v for k,v in x.items() if k not in ['frames','gifs']} for x in result['results']],indent=2))
if __name__=='__main__':main()
