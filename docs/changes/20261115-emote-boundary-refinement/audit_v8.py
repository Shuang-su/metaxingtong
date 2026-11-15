#!/usr/bin/env python3
"""Independent decode-based v8 verification; does not call the patch builder."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,csv
import numpy as np
ROOT=Path(__file__).resolve().parents[3];DOC=Path(__file__).resolve().parent
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
SELECTED={'02-butterfly':'v8-local-r1','03-awake':'v8-local-r2'}
def decode(path):
    frames=[];times=[]
    with Image.open(path) as g:
        size=g.size;loop=g.info.get('loop')
        for n in range(g.n_frames):g.seek(n);frames.append(np.array(g.convert('RGB')));times.append(g.info['duration'])
    return frames,times,size,loop
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    output=[];csv_rows=[];inputs=json.loads((DOC.parent/'20261113-emote-local-patch-review/intake-verification.json').read_text())['files_verified'];verified=[]
    for item in inputs:
        p=ROOT/item['path'];assert p.stat().st_size==item['size_bytes'] and sha(p)==item['sha256'];verified.append(item['path'])
    for name,version in SELECTED.items():
        src=ROOT/'emotes/sunburst/agent-emotes'/name;b=src/'versions/20261113-local-patch-review';out=src/'versions/20261115-boundary-refinement'/version
        original,ot,_,_=decode(src/'master.gif');before,bt,_,_=decode(b/'v7-green-local-r2/CANDIDATE-color-master-768.gif');after,times,size,loop=decode(out/(name[:2]+'-v8-CANDIDATE-master-768.gif'))
        manifest=json.loads((src/'manifest.json').read_text());assert times==bt==ot==manifest['frame_durations_ms'] and size==(768,768) and loop==0
        records=[]
        for k,(a,c) in enumerate(zip(before,after),1):
            p=out/f'allowed-mask-{k:02d}.png';mask=np.array(Image.open(p))>0 if p.exists() else np.zeros((768,768),bool)
            p=out/f'protected-{k:02d}.png';pr=np.array(Image.open(p))>0 if p.exists() else np.zeros((768,768),bool)
            color=np.array(Image.open(b/'v7-green-local-r2'/f'color-mask-{k:02d}.png'))>0;diff=np.any(a!=c,axis=-1)
            row={'emote':name,'frame':k,'duration_ms':times[k-1],'changed_pixels':int(diff.sum()),'outside_mask_changes':int((diff&~mask).sum()),'protected_hand_changes':int((diff&pr).sum()),'green_color_changes':int((diff&color).sum()),'head_y_lt_420_changes':int(diff[:420].sum()),'candidate_rgb_sha256':hashlib.sha256(c.tobytes()).hexdigest()}
            assert all(row[x]==0 for x in ['outside_mask_changes','protected_hand_changes','green_color_changes','head_y_lt_420_changes'])
            records.append(row);csv_rows.append(row)
        gifs=[]
        for p in sorted(out.glob('*.gif')):
            ims,ts,sz,lp=decode(p);assert ts==times and lp==0 and len(ims)==len(after)
            gifs.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'size_bytes':p.stat().st_size,'dimensions':sz,'frame_count':len(ims),'frame_durations_ms':ts,'loop':lp})
        # These are actual decoded 112px frames, never resized from a PNG sheet.
        small,_,_,_=decode(out/(name[:2]+'-v8-CANDIDATE-preview-112.gif'));cols=7;sheet=Image.new('RGB',(784,((len(small)+6)//7)*134),'#eee');d=ImageDraw.Draw(sheet)
        for i,a in enumerate(small):x=i%7*112;y=i//7*134;sheet.paste(Image.fromarray(a),(x,y+22));d.text((x+2,y+3),f'F{i+1} {times[i]}ms',font=FONT,fill='black')
        sheet.save(DOC/(name[:2]+'-final-decoded-112-all.png'))
        metrics=[]
        if name.startswith('03'):
            roi=(230,450,345,550);x0,y0,x1,y1=roi
            for f1,f2 in [(54,1),(4,5),(21,22),(27,28)]:
                values={}
                for label,ims in [('v7',before),('v8',after)]:values[label]=float(np.abs(ims[f1-1][y0:y1,x0:x1].astype(float)-ims[f2-1][y0:y1,x0:x1].astype(float)).mean())
                metrics.append({'transition':[f1,f2],'roi':roi,'raw_RGB_MAE_0_255':values,'not_perceptual_playback_acceptance':True})
            ids=[51,52,53,54,1,2,3,4];box=(225,445,345,550);tw=240;th=210;sh=Image.new('RGB',(tw*4,(th*2+24)*2),'#ddd');dr=ImageDraw.Draw(sh)
            for j,n in enumerate(ids):
                x=j%4*tw;y=j//4*(th*2+24);dr.text((x+2,y+3),f'F{n}: v7 above / v8 below',font=FONT,fill='black')
                for z,ims in enumerate([before,after]):sh.paste(Image.fromarray(ims[n-1]).crop(box).resize((tw,th),Image.Resampling.NEAREST),(x,y+24+z*th))
            sh.save(DOC/'03-loop-boundary-v7-v8.png')
        output.append({'emote':name,'selected_version':version,'original_sha256':sha(src/'master.gif'),'frame_count':len(after),'total_ms':sum(times),'changed_frames':[r['frame'] for r in records if r['changed_pixels']],'changed_duration_ms':sum(r['duration_ms'] for r in records if r['changed_pixels']),'all_pixel_protection_checks_pass':True,'gifs':gifs,'boundary_metrics':metrics})
    report={'status':'verified_files_visual_review_recorded_separately','snapshots_verified':len(verified),'snapshot_paths':verified,'emotes':output,'api_configuration_present':False,'api_calls':0,'usage_tokens':0,'generated_images':0,'api_cost_usd':0,'actual_browser_playback':'unverified; prior explicit management block not retried or bypassed'}
    (DOC/'final-v8-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    with (DOC/'final-v8-frame-audit.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(csv_rows[0]),lineterminator='\n');w.writeheader();w.writerows(csv_rows)
    print(json.dumps({'snapshots_verified':len(verified),'emotes':[{k:r[k] for k in ['emote','frame_count','total_ms','changed_frames','boundary_metrics']} for r in output]},indent=2))
if __name__=='__main__':main()
