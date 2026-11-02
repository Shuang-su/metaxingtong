"""Local CPU depth evidence. Not reconstruction, metric geometry, or confidence."""
from pathlib import Path
import argparse, hashlib, importlib.metadata as md, json, time
import numpy as np
from PIL import Image, ImageDraw
import torch
from transformers import AutoImageProcessor, AutoModelForDepthEstimation

ap=argparse.ArgumentParser()
ap.add_argument('--config', required=True)
ap.add_argument('--model-dir', required=True)
ap.add_argument('--threads',type=int,default=3)
args=ap.parse_args()
root=Path(__file__).resolve().parents[1]
cfg=json.loads((root/args.config).read_text())
model_dir=Path(args.model_dir).resolve()
source=root/cfg['source']['path']; out=root/cfg['output']; out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)==cfg['source']['sha256']
img=Image.open(source).convert('RGB'); img.load()
torch.set_num_threads(args.threads); torch.set_num_interop_threads(1)
proc=AutoImageProcessor.from_pretrained(model_dir,local_files_only=True,trust_remote_code=False,use_fast=False)
model=AutoModelForDepthEstimation.from_pretrained(model_dir,local_files_only=True,trust_remote_code=False,use_safetensors=True).eval()
x=proc(images=img,return_tensors='pt'); t=time.perf_counter()
with torch.inference_mode(): raw=model(**x).predicted_depth[0].cpu().numpy().astype('float32')
elapsed=time.perf_counter()-t
np.save(out/'relative-inverse-depth-model-grid.npy',raw,allow_pickle=False)
finite=np.isfinite(raw); lo=float(raw[finite].min()); hi=float(raw[finite].max())
norm=np.where(finite,np.clip((raw-lo)/(hi-lo),0,1),0)
Image.fromarray((norm*65535).round().astype('uint16')).save(out/'relative-inverse-depth-gray16-model-grid.png')
res=torch.nn.functional.interpolate(torch.from_numpy(raw)[None,None],size=(img.height,img.width),mode='bicubic',align_corners=False)[0,0].numpy()
Image.fromarray((np.clip((res-lo)/(hi-lo),0,1)*255).round().astype('uint8')).save(out/'relative-inverse-depth-gray8-derived-source-grid.png')
mask=Image.new('L',img.size);d=ImageDraw.Draw(mask)
for item in cfg['mask_regions']:
    getattr(d,item['shape'])(item['coords'],fill=item['value'])
mask.save(out/'manual-exclusion-classes-source-grid.png')
Image.new('L',img.size,255).save(out/'confidence-unknown-source-grid.png')
report={
    'purpose':'Supplemental source relative-depth evidence only; not measured scale or reconstruction acceptance',
    'source':dict(cfg['source'],bytes=source.stat().st_size,dimensions=img.size,effective_crop=[0,0,img.width,img.height]),
    'method':{
        'repo':'depth-anything/Depth-Anything-V2-Small-hf','revision':'5426e4f0f36572d16453bbda7a8389317b1bef99',
        'weights_sha256':sha(model_dir/'model.safetensors'),'device':'cpu','threads':args.threads,'dtype':'float32',
        'versions':{p:md.version(p) for p in ['torch','transformers','safetensors','pillow','numpy']},
        'input_tensor_shape':list(x['pixel_values'].shape),'raw_shape':list(raw.shape),
        'processor_config':json.loads((model_dir/'preprocessor_config.json').read_text()),
        'inference_seconds':elapsed,'local_files_only':True,'trust_remote_code':False,
    },
    'values':{'definition':'Relative inverse-depth-like model values; higher conventionally nearer, not metric',
        'min':lo,'max':hi,'nonfinite_count':int((~finite).sum()),
        'normalization':'(raw-min)/(max-min); white=nearer; per-image only; no cross-image absolute comparison',
        'derived_grid':'bicubic align_corners=False source-grid display, clamped after normalization; not full-resolution prediction'},
    'masks':{'classes':cfg['mask_classes'],'regions':cfg['mask_regions'],
        'confidence':'255 everywhere means unknown: model supplies no calibrated confidence',
        'limits':'Conservative hand-drawn ROIs include neighboring material; not exact segmentation; zero is unlabelled NOT validated'},
    'limitations':cfg['limitations'],
}
report['outputs']=[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'dimensions':list(Image.open(p).size) if p.suffix=='.png' else None} for p in sorted(out.iterdir()) if p.is_file() and p.name!='report.json']
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'raw_shape':raw.shape,'input_shape':list(x['pixel_values'].shape),'min':lo,'max':hi,'inference_seconds':elapsed}))
