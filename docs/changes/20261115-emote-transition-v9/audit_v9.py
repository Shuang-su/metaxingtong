#!/usr/bin/env python3
"""Decode the deliverables independently; audit all original time intervals."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,distance_transform_edt
import json,hashlib,csv
import numpy as np
ROOT=Path(__file__).resolve().parents[3];DOC=Path(__file__).resolve().parent
SRC=ROOT/'emotes/sunburst/agent-emotes/03-awake';OLD=SRC/'versions/20261115-boundary-refinement/v8-local-r2';NEW=SRC/'versions/20261115-transition-v9/v9-shared-collar-r3';V7=SRC/'versions/20261113-local-patch-review/v7-green-local-r2'
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
def decode(p):
    ims=[];ts=[]
    with Image.open(p) as g:
        size=g.size;loop=g.info.get('loop')
        for i in range(g.n_frames):g.seek(i);ims.append(np.array(g.convert('RGB')));ts.append(g.info['duration'])
    return ims,ts,size,loop
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mae(a,b,box):
    x0,y0,x1,y1=box;return float(np.abs(a[y0:y1,x0:x1].astype(float)-b[y0:y1,x0:x1].astype(float)).mean())
def main():
    a,at,_,_=decode(OLD/'03-v8-CANDIDATE-master-768.gif');c,ct,size,loop=decode(NEW/'03-v9-CANDIDATE-master-768.gif');orig,ot,_,_=decode(SRC/'master.gif');manifest=json.loads((SRC/'manifest.json').read_text());assert at==ct==ot==manifest['frame_durations_ms'] and len(c)==54 and size==(768,768) and loop==0
    rows=[]
    for i,(old,new) in enumerate(zip(a,c),1):
        p=NEW/f'allowed-mask-{i:02d}.png';mask=np.array(Image.open(p))>0 if p.exists() else np.zeros((768,768),bool)
        p=NEW/f'protected-{i:02d}.png';protected=np.array(Image.open(p))>0 if p.exists() else np.zeros_like(mask)
        green=np.array(Image.open(V7/f'color-mask-{i:02d}.png'))>0;diff=np.any(old!=new,axis=-1)
        rr,gg,bb=[old[:,:,z].astype(int) for z in range(3)];skin=(rr>170)&(gg>110)&(rr-gg>12)&(rr-bb>18);labs,_=label(skin);ids=np.unique(labs[420:465,150:260]);ids=ids[ids>0];face=distance_transform_edt(~np.isin(labs,ids))<=2;face[:,330:]=False
        checks={'outside_mask_changes':int((diff&~mask).sum()),'protected_changes':int((diff&protected).sum()),'face_boundary_changes':int((diff&face).sum()),'green_changes':int((diff&green).sum()),'head_above_450_changes':int(diff[:450].sum()),'knee_and_lower_body_changes':int(diff[552:].sum())};assert not any(checks.values())
        if not 5<=i<=21:assert not diff.any()
        rows.append({'frame':i,'duration_ms':ct[i-1],'changed_pixels':int(diff.sum()),'source_rgb_sha256':hashlib.sha256(old.tobytes()).hexdigest(),'candidate_rgb_sha256':hashlib.sha256(new.tobytes()).hexdigest(),**checks})
    bounds=[]
    for n in range(1,55):
        nxt=n%54+1;r={'from':n,'to':nxt}
        for name,box in [('collar_roi',[230,450,345,550]),('lower_collar_roi',[230,490,315,540]),('whole_frame',[0,0,768,768])]:r[name]={'v8':mae(a[n-1],a[nxt-1],box),'v9':mae(c[n-1],c[nxt-1],box),'original':mae(orig[n-1],orig[nxt-1],box),'box':box}
        bounds.append(r)
    gifs=[]
    for p in sorted(NEW.glob('*.gif')):
        ims,ts,sz,lp=decode(p);assert ts==ct and len(ims)==54 and lp==0;gifs.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'size_bytes':p.stat().st_size,'dimensions':sz,'frames':len(ims),'frame_durations_ms':ts,'loop':lp})
    small,_,_,_=decode(NEW/'03-v9-CANDIDATE-preview-112.gif');sheet=Image.new('RGB',(784,8*134),'#eee');dr=ImageDraw.Draw(sheet)
    for i,im in enumerate(small):x=i%7*112;y=i//7*134;sheet.paste(Image.fromarray(im),(x,y+22));dr.text((x+2,y+3),f'F{i+1} {ct[i]}ms',font=FONT,fill='black')
    sheet.save(DOC/'03-v9-decoded-112-all.png')
    # Include unchanged entry/exit/loop frames, so a new boundary is not hidden.
    ids=list(range(3,24))+[27,28,54,1];box=(210,450,340,560);tw,th=260,220;sheet=Image.new('RGB',(tw*5,((len(ids)+4)//5)*(th+24)),'#eee');dr=ImageDraw.Draw(sheet)
    for i,n in enumerate(ids):x=i%5*tw;y=i//5*(th+24);sheet.paste(Image.fromarray(c[n-1]).crop(box).resize((tw,th),Image.Resampling.NEAREST),(x,y+24));dr.text((x+3,y+3),f'F{n}',font=FONT,fill='black')
    sheet.save(DOC/'03-v9-collar-native-all.png')
    ids=[3,4,5,6,9,17,21,22];box=(210,450,340,560);sheet=Image.new('RGB',(tw*4,(th*2+24)*2),'#eee');dr=ImageDraw.Draw(sheet)
    for i,n in enumerate(ids):
        x=i%4*tw;y=i//4*(th*2+24);dr.text((x+3,y+3),f'F{n}: v8 above / v9 below',font=FONT,fill='black')
        for z,ims in enumerate([a,c]):sheet.paste(Image.fromarray(ims[n-1]).crop(box).resize((tw,th),Image.Resampling.NEAREST),(x,y+24+z*th))
    sheet.save(DOC/'03-v8-v9-boundary-comparison.png')
    source_checks=[]
    for f in json.loads((DOC.parent/'20261113-emote-local-patch-review/intake-verification.json').read_text())['files_verified']:
        p=ROOT/f['path'];assert sha(p)==f['sha256'] and p.stat().st_size==f['size_bytes'];source_checks.append(f['path'])
    out={'status':'candidate_complete_file_checks_pass_playback_unverified','original_sha256':sha(SRC/'master.gif'),'v8_sha256':sha(OLD/'03-v8-CANDIDATE-master-768.gif'),'snapshot_files_unchanged':len(source_checks),'frame_count':54,'total_ms':sum(ct),'changed_frames':[r['frame'] for r in rows if r['changed_pixels']],'changed_duration_ms':sum(r['duration_ms'] for r in rows if r['changed_pixels']),'all_protection_checks_pass':True,'gifs':gifs,'boundary_metrics':bounds,'metrics_limit':'RGB frame differences describe local pixel transitions; they do not establish actual timed playback or subjective acceptance.','actual_playback':'unverified; prior explicit browser management denial not retried/bypassed','api_calls':0,'api_cost_usd':0}
    (DOC/'final-v9-validation.json').write_text(json.dumps(out,indent=2)+'\n')
    with (DOC/'final-v9-frame-audit.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'frames':54,'total_ms':sum(ct),'changed_duration_ms':out['changed_duration_ms'],'boundaries':[x for x in bounds if x['from'] in [4,9,21,27,54]],'worse_collar_steps':[{'from':x['from'],'to':x['to'],**x['collar_roi']} for x in bounds if x['collar_roi']['v9']>x['collar_roi']['v8']+1]},indent=2))
if __name__=='__main__':main()
