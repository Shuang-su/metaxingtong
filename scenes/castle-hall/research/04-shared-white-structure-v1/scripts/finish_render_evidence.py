from pathlib import Path
import json,hashlib,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];OIDN=R.parent/'teahouse_v2/oidn/bin/oidnDenoise'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pfmwrite(p,a):
 with open(p,'wb') as f:f.write(('PF\n%d %d\n-1.0\n'%(a.shape[1],a.shape[0])).encode());np.flipud(a.astype('<f4')).tofile(f)
def pfmread(p):
 with open(p,'rb') as f:f.readline();w,h=map(int,f.readline().split());f.readline();return np.flipud(np.frombuffer(f.read(),dtype='<f4').reshape(h,w,3)).copy()
expected=['fit_4528','fit_4529','holdout_4527','holdout_4509','normal_main','qa_arch_inside','qa_stair_return']
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
except:font=None
for name in expected:
 path=R/'renders'/(name+'_raw.png');meta=json.loads(path.with_suffix('.json').read_text());raw=Image.open(path).convert('RGB');p=R/'qa/tmp_input.pfm';q=R/'qa/tmp_output.pfm';pfmwrite(p,np.array(raw,dtype=np.float32)/255)
 subprocess.run([str(OIDN),'--ldr',str(p),'--srgb','--threads','2','-o',str(q)],check=True,stdout=subprocess.DEVNULL)
 clean=Image.fromarray(np.uint8(np.clip(pfmread(q),0,1)*255+.5));cp=R/'renders'/(name+'_clean.png');clean.save(cp);cm=dict(meta);cm.update({'image':cp.name,'sha256':sha(cp),'denoised':True,'denoiser':'Standalone Intel OIDN 2.5.1, color-only LDR sRGB, 2 threads; no albedo/normal guides','raw_image':path.name,'raw_sha256':sha(path),'note':'Clean image is presentation assistance; raw render and raw direct overlay remain the geometric evidence.'});cp.with_suffix('.json').write_text(json.dumps(cm,indent=2))
 if meta['source_file']:
  sp=R/'inputs'/meta['source_file'];source=Image.open(sp).convert('RGB');assert source.size==raw.size==(1180,664)
  for kind,render in [('raw',raw),('clean',clean)]:
   ov=Image.blend(source,render,.5);op=R/'qa'/('overlay50_'+name+'_'+kind+'.png');ov.save(op);om={'image':op.name,'sha256':sha(op),'formula':'PIL.Image.blend(source.convert(RGB), render.convert(RGB), 0.5), same 1180x664 pixel grid','source':str(sp.relative_to(R)),'source_sha256':sha(sp),'render':'renders/'+name+'_'+kind+'.png','render_sha256':sha(R/'renders'/(name+'_'+kind+'.png')),'model_sha256':meta['model_sha256'],'geometry_signature':meta['geometry_signature'],'reference_warp':False,'reference_resize':False,'mask_applied_to_image':False,'source_time_seconds':meta['source_time_seconds'],'acceptance':False};op.with_suffix('.json').write_text(json.dumps(om,indent=2))
  contact=Image.new('RGB',(1180,3*(664+40)),(18,20,24));d=ImageDraw.Draw(contact)
  for i,(im,label) in enumerate([(source,'SOURCE '+str(meta['source_time_seconds'])+'s | 1180x664 displayed core'),(clean,'SAME FIXED WHITE GEOMETRY | physical camera | OIDN presentation'),(Image.blend(source,raw,.5),'DIRECT 50% SOURCE + RAW RENDER | NO WARP | candidate, not accepted')]):
   y=i*704;d.text((12,y+9),label,fill='white',font=font);contact.paste(im,(0,y+40))
  contact.save(R/'qa'/('compare_'+name+'_contact.jpg'),quality=92,subsampling=0)
 print('EVIDENCE_DONE '+name,flush=True)
for p in [R/'qa/tmp_input.pfm',R/'qa/tmp_output.pfm']:
 if p.exists():p.unlink()
# Compact normal/internal inspection sheet; complete renders retained individually.
can=Image.new('RGB',(1180,3*372),(20,22,26));d=ImageDraw.Draw(can)
for i,(name,label) in enumerate([('normal_main','NORMAL MAIN - full fixed shell'),('qa_arch_inside','ARCH INSPECTION - upper 2 treads / landing / enclosure are INFERRED'),('qa_stair_return','RETURN VIEW - camera on INFERRED landing; onward destination UNKNOWN')]):
 im=Image.open(R/'renders'/(name+'_clean.png')).resize((590,332));can.paste(im,(0,i*372+40));d.text((12,i*372+9),label,fill='white',font=font)
# use full width instead of empty half: save regular 3 vertically stacked 1180 cores
can=Image.new('RGB',(1180,3*704),(20,22,26));d=ImageDraw.Draw(can)
for i,(name,label) in enumerate([('normal_main','NORMAL MAIN - full fixed shell'),('qa_arch_inside','ARCH INSPECTION - upper 2 treads / landing / enclosure are INFERRED'),('qa_stair_return','RETURN VIEW - camera on INFERRED landing; onward destination UNKNOWN')]):
 can.paste(Image.open(R/'renders'/(name+'_clean.png')),(0,i*704+40));d.text((12,i*704+9),label,fill='white',font=font)
can.save(R/'qa/normal_and_internal_inspection.jpg',quality=92,subsampling=0)
print('EVIDENCE_FINISHED',flush=True)
