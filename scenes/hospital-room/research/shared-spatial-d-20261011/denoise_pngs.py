from pathlib import Path
import os,shutil,sys,tempfile,subprocess,numpy as np
from PIL import Image
# Frozen output dependency: Intel Open Image Denoise 2.5.1, CPU RT LDR sRGB high, two threads.
# Set OIDN_BIN to the 2.5.1 oidnDenoise executable, or place it on PATH.
binary=os.environ.get('OIDN_BIN') or shutil.which('oidnDenoise')
if not binary:raise SystemExit('Open Image Denoise 2.5.1 is required; set OIDN_BIN or add oidnDenoise to PATH.')
for name in sys.argv[1:]:
 p=Path(name);im=np.asarray(Image.open(p).convert('RGB')).astype(np.float32)/255;h,w=im.shape[:2]
 with tempfile.TemporaryDirectory() as td:
  a=Path(td)/'a.pfm';b=Path(td)/'b.pfm'
  with open(a,'wb') as f:f.write(f'PF\n{w} {h}\n-1.0\n'.encode());np.flipud(im).astype('<f4').tofile(f)
  subprocess.run([str(binary),'--device','cpu','--ldr',str(a),'--srgb','--quality','high','--threads','2','-o',str(b)],check=True,stdout=subprocess.DEVNULL)
  with open(b,'rb') as f:
   assert f.readline().strip()==b'PF';ww,hh=map(int,f.readline().split());s=float(f.readline());data=np.fromfile(f,'<f4' if s<0 else '>f4').reshape(hh,ww,3)
  out=p.with_stem(p.stem+'_oidn');Image.fromarray(np.uint8(np.clip(np.flipud(data),0,1)*255+.5)).save(out);print(out)
