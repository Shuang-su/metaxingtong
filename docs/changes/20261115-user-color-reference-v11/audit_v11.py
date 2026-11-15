#!/usr/bin/env python3
"""Audit full decoded animations, explicit protection and color-rule stability."""
import json,csv,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageSequence,ImageDraw
import color_v11 as c
from build_v11 import outdir

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(p):
 im=Image.open(p);fs=[];tt=[]
 for f in ImageSequence.Iterator(im):fs.append(f.convert('RGB'));tt.append(f.info['duration'])
 return fs,tt,im.info.get('loop')
def main():
 results=[];allrows=[]
 for name in c.SOURCES:
  old,times=c.load(name);out=outdir(name);prefix=name[:2];new,tt,loop=decode(out/f'{prefix}-v11-CANDIDATE-master-768.gif');assert tt==times and loop==0 and len(new)==len(old)
  construct=json.loads((out/'construction.json').read_text());rows=[]
  targets=[json.dumps(r['target_ab'],sort_keys=True) for r in construct['frames']];assert len(set(targets))==1
  for n,(a0,b0) in enumerate(zip(old,new),1):
   a=np.array(a0);b=np.array(b0);change=np.any(a!=b,axis=2);mask=np.array(Image.open(out/f'allowed-mask-{n:02}.png'))>0
   assert not (change&~mask).any();assert b0.tobytes()==Image.open(out/f'candidate-{n:02}.png').convert('RGB').tobytes()
   dark=np.max(a,axis=2)<90;white=np.min(a,axis=2)>220
   assert not (change&dark).any();assert not (change&white).any()
   handpath=c.ROOT/'emotes/sunburst/agent-emotes'/name/'versions/20261113-local-patch-review/v6-contour-and-motion'/('dynamic-candidate' if name.startswith('02') else 'dynamic-candidate-r1')/f'protected-{n:02}.png'
   hands=np.array(Image.open(handpath))>0 if handpath.exists() else np.zeros(mask.shape,bool)
   assert not (change&hands).any()
   prior_patch=c.ROOT/'emotes/sunburst/agent-emotes'/name/('versions/20261115-boundary-refinement/v8-local-r1' if name.startswith('02') else 'versions/20261115-transition-v9/v9-shared-collar-r3')/f'allowed-mask-{n:02}.png'
   patch=np.array(Image.open(prior_patch))>0 if prior_patch.exists() else np.zeros(mask.shape,bool)
   assert not (change&patch).any()
   if name.startswith('03'):
    yy,xx=np.indices(mask.shape);garment=(yy>=440)&(xx<655);assert not (change&garment).any()
   regionstats={}
   for region in ['hair','bang','left_iris','right_iris']:
    m=np.array(Image.open(out/f'{region}-mask-{n:02}.png'))>0
    regionstats[region]={'pixels':int(m.sum()),'median_before_rgb':np.median(a[m],axis=0).tolist() if m.any() else None,'median_after_rgb':np.median(b[m],axis=0).tolist() if m.any() else None,'median_before_lab':np.median(c.lab(a[m]),axis=0).tolist() if m.any() else None,'median_after_lab':np.median(c.lab(b[m]),axis=0).tolist() if m.any() else None}
   row={'emote':name,'frame':n,'duration_ms':times[n-1],'changed_pixels':int(change.sum()),'outside_mask_changed_pixels':0,'dark_ink_changed_pixels':int((change&dark).sum()),'white_core_changed_pixels':int((change&white).sum()),'prior_hand_protection_changed_pixels':int((change&hands).sum()),'previous_skirt_or_collar_patch_changed_pixels':int((change&patch).sum())};rows.append(row);allrows.append(row)
   construct['frames'][n-1]['measured_color']=regionstats
  gifs=[]
  for p in sorted(out.glob('*.gif')):
   frames,durations,l=decode(p);assert len(frames)==len(old) and durations==times and l==0
   gifs.append({'path':str(p.relative_to(c.ROOT)),'sha256':sha(p),'size_bytes':p.stat().st_size,'frame_count':len(frames),'size':list(frames[0].size),'total_ms':sum(times),'durations_match':True,'loop':l})
  # Save two native representative faces, both loop endpoints, and action/occlusion.
  ids=[1,17,27,len(old)] if name.startswith('02') else [1,5,17,34,54]
  comp=Image.new('RGB',(1536,len(ids)*410),'#eee');d=ImageDraw.Draw(comp)
  for j,n in enumerate(ids):
   for k,im in enumerate([old[n-1],new[n-1]]):
    y=j*410;comp.paste(im.crop((0,50,768,438)),(k*768,y+22));d.text((k*768+4,y+4),f'{name} F{n:02} '+('previous' if k==0 else 'v11'),fill='black')
  comp.save(out/'native-color-comparison.png')
  (out/'measured-colors.json').write_text(json.dumps(construct,ensure_ascii=False,indent=2)+'\n')
  results.append({'emote':name,'frames':len(old),'total_ms':sum(times),'gif_validation':gifs,'all_targets_identical_across_frames':True,'common_palette_size':len(construct['common_hair_palette_rgb']),'frames_audit':rows,'remaining':'Existing anatomy repairs and original hard pose transitions retained; no temporal redraw/interpolation.'})
 intake=json.loads((c.DOC/'reference-intake.json').read_text())
 for r in intake['files']:assert sha(Path(r['path']))==r['sha256']
 original=json.loads((c.DOC.parent/'20261113-emote-local-patch-review/intake-verification.json').read_text())['files_verified']
 for r in original:assert sha(c.ROOT/r['path'])==r['sha256']
 (c.DOC/'final-v11-validation.json').write_text(json.dumps({'selected_version':'v11-color-r5','reference_hashes_verified':2,'original_handoff_files_unchanged':len(original),'api_calls':0,'api_cost_usd':0,'results':results,'actual_browser_playback':'NOT VERIFIED; known administrative block not retried','scope_limits':['Source poses/anatomy not changed.','Deep occluded left braid below sleeve in 03 preserved to avoid garment recolor.','Existing accessory shapes retained; no red neckband or floating green glyphs added.','GIF-name reference decodes as single-frame PNG, not an animation.'],'pixel_protection':'Outside each saved mask, dark ink RGB max<90, white cores RGB min>220, and prior explicit hand-protection masks are byte-identical. Semantic clothing/Xingtong review is visual plus these exact pixel checks.'},ensure_ascii=False,indent=2)+'\n')
 with (c.DOC/'final-v11-frame-audit.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(allrows[0]),lineterminator='\n');w.writeheader();w.writerows(allrows)
 print(json.dumps({'results':[{'emote':r['emote'],'frames':r['frames'],'total_ms':r['total_ms'],'gifs':r['gif_validation']} for r in results],'references_verified':2,'protected_tests':'pass'},indent=2))

if __name__=='__main__':main()
