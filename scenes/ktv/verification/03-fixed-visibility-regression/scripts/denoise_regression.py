from pathlib import Path
from PIL import Image
import numpy as np,subprocess,json,hashlib
R=Path('/workspace/scratch/fa58bfcf0425/ktv_fixed_visibility_20261010')
BIN='/workspace/scratch/fa58bfcf0425/teahouse_v2/oidn/bin/oidnDenoise'
log=[]
for p in sorted((R/'renders').glob('*.png')):
 if p.stem.endswith('_denoised'):continue
 dst=p.with_name(p.stem+'_denoised.png')
 if dst.exists():continue
 a=np.asarray(Image.open(p).convert('RGB'),np.float32)/255;inp=p.with_suffix('.pfm');out=p.with_name(p.stem+'_denoised.pfm')
 with inp.open('wb') as fp:
  fp.write(f'PF\n{a.shape[1]} {a.shape[0]}\n-1.0\n'.encode());np.flipud(a).tofile(fp)
 subprocess.run([BIN,'--ldr',str(inp),'--srgb','-o',str(out),'--threads','2'],check=True,stdout=subprocess.DEVNULL)
 with out.open('rb') as fp:
  fp.readline();w,h=map(int,fp.readline().decode().strip().split());fp.readline();b=np.flipud(np.fromfile(fp,dtype='<f4').reshape(h,w,3))
 Image.fromarray((np.clip(b,0,1)*255+.5).astype(np.uint8)).save(dst);inp.unlink();out.unlink()
 log.append({'input':p.name,'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'output':dst.name,'output_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'method':'OIDN 2.5.1 LDR sRGB color only, threads=2; raw render retained','dimensions':[w,h]})
 print(dst.name,flush=True)
old=R/'qa/denoise_log.json';previous=json.load(old.open()) if old.exists() else [];json.dump(previous+log,old.open('w'),indent=2)
