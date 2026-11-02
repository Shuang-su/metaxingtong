from pathlib import Path
import os
cpus=sorted(os.sched_getaffinity(0))[:2];os.sched_setaffinity(0,cpus)
os.environ['OMP_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2';os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
import json,hashlib,time,importlib.metadata as md
import numpy as np
from PIL import Image,ImageDraw
import torch
from transformers import AutoImageProcessor,AutoModelForDepthEstimation
D=Path(__file__).resolve().parent;E=D.parent/'depth-validation-20261102';S=D.parent/'recovered-source-candidates/arcade'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
torch.set_num_threads(2);torch.set_num_interop_threads(1)
proc=AutoImageProcessor.from_pretrained(E/'model',local_files_only=True,trust_remote_code=False,use_fast=False)
model=AutoModelForDepthEstimation.from_pretrained(E/'model',local_files_only=True,trust_remote_code=False,use_safetensors=True).eval()
art=json.loads((E/'model-artifact-manifest.json').read_text());assert sha(E/'model/model.safetensors')=='3152477ce0d8d6978d76b995120de97cb5b928701fd0f817769f59e249a16b70'
reports=[]
for stamp,expected in [('2560.58535','53091d7dc360b76e0db749671bd29c9dcee7ec9b5710e69359351cce5055a67e'),('2522.827654','b7be5314a9e94276b3ab882331ad8b9573995addd66b30c4faebe396cbba8ffa')]:
 source=S/f'BV1nxQPBkEGH_P1_{stamp}.png';assert sha(source)==expected;im=Image.open(source).convert('RGB');out=D/stamp;out.mkdir(exist_ok=True);x=proc(images=im,return_tensors='pt');t=time.time()
 with torch.inference_mode():raw=model(**x).predicted_depth[0].cpu().numpy().astype('float32')
 elapsed=time.time()-t;np.save(out/'relative-inverse-depth-model-grid.npy',raw,allow_pickle=False);finite=np.isfinite(raw);lo=float(raw[finite].min());hi=float(raw[finite].max());norm=np.clip((raw-lo)/(hi-lo),0,1)
 Image.fromarray((norm*65535).round().astype('uint16')).save(out/'gray16-model-grid.png')
 aligned=torch.nn.functional.interpolate(torch.from_numpy(raw)[None,None],size=(im.height,im.width),mode='bicubic',align_corners=False)[0,0].numpy();np.save(out/'relative-inverse-depth-derived-source-grid.npy',aligned,allow_pickle=False)
 gray=Image.fromarray((np.clip((aligned-lo)/(hi-lo),0,1)*255).round().astype('uint8'));gray.save(out/'gray8-derived-source-grid.png')
 # Independent overlapping manual bit masks. They are warnings, not learned confidence.
 masks={}
 def make(bit,name,rects=(),polys=()):
  m=Image.new('L',im.size,0);dr=ImageDraw.Draw(m)
  for r in rects:dr.rectangle(r,fill=1)
  for q in polys:dr.polygon(q,fill=1)
  m.save(out/f'mask-{name}.png');masks[bit]=np.array(m,dtype=np.uint8)
 if stamp.startswith('2560'):
  make(1,'character-conservative',[(850,185,1110,900)])
  make(2,'reflective-surface',polys=[[(0,685),(180,675),(255,815),(0,865)],[(225,655),(1010,580),(1140,690),(1135,740),(335,820)],[(1030,580),(1615,532),(1850,610),(1840,657),(1190,722)],[(0,865),(335,820),(1135,740),(1840,657),(1919,650),(1919,1079),(0,1079)]])
  make(4,'emissive-screen-controls',rects=[(310,235,810,325),(1040,200,1460,300)],polys=[[(320,0),(740,0),(760,220),(340,240)],[(1040,0),(1390,0),(1410,195),(1055,210)]])
 else:
  make(1,'character-conservative',[(840,160,1270,1079)])
  make(2,'reflective-surface',[(0,390,450,1079)])
  make(4,'emissive-screen-controls',rects=[(490,590,1040,705),(1350,520,1919,670)],polys=[[(570,340),(1030,285),(1045,540),(545,600)],[(1420,210),(1919,170),(1919,525),(1370,560)]])
 make(8,'frame-border-uncertain',[(0,0,1919,19),(0,1060,1919,1079),(0,0,19,1079),(1900,0,1919,1079)])
 bits=np.zeros((im.height,im.width),np.uint8)
 for bit,m in masks.items():bits|=m*bit
 Image.fromarray(bits).save(out/'manual-warning-bitmask-source-grid.png');Image.new('L',im.size,255).save(out/'confidence-UNKNOWN-255-source-grid.png')
 sheet=Image.new('RGB',(1440,432),'#222');draw=ImageDraw.Draw(sheet)
 for i,(a,label) in enumerate([(im,'NATIVE source display resize'),(gray.convert('RGB'),'DERIVED relative inverse depth: white generally nearer'),(Image.fromarray(bits*15).convert('RGB'),'MANUAL warning mask, 0 NOT certified valid')]):sheet.paste(a.resize((480,270)),(i*480,32));draw.text((i*480+5,8),label,fill='white')
 draw.text((8,320),'No metric scale, no calibrated confidence. Bicubic aligned map is NOT native-resolution inference.',fill='white');sheet.save(out/'source-depth-warning-contact.jpg',quality=90)
 r={'purpose':'Nov2 remake of historical arcade, NOT a new scene; monocular depth diagnostic only','source':{'path':str(source),'BV':'BV1nxQPBkEGH','part':1,'time_seconds':float(stamp),'size_wh':list(im.size),'sha256':expected,'bytes':source.stat().st_size,'crop':[0,0,im.width,im.height],'provenance':'Recovered historical native frame; original source hash checked; no fresh login/quality verification'},'method':{'repo':art['repo'],'revision':art['revision'],'weights_sha256':sha(E/'model/model.safetensors'),'license':'apache-2.0','local_files_only':True,'trust_remote_code':False,'format':'safetensors','device':'cpu','cpu_affinity':cpus,'torch_threads':2,'interop_threads':1,'dtype':'float32','input_tensor_shape':list(x['pixel_values'].shape),'model_grid_hw':list(raw.shape),'derived_aligned_wh':list(im.size),'processor_config':json.loads((E/'model/preprocessor_config.json').read_text()),'versions':{n:md.version(n) for n in ['torch','transformers','safetensors','pillow','numpy']},'inference_seconds':elapsed},'values':{'min':lo,'max':hi,'nonfinite':int((~finite).sum()),'definition':'relative inverse-depth-like model prediction; white larger generally nearer, not meters or calibrated disparity','normalization':'Per-image min/max; images not quantitatively comparable. Original model-grid float32 retained. Source-aligned float32/gray derived by bicubic align_corners=False, no extra native detail.'},'mask':{'bit1':'manual conservative actor bbox incl background, not instance segmentation','bit2':'manual reflective dance pads/floor or claw glass; overlap allowed, not exhaustive','bit4':'manual emissive screens/control regions; screen scene content NOT physical depth','bit8':'20px frame-edge caution strip; does not represent hidden off-frame geometry','zero':'unlabelled NOT certified valid','confidence':'255 everywhere is UNKNOWN; model gives no calibrated confidence','occluded_hidden':'unknown, not inferred completion; printed static poster silhouette not a moving actor'},'outputs':[]}
 r['outputs']=[{'path':f.name,'bytes':f.stat().st_size,'sha256':sha(f),'size_wh':list(Image.open(f).size) if f.suffix in ['.png','.jpg'] else None} for f in sorted(out.iterdir()) if f.is_file()]
 (out/'report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));reports.append({'stamp':stamp,'grid':list(raw.shape),'seconds':elapsed,'source_sha':expected});print(json.dumps(reports[-1]),flush=True)
(D/'completion.json').write_text(json.dumps(reports,indent=2));print('TWO_IMAGES_COMPLETE',flush=True)
