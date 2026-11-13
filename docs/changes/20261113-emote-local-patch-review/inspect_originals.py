#!/usr/bin/env python3
"""Decode the original GIF and record its actual timeline without modifying it."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, json

ROOT=Path(__file__).resolve().parents[3]
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)

def contact(frames, ids, box, thumb, columns, path):
    tilew,tileh=thumb
    out=Image.new('RGB',(columns*tilew,((len(ids)+columns-1)//columns)*(tileh+24)), '#ececec')
    draw=ImageDraw.Draw(out)
    for n,i in enumerate(ids):
        im=frames[i-1]
        if box: im=im.crop(box)
        im=im.resize(thumb,Image.Resampling.LANCZOS)
        x=(n%columns)*tilew;y=(n//columns)*(tileh+24)
        out.paste(im,(x,y+24));draw.text((x+5,y+3),f'Frame {i}',font=FONT,fill='black')
    out.save(path)

def main():
    for name in ['02-butterfly','03-awake']:
        source=ROOT/'emotes/sunburst/agent-emotes'/name
        out=source/'versions/20261113-local-patch-review'
        raw=out/'original-decoded';raw.mkdir(parents=True,exist_ok=True)
        manifest=json.loads((source/'manifest.json').read_text())
        frames=[];timings=[];records=[]
        with Image.open(source/'master.gif') as gif:
            for i in range(gif.n_frames):
                gif.seek(i);im=gif.convert('RGB');frames.append(im);timings.append(gif.info['duration'])
                path=raw/f'{i+1:02d}.png';im.save(path)
                records.append({'frame':i+1,'duration_ms':gif.info['duration'],
                                'decoded_rgb_sha256':hashlib.sha256(im.tobytes()).hexdigest(),
                                'png_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                                'manifest_source':manifest['frame_review'][i]['source']})
        assert timings==manifest['frame_durations_ms']
        assert len(frames)==manifest['frames'] and sum(timings)==manifest['total_ms']
        (out/'original-verification.json').write_text(json.dumps({'master_sha256':hashlib.sha256((source/'master.gif').read_bytes()).hexdigest(),
            'frame_count':len(frames),'total_ms':sum(timings),'manifest_timing_exact_match':True,
            'note':'Decoded GIF RGB hashes are separate from pre-encoding PNG hashes in the original manifest.',
            'frames':records},indent=2)+'\n')
        contact(frames,list(range(1,len(frames)+1)),None,(160,160),9,out/'original-all-frames.png')
        if name=='02-butterfly':
            contact(frames,list(range(23,30)),None,(224,224),7,out/'original-23-29.png')
            contact(frames,list(range(23,30)),(460,430,715,585),(255,155),7,out/'original-hand-crops-23-29.png')
        else:
            contact(frames,list(range(9,38)),(220,400,690,675),(235,138),6,out/'original-hand-crops-09-37.png')
        print(name,len(frames),sum(timings), 'timeline matches manifest')

if __name__=='__main__':main()
