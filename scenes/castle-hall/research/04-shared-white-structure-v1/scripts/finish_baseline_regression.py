from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,subprocess,numpy as np
R=Path(__file__).resolve().parents[1];G=R/'regression';OIDN=R.parent/'teahouse_v2/oidn/bin/oidnDenoise'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def writepfm(p,a):
 with open(p,'wb') as f:f.write(('PF\n%d %d\n-1.0\n'%(a.shape[1],a.shape[0])).encode());np.flipud(a.astype('<f4')).tofile(f)
def readpfm(p):
 with open(p,'rb') as f:f.readline();w,h=map(int,f.readline().split());f.readline();return np.flipud(np.frombuffer(f.read(),dtype='<f4').reshape(h,w,3)).copy()
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
for n in ['fit_4528','holdout_4509']:
 p=G/(n+'_baseline_raw.png');meta=json.loads(p.with_suffix('.json').read_text());old=Image.open(p).convert('RGB');tmp=G/'input.pfm';temp=G/'output.pfm';writepfm(tmp,np.asarray(old,dtype=np.float32)/255);subprocess.run([str(OIDN),'--ldr',str(tmp),'--srgb','--threads','2','-o',str(temp)],check=True,stdout=subprocess.DEVNULL)
 clean=Image.fromarray(np.uint8(np.clip(readpfm(temp),0,1)*255+.5));cp=G/(n+'_baseline_clean.png');clean.save(cp);cm=dict(meta);cm.update({'image':cp.name,'sha256':sha(cp),'denoiser':'OIDN2.5.1 LDR sRGB color only, threads2','raw_sha256':sha(p)});cp.with_suffix('.json').write_text(json.dumps(cm,indent=2))
 npth=R/'renders'/(n+'_raw.png');new=Image.open(npth).convert('RGB');op=G/('overlay50_baseline_candidate_'+n+'_raw.png');overlay=Image.blend(old,new,.5);overlay.save(op);om={'image':op.name,'sha256':sha(op),'formula':'PIL.Image.blend(baseline raw RGB,candidate raw RGB,0.5); same 1180x664 pixels, no warp','baseline_image':p.name,'baseline_image_sha256':sha(p),'candidate_image':'../renders/'+npth.name,'candidate_image_sha256':sha(npth),'baseline_geometry_sha256':meta['geometry_baseline_sha256'],'candidate_geometry_sha256':meta['render_template_candidate_sha256'],'conditions':'same_condition_setup.json','source_acceptance':False};op.with_suffix('.json').write_text(json.dumps(om,indent=2))
 can=Image.new('RGB',(1180,3*704),(18,20,24));d=ImageDraw.Draw(can)
 for i,(im,lab) in enumerate([(clean,'OLD BASELINE - SAME CAMERA / LIGHTS / WHITE MATERIAL - no hidden walls'),(Image.open(R/'renders'/(n+'_clean.png')),'NEW CANDIDATE - fixed real opening / finite stair enclosure'),(overlay,'DIRECT 50% OLD RAW + NEW RAW - visibility regression, not source acceptance')]):
  d.text((12,i*704+9),lab,fill='white',font=font);can.paste(im,(0,i*704+40))
 co=G/('compare_baseline_candidate_'+n+'.jpg');can.save(co,quality=92,subsampling=0);co.with_suffix('.json').write_text(json.dumps({'image':co.name,'sha256':sha(co),'panels':[cp.name,'../renders/'+n+'_clean.png',op.name],'camera':meta['camera'],'conditions':'same_condition_setup.json'},indent=2))
 print('BASELINE_COMPARISON_DONE '+n,flush=True)
for p in [G/'input.pfm',G/'output.pfm']:
 if p.exists():p.unlink()
print('BASELINE_COMPARISONS_FINISHED',flush=True)
