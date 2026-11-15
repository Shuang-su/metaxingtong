#!/usr/bin/env python3
"""Build a full real-timeline candidate; only existing F5-21 collar pixels change."""
from fit_shared_collar import *
import hashlib,argparse

def save_loop(ims,times,path):
    ims[0].save(path,save_all=True,append_images=ims[1:],duration=times,loop=0,disposal=2,optimize=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='v9-shared-collar-r3');args=ap.parse_args()
    b=base('03-awake');src=b.parent/'20261115-boundary-refinement/v8-local-r2/03-v8-CANDIDATE-master-768.gif';before,times=frames(src)
    out=b.parent/'20261115-transition-v9'/args.output;out.mkdir(parents=True,exist_ok=False);encoded=[];records=[]
    for n,im in enumerate(before,1):
        a=np.array(im);mask=np.zeros((768,768),bool);details={};candidate=im
        hand=protect('03-awake',n);face=face_protection(im);color=np.array(Image.open(b/'v7-green-local-r2'/f'color-mask-{n:02d}.png'))>0;protected=hand|face|color;protected[:450]=True
        if 5<=n<=21:candidate,mask,details=patch_shared(im,n)
        q=quantize_exact_outside(im,candidate,mask);decoded=q.convert('RGB');c=np.array(decoded);diff=np.any(a!=c,axis=-1)
        assert not np.any(diff&(~mask|protected));assert not diff[552:].any()
        if mask.any():
            decoded.save(out/f'candidate-{n:02d}.png');Image.fromarray(mask.astype('uint8')*255).save(out/f'allowed-mask-{n:02d}.png');Image.fromarray(protected.astype('uint8')*255).save(out/f'protected-{n:02d}.png');Image.fromarray(np.dstack([c,mask.astype('uint8')*255])).save(out/f'local-layer-{n:02d}.png')
        records.append({'frame':n,'duration_ms':times[n-1],'mask_pixels':int(mask.sum()),'changed_pixels':int(diff.sum()),'source_rgb_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'candidate_rgb_sha256':hashlib.sha256(c.tobytes()).hexdigest(),'protected_changes':0,'outside_mask_changes':0,'construction':details});encoded.append(q)
    master=out/'03-v9-CANDIDATE-master-768.gif';save_loop(encoded,times,master);after,actual_times=frames(master);assert actual_times==times and len(after)==54
    save_loop([im.resize((112,112),Image.Resampling.LANCZOS) for im in after],times,out/'03-v9-CANDIDATE-preview-112.gif')
    comparisons=[]
    for a,c in zip(before,after):
        canvas=Image.new('RGB',(640,344),'#eee');dr=ImageDraw.Draw(canvas);dr.text((8,4),'v8 before',font=FONT,fill='black');dr.text((328,4),'v9 collar candidate',font=FONT,fill='black');canvas.paste(a.resize((320,320),Image.Resampling.LANCZOS),(0,24));canvas.paste(c.resize((320,320),Image.Resampling.LANCZOS),(320,24));comparisons.append(canvas)
    save_loop(comparisons,times,out/'03-v8-v9-comparison-320.gif')
    report={'status':'candidate_pending_full_timeline_review','base_commit':'7f310b95f7848b7b5f45008752cb620f3958a129','source_v8_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'donor_frame':54,'donor_original_file':str((b/'original-decoded/54.png').relative_to(ROOT)),'donor_file_sha256':hashlib.sha256((b/'original-decoded/54.png').read_bytes()).hexdigest(),'frame_count':54,'frame_durations_ms':times,'total_ms':sum(times),'frames':records,'api_calls':0,'api_cost_usd':0,'temporal_interpolation':False,'actual_playback':'unverified; prior management denial not retried or bypassed'}
    (out/'construction.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'output':str(out),'frames':54,'duration_ms':sum(times),'changed_frames':[r['frame'] for r in records if r['changed_pixels']]}),flush=True)
if __name__=='__main__':main()
