#!/usr/bin/env python3
"""Read-only bounded normalized correlation for local patch placement."""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.signal import correlate2d
import numpy as np,json
from try_local_candidates import ROOT

def match_translation(reference,target,box,dx_range,dy_range):
    a=np.array(reference.convert('L'),dtype=float);b=np.array(target.convert('L'),dtype=float)
    x0,y0,x1,y1=box;template=a[y0:y1,x0:x1];template-=template.mean()
    search=b[y0+dy_range[0]:y1+dy_range[1],x0+dx_range[0]:x1+dx_range[1]]
    ones=np.ones(template.shape);N=template.size
    numerator=correlate2d(search,template,mode='valid')
    sums=correlate2d(search,ones,mode='valid');squares=correlate2d(search*search,ones,mode='valid')
    denominator=np.sqrt(np.maximum(squares-sums*sums/N,1)*np.sum(template*template))
    score=numerator/denominator;y,x=np.unravel_index(np.argmax(score),score.shape)
    return {'dx':int(x+dx_range[0]),'dy':int(y+dy_range[0]),'ncc':float(score[y,x]),'reference_box':box}

def main():
    records={}
    for name,reference_id,ids,regions in [
       ('02-butterfly',27,range(24,29),{'hem':([540,495,573,519],[-9,9],[-9,9]),'stripe':([540,532,582,556],[-9,9],[-9,9])}),
       ('03-awake',17,range(1,34),{'shoulder':([250,478,315,518],[-25,25],[-65,25]),'knee':([478,574,565,634],[-15,15],[-20,20])})]:
        base=ROOT/'emotes/sunburst/agent-emotes'/name/'versions/20261113-local-patch-review'
        out=base/'v6-contour-and-motion';out.mkdir(exist_ok=True)
        reference=Image.open(base/'original-decoded'/f'{reference_id:02d}.png').convert('RGB')
        rows=[]
        for n in ids:
            target=Image.open(base/'original-decoded'/f'{n:02d}.png').convert('RGB');row={'frame':n}
            for label,(box,dxs,dys) in regions.items():
                if name=='03-awake' and ((label=='shoulder' and n>27) or (label=='knee' and n<10)):continue
                row[label]=match_translation(reference,target,box,dxs,dys)
            rows.append(row)
        records[name]=rows
        (out/'registration.json').write_text(json.dumps(rows,indent=2)+'\n')
        print(name,[(r['frame'],{k:(v['dx'],v['dy'],round(v['ncc'],3)) for k,v in r.items() if k!='frame'}) for r in rows])
        if name=='03-awake':
            canvas=Image.new('RGB',(9*180,3*172),'#eee');d=ImageDraw.Draw(canvas)
            for k,row in enumerate(rows[:27]):
                n=row['frame'];m=row['shoulder'];im=Image.open(base/'original-decoded'/f'{n:02d}.png').convert('RGB')
                b=[250+m['dx'],478+m['dy'],315+m['dx'],518+m['dy']]
                ImageDraw.Draw(im).rectangle(b,outline='red',width=2)
                crop=im.crop((220,405,355,525)).resize((180,160))
                x=k%9*180;y=k//9*172;canvas.paste(crop,(x,y+12));d.text((x+3,y),f'F{n} {m["ncc"]:.2f}',fill='black')
            canvas.save(out/'shoulder-placement-review.png')

if __name__=='__main__':main()
