#!/usr/bin/env python3
"""Build explicitly rejected review loops with exact protected GIF pixels."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
from try_local_candidates import ROOT,compare

FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    results={}
    for name,affected in [('02-butterfly',list(range(24,29))),('03-awake',[17])]:
        source=ROOT/'emotes/sunburst/agent-emotes'/name
        parent=source/'versions/20261113-local-patch-review'
        out=parent/'rejected-review';out.mkdir(exist_ok=False)
        timing=json.loads((source/'manifest.json').read_text())['frame_durations_ms']
        original=[];candidates=[];paletted=[];masks={};changes=[]
        protected_rectangles=([[634,478,722,538],[460,473,528,540]] if name=='02-butterfly' else [[285,425,508,545]])
        for i in range(1,len(timing)+1):
            orig=Image.open(parent/'original-decoded'/f'{i:02d}.png').convert('RGB')
            original.append(orig);a=np.array(orig);candidate=orig.copy();mask=Image.new('L',orig.size)
            if i in affected:
                trial=parent/'v2-cloth-mapping'/f'{i:02d}'
                candidate=Image.open(trial/'candidate.png').convert('RGB');mask=Image.open(trial/'allowed-mask.png').convert('L')
                # Conservative exclusion of valid hands/gesture. Some defect residue may
                # remain; do not silently erase correct anatomy to improve the trial.
                for box in protected_rectangles:
                    candidate.paste(orig.crop(box),box[:2]);ImageDraw.Draw(mask).rectangle([box[0],box[1],box[2]-1,box[3]-1],fill=0)
                candidate.save(out/f'candidate-{i:02d}.png');mask.save(out/f'allowed-mask-{i:02d}.png')
                crop=[550,465,695,565] if name=='02-butterfly' else [440,530,585,655]
                compare(orig,candidate,mask,crop,out/f'comparison-{i:02d}.png')
            b=np.array(candidate);allowed=np.array(mask)>0;changed=np.any(a!=b,axis=-1)
            assert not np.any(changed&~allowed)
            # Lock each frame to its original GIF palette. Paste only changed pixels.
            base=orig.quantize(colors=256,method=Image.Quantize.MAXCOVERAGE,dither=Image.Dither.NONE)
            assert np.array_equal(np.array(base.convert('RGB')),a)
            q=candidate.quantize(palette=base,dither=Image.Dither.NONE)
            base.paste(q,(0,0),mask);paletted.append(base);candidates.append(base.convert('RGB'));masks[i]=allowed
            changes.append({'frame':i,'duration_ms':timing[i-1], 'original_rgb_sha256':hashlib.sha256(a.tobytes()).hexdigest(),
                            'candidate_changed_pixels':int(changed.sum()),'allowed_pixels':int(allowed.sum()),
                            'pixels_protected':int((~allowed).sum()),'png_changes_outside_mask':0})
        dest=out/'REJECTED-candidate-full-loop.gif'
        paletted[0].save(dest,save_all=True,append_images=paletted[1:],duration=timing,loop=0,disposal=2,optimize=False)
        decoded=[];durations=[]
        with Image.open(dest) as gif:
            assert gif.n_frames==len(timing)
            for j in range(gif.n_frames):
                gif.seek(j);im=gif.convert('RGB');decoded.append(im);durations.append(gif.info['duration'])
                if j+1 in affected: im.save(out/f'gif-decoded-{j+1:02d}.png')
                diff=np.any(np.array(im)!=np.array(original[j]),axis=-1)
                outside=int((diff&~masks[j+1]).sum());assert outside==0,(name,j+1,outside)
                for box in protected_rectangles:
                    assert im.crop(box).tobytes()==original[j].crop(box).tobytes()
                changes[j]['gif_decoded_changed_pixels']=int(diff.sum());changes[j]['gif_changes_outside_mask']=outside
        assert durations==timing
        small=[im.resize((112,112),Image.Resampling.LANCZOS) for im in decoded]
        small[0].save(out/'REJECTED-preview-112.gif',save_all=True,append_images=small[1:],duration=timing,loop=0,disposal=2,optimize=False)
        # Native 112px images, clearly identified as rejected; labels are outside artwork.
        ids=list(range(23,30)) if name=='02-butterfly' else [9,10,16,17,18,33,34]
        panel=Image.new('RGB',(112*len(ids),282),'#eee');d=ImageDraw.Draw(panel)
        for k,n in enumerate(ids):
            x=k*112;d.text((x+3,3),f'F{n} original',fill='black',font=FONT)
            panel.paste(original[n-1].resize((112,112),Image.Resampling.LANCZOS),(x,25))
            d.text((x+3,143),'REJECTED',fill='#a00000',font=FONT)
            panel.paste(decoded[n-1].resize((112,112),Image.Resampling.LANCZOS),(x,168))
        panel.save(out/'comparison-native-112.png')
        report={'status':'rejected_not_for_production','source_master_sha256':sha(source/'master.gif'),
            'candidate_gif_sha256':sha(dest),'frame_count':len(timing),'total_ms':sum(timing),'frame_durations_ms':timing,
            'modified_frames':affected,'modified_duration_ms':sum(timing[i-1] for i in affected),
            'timing_and_frame_count_unchanged':True,'all_decoded_gif_pixels_outside_masks_unchanged':True,
            'additional_protected_rectangles_xyxy_exclusive':protected_rectangles,
            'review_note':'Original animation and correct hand/gesture rectangles unchanged. Visible cloth seams/residue remain. No artistic acceptance.',
            'frames':changes}
        (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');results[name]=report
        print(name,'GIF exact protected-pixel checks passed; visual status REJECTED')
    (ROOT/'docs/changes/20261113-emote-local-patch-review/loop-verification-summary.json').write_text(json.dumps({n:{k:v for k,v in r.items() if k!='frames'} for n,r in results.items()},indent=2)+'\n')

if __name__=='__main__':main()
