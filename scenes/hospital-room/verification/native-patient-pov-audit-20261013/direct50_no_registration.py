"""Blend already matching-resolution source and render. No camera fitting, resize or warp.
Usage: python direct50_no_registration.py SOURCE.png RENDER.png OUTPUT.png
The caller must identify the actual render camera and its calibration limits separately.
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('render');p.add_argument('output');a=p.parse_args()
src,ren,out=map(Path,(a.source,a.render,a.output));receipt=out.with_suffix(out.suffix+'.json')
if out.exists() or receipt.exists():raise SystemExit('Refusing to overwrite existing output or receipt')
s=Image.open(src).convert('RGB');r=Image.open(ren).convert('RGB')
if s.size!=r.size:raise SystemExit('Source and render dimensions differ; resize is prohibited')
pixels=((np.asarray(s).astype(np.uint16)+np.asarray(r).astype(np.uint16))//2).astype(np.uint8)
Image.fromarray(pixels).save(out)
assert np.array_equal(np.asarray(Image.open(out)),pixels)
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
receipt.write_text(json.dumps({'source_name':src.name,'source_sha256':h(src),'render_name':ren.name,'render_sha256':h(ren),'output_name':out.name,'output_sha256':h(out),'dimensions':s.size,'formula':'floor((source uint16 + render uint16)/2)','registration':False,'resized':False,'camera_calibration':'not_asserted_by_this_utility','source_fidelity_accepted':False},indent=2))
print(out)
