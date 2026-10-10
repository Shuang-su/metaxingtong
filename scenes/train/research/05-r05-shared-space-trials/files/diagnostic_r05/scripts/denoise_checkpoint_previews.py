from pathlib import Path
from PIL import Image
import numpy as np,subprocess,json,hashlib
R=Path(__file__).resolve().parents[1];outdir=R/'checkpoint_r05c/preview_denoised';outdir.mkdir(parents=True,exist_ok=True);tmp=R/'analysis/denoise_tmp';tmp.mkdir(exist_ok=True)
BIN='/workspace/scratch/fa58bfcf0425/teahouse_v2/oidn/bin/oidnDenoise'
for p in sorted((R/'checkpoint_r05c').glob('*.png')):
 meta=p.with_suffix('.json')
 if not meta.exists():continue
 d=json.loads(meta.read_text());h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==d['output_sha256'];out=outdir/p.name
 if out.exists() and out.with_suffix('.json').exists() and json.loads(out.with_suffix('.json').read_text()).get('raw_sha256')==h:continue
 a=np.asarray(Image.open(p).convert('RGB'),np.float32)/255;inp=tmp/'input.pfm';op=tmp/'output.pfm'
 with inp.open('wb') as f:f.write(f'PF\n{a.shape[1]} {a.shape[0]}\n-1.0\n'.encode());np.flipud(a).tofile(f)
 subprocess.run([BIN,'--ldr',str(inp),'--srgb','-o',str(op),'--threads','2'],check=True,stdout=subprocess.DEVNULL)
 with op.open('rb') as f:
  f.readline();w,ht=map(int,f.readline().split());f.readline();b=np.flipud(np.frombuffer(f.read(),dtype='<f4').reshape(ht,w,3))
 Image.fromarray((np.clip(b,0,1)*255+.5).astype(np.uint8)).save(out)
 out.with_suffix('.json').write_text(json.dumps({'raw_source':str(p.relative_to(R)),'raw_sha256':h,'input_blend_sha256':d.get('input_blend_sha256',d.get('input_blend_sha256_at_load')),'operation':'OIDN LDR sRGB standard denoising, same pixel lattice, no warp/crop/rescale','threads':2,'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2));print(out.name,flush=True)
for p in tmp.glob('*.pfm'):p.unlink()
