#!/usr/bin/env python3
"""Decode every deliverable; check timing, pixel protection, and loop edges."""
import json,hashlib,csv
from pathlib import Path
import numpy as np
from PIL import Image,ImageSequence
from repair_desk import DOC,ROOT,load,ORIGINAL
from build_v10 import OUT

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(p):
    im=Image.open(p);frames=[];times=[]
    for f in ImageSequence.Iterator(im):frames.append(f.convert('RGB'));times.append(f.info['duration'])
    return frames,times,im.info.get('loop')
def mae(a,b,box):
    x0,y0,x1,y1=box
    return float(np.abs(a[y0:y1,x0:x1].astype(float)-b[y0:y1,x0:x1]).mean())
def main():
    old,times=load();master=OUT/'11-v10-CANDIDATE-master-768.gif';new,nt,loop=decode(master)
    manifest=json.loads((DOC/'source-previews/11-count/manifest.json').read_text())
    assert times==nt==manifest['frame_durations_ms'];assert len(new)==54 and sum(nt)==4740 and loop==0
    assert sha(ORIGINAL)==manifest['sha256']
    rows=[]
    for n,(o,p) in enumerate(zip(old,new),1):
        a,b=np.array(o),np.array(p);change=np.any(a!=b,axis=2)
        mask=np.zeros(a.shape[:2],bool);protected=np.ones(a.shape[:2],bool)
        if n>=50:
            mask=np.array(Image.open(OUT/f'allowed-mask-{n:02}.png'))>0
            protected=np.array(Image.open(OUT/f'protected-mask-{n:02}.png'))>0
            assert p.tobytes()==Image.open(OUT/f'candidate-{n:02}.png').convert('RGB').tobytes()
        assert not (change&~mask).any() and not (change&protected).any()
        assert not change[:688].any()
        row={'frame':n,'duration_ms':times[n-1],'changed_pixels':int(change.sum()),'outside_mask_changed_pixels':int((change&~mask).sum()),'protected_changed_pixels':int((change&protected).sum()),'hands_and_pendulum_changed_pixels':int(change[410:680].sum())}
        rows.append(row)
    assert [r['frame'] for r in rows if r['changed_pixels']]==list(range(50,55))
    boundaries=[]
    for j in range(54):
        k=(j+1)%54;a,b,c,d=[np.array(q) for q in [old[j],old[k],new[j],new[k]]]
        boundaries.append({'from_frame':j+1,'to_frame':k+1,'desk_surface_before_mae':mae(a,b,[20,718,510,745]),'desk_surface_after_mae':mae(c,d,[20,718,510,745]),'lower_strip_before_mae':mae(a,b,[8,688,760,756]),'lower_strip_after_mae':mae(c,d,[8,688,760,756]),'whole_before_mae':mae(a,b,[0,0,768,768]),'whole_after_mae':mae(c,d,[0,0,768,768])})
    gifs=[]
    for p in sorted(OUT.glob('*.gif')):
        ff,tt,ll=decode(p);assert len(ff)==54 and tt==times and ll==0
        gifs.append({'path':str(p.relative_to(ROOT)),'frames':len(ff),'size':list(ff[0].size),'total_ms':sum(tt),'durations_match_original':True,'loop':ll,'sha256':sha(p),'size_bytes':p.stat().st_size})
    sources=[]
    for manifest_name in ['source-preview-provenance.json','selected-source-provenance.json']:
        for r in json.loads((DOC/manifest_name).read_text())['files']:
            p=ROOT/r['destination'];assert sha(p)==r['sha256'];sources.append({'path':r['destination'],'sha256':sha(p),'verified':True})
    originals=json.loads((DOC.parent/'20261113-emote-local-patch-review/intake-verification.json').read_text())['files_verified']
    for r in originals:
        p=ROOT/r['path'];assert sha(p)==r['sha256']
    result={'version':'v10-desk-r1','source_commit':'76051cf96bffc57200f90a6e4d88ed1ae9812287','affected_frames':[50,51,52,53,54],'affected_duration_ms':330,'unmodified_full_frames':49,'all_original_frame_timings_preserved':True,'outside_allowed_masks_changed_pixels':0,'hands_face_pendulum_changed_pixels':0,'new_source_files_hashes_verified':sources,'previous_02_03_original_files_unchanged':len(originals),'gif_validation':gifs,'frames':rows,'boundaries':boundaries,'visual_status':{'native_affected_frames':'reviewed; table restored, foreground edges retained','all_54_at_112':'static review completed','actual_timed_browser_playback':'NOT VERIFIED; prior ERR_BLOCKED_BY_ADMINISTRATOR route not retried','remaining':'Original pose and metronome geometry jitter retained; desk repair only. 03 original pose discontinuity remains unresolved.'},'api_calls':0,'api_cost_usd':0}
    (DOC/'final-v10-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    with (DOC/'final-v10-frame-audit.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'gifs':gifs,'boundary_49_50':boundaries[48],'boundary_54_1':boundaries[53],'affected':result['affected_frames'],'source_hashes_verified':len(sources)},indent=2))

if __name__=='__main__':main()
