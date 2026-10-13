import json,hashlib,shutil,subprocess
import numpy as np
from PIL import Image,ImageDraw
from pathlib import Path
r=Path(__file__).parent;parent=r.parent;obs=json.loads((r/'observations.json').read_text())['observations'];fit=json.loads((r/'fit_results.json').read_text());bp=json.loads((r/'blender_projection_verification.json').read_text());checks=[]
exe=parent.parent/'teahouse_v2/oidn/bin/oidnDenoise'
for path in list(r.glob('*_raw.png')):
 out=r/(path.stem.replace('_raw','_denoised')+'.png');a=np.asarray(Image.open(path).convert('RGB')).astype(np.float32)/255.;h,w=a.shape[:2];temp=r/(path.stem+'.pfm');tmpout=r/(path.stem+'.out.pfm')
 with temp.open('wb') as f:f.write(f'PF\n{w} {h}\n-1.0\n'.encode());np.flipud(a).astype('<f4').tofile(f)
 subprocess.run([str(exe),'--device','cpu','--ldr',str(temp),'--srgb','--quality','high','--threads','2','-o',str(tmpout)],check=True,stdout=subprocess.DEVNULL)
 with tmpout.open('rb') as f:
  f.readline();ww,hh=map(int,f.readline().split());scale=float(f.readline());b=np.flipud(np.fromfile(f,dtype='<f4' if scale<0 else '>f4').reshape(hh,ww,3))
 Image.fromarray(np.uint8(np.clip(b,0,1)*255+.5)).save(out);temp.unlink();tmpout.unlink()
for tag in 'FGH':
 source=next((parent/'refs/extracted/hospital/frames').glob(f'*-{tag}-*'));src=Image.open(source).convert('RGB');ann=src.copy();d=ImageDraw.Draw(ann)
 for a in obs[tag]:
  col={'train':'#00ff00','holdout':'#ff00ff','direction_only':'#ffbf00'}[a['split']];uv=a['observed'];uv=[uv] if a['kind']=='point' else uv
  if a['kind']=='line':d.line(tuple(tuple(v) for v in uv),fill=col,width=3)
  for x,y in uv:d.ellipse((x-5,y-5,x+5,y+5),outline=col,width=2)
  x,y=uv[0];d.text((min(x+9,1720),max(y-14,0)),a['id']+' '+a['split'],fill=col,stroke_width=1,stroke_fill='black')
 ann.save(r/f'{tag}_source_annotated.png')
 orig=parent/'candidate_b'/f'{tag}_B_legacy_camera_1920.png';new=r/f'{tag}_candidate_camera_raw.png';paths=[('original',orig),('candidate',new)]
 if tag=='G':paths.append(('fixed_focal',r/'G_fixed_focal_alternative_raw.png'))
 for label,p in paths:
  a=np.asarray(src,dtype=np.uint16);b=np.asarray(Image.open(p).convert('RGB'),dtype=np.uint16);assert a.shape==b.shape==(1080,1920,3);z=((a+b)//2).astype(np.uint8);out=r/f'{tag}_{label}_direct50.png';Image.fromarray(z).save(out);read=np.asarray(Image.open(out));delta=np.abs(read.astype(int)-z.astype(int));checks.append({'file':out.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'render_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'formula':'floor((source_uint16 + raw_render_uint16)/2)','size':[1920,1080],'max_integer_error':int(delta.max()),'different_pixels':int(np.any(delta,axis=2).sum()),'resampling':False,'warping':False})
  for cropname,box in [('architecture',(800,0,1920,600)),('foreground',(0,650,1920,1080))]:Image.fromarray(z).crop(box).save(r/f'{tag}_{label}_{cropname}_direct50_crop.png')
 # Review panel is clearly downscaled presentation; pixel-exact overlays above remain original resolution.
 ims=[src,Image.open(parent/'candidate_b'/f'{tag}_B_legacy_camera_1920_denoised.png') if (parent/'candidate_b'/f'{tag}_B_legacy_camera_1920_denoised.png').exists() else Image.open(orig),Image.open(r/f'{tag}_candidate_camera_denoised.png')]
 labels=[f'{tag} NATIVE SOURCE',f'{tag} ORIGINAL CAMERA / B MODEL',f'{tag} CAMERA CANDIDATE - NOT ADOPTED' if tag!='H' else 'H UNCHANGED CAMERA / NOT IDENTIFIABLE']
 if tag=='G':ims.append(Image.open(r/'G_fixed_focal_alternative_denoised.png'));labels.append('G FIXED FOCAL ALTERNATIVE - NOT ADOPTED')
 panel=Image.new('RGB',(960,570*len(ims)),(25,25,25));dd=ImageDraw.Draw(panel)
 for i,(im,lab) in enumerate(zip(ims,labels)):dd.text((12,i*570+10),lab,fill='white');panel.paste(im.resize((960,540)),(0,i*570+30))
 panel.save(r/f'{tag}_fullframe_review_panel.png')
(r/'direct50_pixel_checks.json').write_text(json.dumps(checks,indent=2))
# Verify analytic fit projection against Blender, in original and chosen candidate views.
from scipy.spatial.transform import Rotation
errs=[]
for tag in 'FGH':
 for mode,v in bp[tag].items():
  x=np.array(fit[tag]['original'] if mode=='original' else fit[tag]['candidates'][mode]['parameters']);R=Rotation.from_rotvec(x[:3]).as_matrix();f=np.exp(x[6])/36*1920
  for a in obs[tag]:
   p=np.array(a['xyz']).reshape(-1,3);vv=(p-x[3:6])@R;uv=np.c_[960+x[7]+f*vv[:,0]/-vv[:,2],540+x[8]-f*vv[:,1]/-vv[:,2]];b=np.array(v['anchors'][a['id']]);errs.append(float(np.max(np.abs(uv-b[:,:2]))))
(r/'projection_math_check.json').write_text(json.dumps({'max_blender_vs_scipy_difference_px':max(errs),'passed_0_002_px':max(errs)<.002,'comparison_count':len(errs)},indent=2))
print('direct50',len(checks),'checks',all(x['max_integer_error']==0 for x in checks),'projectionmax',max(errs))
