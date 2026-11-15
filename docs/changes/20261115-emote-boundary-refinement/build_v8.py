#!/usr/bin/env python3
"""Expand reviewed r1 local patches, preserve timing and outside pixels exactly."""
from refine_local import *
import csv

def save_gif(ims,times,path):
    ims[0].save(path,save_all=True,append_images=ims[1:],duration=times,loop=0,disposal=2,optimize=False)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--emotes',nargs='+',default=['02-butterfly','03-awake']);parser.add_argument('--output',default='v8-local-r2');args=parser.parse_args()
    summaries=[]
    for name in args.emotes:
        b=base(name);src=b/'v7-green-local-r2/CANDIDATE-color-master-768.gif';before,times=frames(src)
        out=b.parent/'20261115-boundary-refinement'/args.output;out.mkdir(parents=True,exist_ok=False)
        encoded=[];rows=[];allowed=[]
        for n,im in enumerate(before,1):
            a=np.array(im);arr=a.copy();mask=np.zeros(a.shape[:2],bool);details=[]
            methods=[stripe] if name.startswith('02') and 24<=n<=28 else []
            if name.startswith('03'):
                if n<=27:methods.append(collar)
                if 10<=n<=33:methods.append(knee)
            for method in methods:
                arr,m,detail=method(Image.fromarray(arr),n);mask|=m;details.append(detail)
            cand=Image.fromarray(arr);q=quantize_exact_outside(im,cand,mask);decoded=q.convert('RGB');c=np.array(decoded);diff=np.any(a!=c,axis=-1)
            pr=protect(name,n);color=np.array(Image.open(b/'v7-green-local-r2'/f'color-mask-{n:02d}.png'))>0
            assert not np.any(diff&~mask) and not np.any(diff&pr) and not np.any(diff&color) and not diff[:420].any()
            if mask.any():
                decoded.save(out/f'candidate-{n:02d}.png');Image.fromarray(mask.astype('uint8')*255).save(out/f'allowed-mask-{n:02d}.png');Image.fromarray(pr.astype('uint8')*255).save(out/f'protected-{n:02d}.png');Image.fromarray(np.dstack([c,mask.astype('uint8')*255])).save(out/f'local-layer-{n:02d}.png')
            encoded.append(q);allowed.append(mask)
            rows.append({'frame':n,'duration_ms':times[n-1],'changed_pixels':int(diff.sum()),'mask_pixels':int(mask.sum()),'outside_mask_changed_pixels':int((diff&~mask).sum()),'protected_changed_pixels':int((diff&pr).sum()),'green_color_changed_pixels':int((diff&color).sum()),'head_above_y420_changed_pixels':int(diff[:420].sum()),'source_rgb_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'candidate_rgb_sha256':hashlib.sha256(c.tobytes()).hexdigest(),'construction':details})
        stem='02' if name.startswith('02') else '03'
        master=out/f'{stem}-v8-CANDIDATE-master-768.gif';save_gif(encoded,times,master)
        actual,actual_times=frames(master);assert actual_times==times and len(actual)==len(before)
        for n,(a,im) in enumerate(zip(before,actual)):
            delta=np.any(np.array(a)!=np.array(im),axis=-1);assert not np.any(delta&~allowed[n]);assert hashlib.sha256(np.array(im).tobytes()).hexdigest()==rows[n]['candidate_rgb_sha256']
        previews=[im.resize((112,112),Image.Resampling.LANCZOS) for im in actual];save_gif(previews,times,out/f'{stem}-v8-CANDIDATE-preview-112.gif')
        paired=[]
        for a,c in zip(before,actual):
            canvas=Image.new('RGB',(640,344),'#eee');dr=ImageDraw.Draw(canvas);dr.text((8,4),'v7 before',font=FONT,fill='black');dr.text((328,4),'v8 candidate',font=FONT,fill='black');canvas.paste(a.resize((320,320),Image.Resampling.LANCZOS),(0,24));canvas.paste(c.resize((320,320),Image.Resampling.LANCZOS),(320,24));paired.append(canvas)
        save_gif(paired,times,out/f'{stem}-v7-v8-comparison-320.gif')
        ids=list(range(23,30)) if stem=='02' else list(range(1,35))+[50,51,52,53,54]
        small,small_times=frames(out/f'{stem}-v8-CANDIDATE-preview-112.gif');assert small_times==times
        sw=112;sh=136;cols=7;sheet=Image.new('RGB',(cols*sw,((len(ids)+cols-1)//cols)*sh),'#eee');dr=ImageDraw.Draw(sheet)
        for i,n in enumerate(ids):x=i%cols*sw;y=i//cols*sh;sheet.paste(small[n-1],(x,y+24));dr.text((x+2,y+3),f'F{n} {times[n-1]}ms',font=FONT,fill='black')
        sheet.save(out/f'{stem}-decoded-112-contact.png')
        report={'status':'candidate_pending_complete_visual_and_playback_review','source_v7':str(src.relative_to(ROOT)),'source_v7_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'frame_count':len(before),'frame_durations_ms':times,'total_ms':sum(times),'frames':rows,'output_dir':str(out.relative_to(ROOT)),'api_calls':0,'api_usage':None,'api_cost_usd':0,'api_configuration_present':False,'browser_playback':'Not retried: prior explicit managed-browser rejection; no actual playback claim.'}
        (out/'construction-and-validation.json').write_text(json.dumps(report,indent=2)+'\n');summaries.append(report)
        print(name,'done',sum(r['changed_pixels']>0 for r in rows),'changed frames',flush=True)
    (DOC/(args.output+'-validation.json')).write_text(json.dumps(summaries,indent=2)+'\n')
if __name__=='__main__':main()
