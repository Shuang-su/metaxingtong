from pathlib import Path
import argparse, hashlib, json, time, importlib.metadata as md
import numpy as np
from PIL import Image, ImageDraw
import torch
from transformers import AutoImageProcessor, AutoModelForDepthEstimation

ap=argparse.ArgumentParser()
ap.add_argument('--source',required=True)
ap.add_argument('--metadata',required=True,help='JSON with source identity, time, pixel provenance, optional exclusions')
ap.add_argument('--out',required=True)
args=ap.parse_args()
p=Path(__file__).resolve().parent; source=Path(args.source); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
meta=json.loads(Path(args.metadata).read_text())
if meta.get('sha256'): assert sha(source)==meta['sha256']
img=Image.open(source).convert('RGB')
artifact=json.loads((p/'provenance/prior-model-artifact-manifest.json').read_text())
for a in artifact['artifacts']: assert sha(p/'model'/a['path'])==a['sha256']
torch.set_num_threads(4); torch.set_num_interop_threads(1)
proc=AutoImageProcessor.from_pretrained(p/'model',local_files_only=True,trust_remote_code=False,use_fast=False)
model=AutoModelForDepthEstimation.from_pretrained(p/'model',local_files_only=True,trust_remote_code=False,use_safetensors=True).eval()
x=proc(images=img,return_tensors='pt'); t=time.time()
with torch.inference_mode(): raw=model(**x).predicted_depth[0].cpu().numpy().astype('float32')
elapsed=time.time()-t
finite=np.isfinite(raw);lo=float(raw[finite].min());hi=float(raw[finite].max());assert hi>lo
np.save(out/'relative-inverse-depth-model-grid.npy',raw,allow_pickle=False)
gray=np.where(finite,np.clip((raw-lo)/(hi-lo),0,1)*65535,0).round().astype('uint16')
Image.fromarray(gray).save(out/'relative-inverse-depth-gray16-model-grid.png')
res=torch.nn.functional.interpolate(torch.from_numpy(raw)[None,None],size=(img.height,img.width),mode='bicubic',align_corners=False)[0,0].numpy()
np.save(out/'relative-inverse-depth-resampled-source-grid.npy',res,allow_pickle=False)
Image.fromarray((np.clip((res-lo)/(hi-lo),0,1)*255).round().astype('uint8')).save(out/'relative-inverse-depth-gray8-resampled-source-grid.png')
mask=Image.new('L',img.size);draw=ImageDraw.Draw(mask)
for roi in meta.get('exclusions',[]):
 if roi['shape']=='rectangle':draw.rectangle(roi['points'],fill=roi['class'])
 elif roi['shape']=='polygon':draw.polygon([tuple(pt) for pt in roi['points']],fill=roi['class'])
mask.save(out/'manual-exclusion-classes-source-grid.png')
if 'dark_rgb_max_threshold' in meta:
 dark=(np.asarray(img).max(axis=2)<=int(meta['dark_rgb_max_threshold']))
 Image.fromarray(dark.astype('uint8')*255).save(out/'dark-low-signal-caution-source-grid.png')
Image.new('L',img.size,255).save(out/'confidence-unknown-source-grid.png')
Image.fromarray((~finite).astype('uint8')*255).save(out/'nonfinite-invalid-model-grid.png')
report={'source':{**meta,'path':str(source),'sha256':sha(source),'bytes':source.stat().st_size,'size':list(img.size),'crop':[0,0,img.width,img.height]},'method':{'repo':artifact['repo'],'revision':artifact['revision'],'weights_sha256':sha(p/'model/model.safetensors'),'device':'cpu','dtype':'float32','threads':4,'trust_remote_code':False,'local_files_only':True,'weights_format':'safetensors','versions':{k:md.version(k) for k in ['torch','transformers','safetensors','pillow','numpy']},'input_tensor_shape':list(x['pixel_values'].shape),'raw_shape':list(raw.shape),'processor_config':json.loads((p/'model/preprocessor_config.json').read_text()),'forward_seconds':elapsed},'range':{'min':lo,'max':hi,'nonfinite_count':int((~finite).sum())},'value_definition':'Relative inverse-depth-like prediction. Larger/white generally nearer, smaller/black generally farther. Not metric distance, not luminance conversion. Per-image min/max normalization is not comparable metric distance across views.','normalization':'(raw-min)/(max-min); source-grid display is derived bicubic interpolation align_corners=False, not native-resolution independent depth inference.','mask_definition':{'manual_exclusions':'Conservative incomplete manual ROIs; 0 is unlabelled, NOT valid certification. See source exclusions descriptions.','confidence_unknown':'255 everywhere means no calibrated model confidence, NEVER high confidence.','nonfinite_invalid':'255 indicates nonfinite numeric prediction, 0 merely finite; does not certify geometric validity.','occluded_hidden_regions':'Not observable, no hidden geometry or surface contact inferred as fact.'},'limitations':['Single monocular estimate cannot validate metric geometry, hidden structures, scale, camera calibration, or contact.','Stylized CG, reflective/translucent surfaces, lighting, characters and screen overlays can be wrong.','Manual exclusion masks are incomplete and not segmentation.','This analysis does not replace native multi-view evidence or direct unwarped overlay validation.']}
report['outputs']=[{'path':f.name,'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(out.iterdir()) if f.is_file() and f.name!='report.json']
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'source':source.name,'raw_shape':raw.shape,'range':report['range'],'forward_seconds':elapsed},ensure_ascii=False))
