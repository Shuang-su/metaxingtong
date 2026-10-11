from pathlib import Path
from PIL import Image
import numpy as np,subprocess,shutil
R=Path(__file__).resolve().parents[1];raw=R/'renders_raw';raw.mkdir(exist_ok=True);tmp=R/'analysis/denoise_tmp';tmp.mkdir(exist_ok=True)
BIN='/workspace/scratch/fa58bfcf0425/teahouse_v2/oidn/bin/oidnDenoise'
for p in sorted((R/'renders').glob('*.png')):
 dst=raw/p.name
 if dst.exists():continue
 shutil.copy2(p,dst);a=np.asarray(Image.open(p).convert('RGB'),np.float32)/255;inp=tmp/'input.pfm';out=tmp/'output.pfm'
 with inp.open('wb') as f:f.write(f'PF\n{a.shape[1]} {a.shape[0]}\n-1.0\n'.encode());np.flipud(a).tofile(f)
 subprocess.run([BIN,'--ldr',str(inp),'--srgb','-o',str(out),'--threads','2'],check=True,stdout=subprocess.DEVNULL)
 with out.open('rb') as f:
  f.readline();w,h=map(int,f.readline().split());f.readline();b=np.flipud(np.frombuffer(f.read(),dtype='<f4').reshape(h,w,3))
 Image.fromarray((np.clip(b,0,1)*255+.5).astype(np.uint8)).save(p);print('DENOISED_REVIEW',p.name,flush=True)
for p in tmp.glob('*.pfm'):p.unlink()
