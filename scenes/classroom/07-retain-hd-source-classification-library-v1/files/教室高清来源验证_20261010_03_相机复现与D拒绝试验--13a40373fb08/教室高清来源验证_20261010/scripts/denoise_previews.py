from PIL import Image
import numpy as np,subprocess,sys
from pathlib import Path
BIN='/workspace/scratch/fa58bfcf0425/teahouse_v2/oidn/bin/oidnDenoise'
for f in sys.argv[1:]:
 p=Path(f);a=np.asarray(Image.open(p).convert('RGB'),np.float32)/255.;inp=p.with_suffix('.pfm');out=p.with_name(p.stem+'_denoised.pfm')
 with inp.open('wb') as fp:
  fp.write(f'PF\n{a.shape[1]} {a.shape[0]}\n-1.0\n'.encode());np.flipud(a).tofile(fp)
 subprocess.run([BIN,'--ldr',str(inp),'--srgb','-o',str(out),'--threads','3'],check=True,stdout=subprocess.DEVNULL)
 with out.open('rb') as fp:
  h=fp.readline();sz=fp.readline().decode().strip();w,h=map(int,sz.split());scale=float(fp.readline());b=np.fromfile(fp,dtype='<f4').reshape(h,w,3);b=np.flipud(b)
 dst=p.with_name(p.stem+'_denoised.png');Image.fromarray((np.clip(b,0,1)*255+.5).astype(np.uint8)).save(dst)
 inp.unlink();out.unlink();print(dst)
