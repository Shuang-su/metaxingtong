import os,sys,subprocess
from PIL import Image
import numpy as np
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OIDN='/workspace/scratch/fa58bfcf0425/teahouse_v2/oidn/bin/oidnDenoise'
def pfmwrite(p,a):
 with open(p,'wb') as f:f.write(('PF\n%d %d\n-1.0\n'%(a.shape[1],a.shape[0])).encode());np.flipud(a.astype('<f4')).tofile(f)
def pfmread(p):
 with open(p,'rb') as f:f.readline();w,h=map(int,f.readline().split());f.readline();return np.flipud(np.frombuffer(f.read(),dtype='<f4').reshape(h,w,3)).copy()
for f in sys.argv[1:]:
 a=np.array(Image.open(f).convert('RGB'),dtype=np.float32)/255;p=ROOT+'/qa/input.pfm';q=ROOT+'/qa/output.pfm';pfmwrite(p,a)
 subprocess.run([OIDN,'--ldr',p,'--srgb','--threads','2','-o',q],check=True,stdout=subprocess.DEVNULL)
 out=os.path.splitext(f)[0]+'_clean.png';Image.fromarray(np.uint8(np.clip(pfmread(q),0,1)*255+.5)).save(out);print(out)
for p in [ROOT+'/qa/input.pfm',ROOT+'/qa/output.pfm']:
 if os.path.exists(p):os.remove(p)
