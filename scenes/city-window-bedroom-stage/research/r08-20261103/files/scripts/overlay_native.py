"""Direct full-frame 50% blend with no geometric transformation."""
from PIL import Image
import numpy as np,sys,json,hashlib
from pathlib import Path
args=sys.argv[1:]; src,render,out=map(Path,args[:3])
a=Image.open(src).convert('RGB'); b=Image.open(render).convert('RGB')
assert a.size==b.size,(a.size,b.size)
blend=Image.blend(a,b,.5);blend.save(out)
expected=((np.array(a,dtype=np.uint16)+np.array(b,dtype=np.uint16))//2).astype(np.uint8)
actual=np.array(Image.open(out).convert('RGB'))
record={'source':str(src),'render':str(render),'output':str(out),'width':a.width,'height':a.height,
 'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'render_sha256':hashlib.sha256(render.read_bytes()).hexdigest(),
 'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'max_formula_pixel_error':int(np.abs(actual.astype(int)-expected.astype(int)).max()),
 'transforms':'None. Full original frames; RGB conversion only. Direct 50% blend, floor rounding.',
 'interpretation':'Formula check is not camera calibration or source-geometry validation.'}
out.with_suffix('.json').write_text(json.dumps(record,indent=2))
