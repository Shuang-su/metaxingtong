"""Reinsert only API mask pixels; unmasked 1024px RGB remains exactly original."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent

def main():
    src=HERE/'sources';base=Image.open(src/'xingtong-17-1024.png').convert('RGB');edited=Image.open(src/'frame17-api.png').convert('RGB');alpha=Image.open(src/'mask-17-1024.png').getchannel('A')
    assert base.size==edited.size==alpha.size==(1024,1024)
    result=Image.composite(base,edited,alpha)
    a=np.array(base);b=np.array(result);protected=np.array(alpha)==255
    outside_changed=int(np.any(a!=b,axis=2)[protected].sum());assert outside_changed==0
    result.save(HERE/'frame17-composited-1024.png');result.resize((768,768),Image.Resampling.LANCZOS).save(HERE/'frame17-composited-768.png')
    sheet=Image.new('RGB',(1536,512),'white')
    for x,im in enumerate([base,result,Image.open(src/'nailu-17-1024.png')]):sheet.paste(im.resize((512,512),Image.Resampling.LANCZOS),(x*512,0))
    sheet.save(HERE/'frame17-comparison.jpg',quality=95)
    # At 768px, blend onto the actual source again, so resampling cannot change
    # original head pixels outside the low-resolution edit support.
    original=Image.open(HERE.parent/'versions/01-original/master.gif');original.seek(16);original=original.convert('RGB')
    support=Image.fromarray(255-np.array(alpha)).resize((768,768),Image.Resampling.NEAREST)
    final=Image.composite(result.resize((768,768),Image.Resampling.LANCZOS),original,support);final.save(HERE/'frame17-final-768.png')
    preserved=np.array(support)==0;assert np.array_equal(np.array(final)[preserved],np.array(original)[preserved])
    report={'protected_pixels_1024':int(protected.sum()),'changed_protected_pixels_1024':outside_changed,'protected_pixels_768':int(preserved.sum()),'changed_protected_pixels_768':0,'composition':'original base; only mask-alpha-complement imported; reinserted original pixels again at 768px','image_sha256':hashlib.sha256((HERE/'frame17-final-768.png').read_bytes()).hexdigest()}
    (HERE/'frame17-composition.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
