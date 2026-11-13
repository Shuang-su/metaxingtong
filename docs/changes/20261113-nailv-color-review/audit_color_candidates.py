#!/usr/bin/env python3
"""Decode final GIF artifacts and verify local color protection and timelines."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,csv
import numpy as np
ROOT=Path(__file__).resolve().parents[3];DOC=Path(__file__).resolve().parent
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(p):
    frames=[];times=[]
    with Image.open(p) as g:
        loop=g.info.get('loop')
        for k in range(g.n_frames):g.seek(k);frames.append(g.convert('RGB'));times.append(g.info['duration'])
    return frames,times,loop
def main():
    result={'status':'decoded_artifact_checks_passed_visual_motion_acceptance_pending',
            'runtime_playback':'not retried; prior browser administrator block remains',
            'scope':'Only 768px master has exact outside-mask protection. 112px/paired previews are resampled.',
            'selected_version':'v7-green-local-r2','emotes':{}};csvrows=[]
    for name,v6 in [('02-butterfly','dynamic-candidate'),('03-awake','dynamic-candidate-r1')]:
        source=ROOT/'emotes/sunburst/agent-emotes'/name;base=source/'versions/20261113-local-patch-review';out=base/'v7-green-local-r2';old=base/'v6-contour-and-motion'/v6
        originals,times,_=decode(old/'CANDIDATE-master-768.gif');frames,ts,loop=decode(out/'CANDIDATE-color-master-768.gif')
        expected=json.loads((source/'manifest.json').read_text())['frame_durations_ms'];assert ts==times==expected and loop==0
        construction=json.loads((out/'construction.json').read_text());rows=[]
        for i,(a,b) in enumerate(zip(originals,frames),1):
            aa=np.array(a);bb=np.array(b);m=np.array(Image.open(out/f'color-mask-{i:02d}.png'))>0;diff=np.any(aa!=bb,-1)
            assert not (diff&~m).any() and not diff[420:].any()
            earlier=old/f'allowed-mask-{i:02d}.png';earlier_changes=0
            if earlier.exists():
                prior=np.array(Image.open(earlier))>0;earlier_changes=int((diff&prior).sum());assert earlier_changes==0
            row={'emote':name,'frame':i,'duration_ms':ts[i-1],'changed_pixels':int(diff.sum()),'outside_color_mask_changes':0,'body_y_ge_420_changes':0,'earlier_hand_repair_region_changes':earlier_changes,'color_mask_sha256':sha(out/f'color-mask-{i:02d}.png'),'v6_rgb_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'color_rgb_sha256':hashlib.sha256(b.tobytes()).hexdigest()}
            rows.append(row);csvrows.append(row)
        paired=[]
        for a,b in zip(originals,frames):
            p=Image.new('RGB',(640,344),'#eee');d=ImageDraw.Draw(p);d.text((5,4),'V6 HAND REPAIR',font=FONT,fill='black');d.text((325,4),'V7 LOCAL GREEN CANDIDATE',font=FONT,fill='black');p.paste(a.resize((320,320),Image.Resampling.LANCZOS),(0,24));p.paste(b.resize((320,320),Image.Resampling.LANCZOS),(320,24));paired.append(p)
        paired[0].save(out/'comparison-v6-v7-320.gif',save_all=True,append_images=paired[1:],duration=ts,loop=0,disposal=2,optimize=False)
        files={}
        for f,size in [('CANDIDATE-color-master-768.gif',(768,768)),('CANDIDATE-color-preview-112.gif',(112,112)),('comparison-v6-v7-320.gif',(640,344))]:
            ims,durations,lp=decode(out/f);assert durations==expected and lp==0 and all(im.size==size for im in ims)
            files[f]={'sha256':sha(out/f),'bytes':(out/f).stat().st_size,'frame_count':len(ims),'total_ms':sum(durations),'every_duration_matches':True,'size':list(size)}
            if size==(112,112):
                sheet=Image.new('RGB',(8*112,134*((len(ims)+7)//8)),'#eee');d=ImageDraw.Draw(sheet)
                for j,im in enumerate(ims):
                    x=j%8*112;y=j//8*134;sheet.paste(im,(x,y+22));d.text((x+2,y+2),f'F{j+1}',font=FONT,fill='black')
                sheet.save(out/'actual-decoded-112-contact.png')
        zero=[r['frame'] for r in rows if r['changed_pixels']==0]
        if name.startswith('02'):assert 17 in zero
        else:
            for n in range(34,40):assert set(construction['frames'][n-1]['regions'])=={'bang_streak'}
            assert 'left_iris' in construction['frames'][39]['regions']
            previous,_,_=decode(base/'v7-green-local-r1/CANDIDATE-color-master-768.gif')
            revised=[i+1 for i,(a,b) in enumerate(zip(previous,frames)) if a.tobytes()!=b.tobytes()];assert revised==[40]
        result['emotes'][name]={'files':files,'unchanged_frames':zero,'outside_color_mask_changes':0,'body_y_ge_420_changes':0,'earlier_hand_repair_region_changes':0,'palette_min_new_color_slots':min(r['palette_new_color_slots'] for r in construction['frames'])}
    inputs=json.loads((ROOT/'handoff-manifest.json').read_text())['files']
    for x in inputs:assert sha(ROOT/x['path'])==x['sha256']
    result['original_snapshot_files_unchanged']=len(inputs)
    (DOC/'final-color-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    with (DOC/'final-color-frame-audit.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(csvrows[0]),lineterminator='\n');w.writeheader();w.writerows(csvrows)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
