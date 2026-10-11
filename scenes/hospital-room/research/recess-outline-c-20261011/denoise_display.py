"""Deterministic display-only OIDN copy; raw PNGs retained unchanged. No warp or registration."""
import os,sys,subprocess,tempfile,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
r=Path(__file__).parent;binary=r.parents[1]/'teahouse_v2/oidn/bin/oidnDenoise'
if not binary.is_file():
 # Candidate lives one level under hospital_object_audit in the cloud workspace.
 binary=r.parents[2]/'teahouse_v2/oidn/bin/oidnDenoise'
records=[]
for tag in 'FG':
 for variant in 'BC':
  source=r/f'{tag}_{variant}_same_camera_16spp_raw.png';out=r/f'{tag}_{variant}_same_camera_16spp_oidn.png';a=np.asarray(Image.open(source).convert('RGB')).astype(np.float32)/255;h,w=a.shape[:2]
  with tempfile.TemporaryDirectory(prefix='recess-c-oidn-') as td:
   tmp=Path(td);inp=tmp/'input.pfm';dest=tmp/'output.pfm'
   with inp.open('wb') as f:f.write(f'PF\n{w} {h}\n-1.0\n'.encode());np.flipud(a).astype('<f4').tofile(f)
   subprocess.run([str(binary),'--device','cpu','--ldr',str(inp),'--srgb','--quality','high','--threads','2','-o',str(dest)],check=True)
   with dest.open('rb') as f:
    assert f.readline().strip()==b'PF';ww,hh=map(int,f.readline().split());scale=float(f.readline());b=np.fromfile(f,dtype='<f4' if scale<0 else '>f4').reshape(hh,ww,3);b=np.flipud(b)
   Image.fromarray(np.uint8(np.clip(b,0,1)*255+.5)).save(out)
  records.append({'input':source.name,'output':out.name,'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'oidn':'2.5.1','mode':'RT LDR sRGB high CPU','threads':2,'samples_in_input':16,'pixel_geometry_transform':None})
(r/'denoise_manifest.json').write_text(json.dumps(records,indent=2))
