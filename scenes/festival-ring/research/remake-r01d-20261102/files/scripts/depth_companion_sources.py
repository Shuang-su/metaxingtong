from pathlib import Path
import hashlib,json,time,importlib.metadata as md
import numpy as np
from PIL import Image,ImageDraw
import torch
from transformers import AutoImageProcessor,AutoModelForDepthEstimation
r=Path(__file__).resolve().parents[1];modelpath=r.parent/'depth-validation-20261102/model';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(modelpath/'model.safetensors')=='3152477ce0d8d6978d76b995120de97cb5b928701fd0f817769f59e249a16b70'
torch.set_num_threads(2);torch.set_num_interop_threads(1)
proc=AutoImageProcessor.from_pretrained(modelpath,local_files_only=True,trust_remote_code=False,use_fast=False);model=AutoModelForDepthEstimation.from_pretrained(modelpath,local_files_only=True,trust_remote_code=False,use_safetensors=True).eval()
refs=[('front','BV15e4deGE1R_144.009018_1080high.png',144.009018,'93b76e3057321c3f9c2aab45d2e1088b387a72e22240b061ce7b0a76d156ad69'),('oblique','BV15e4deGE1R_60.010322_1080high.png',60.010322,'98a0817234b4486f4cb33bcd0108fb1e666e936515759e8aeec9d90f55f37427')]
for label,file,t,expected in refs:
 sp=r/'sources'/file;assert sha(sp)==expected;im=Image.open(sp).convert('RGB');out=r/'qa'/('depth-'+label);out.mkdir(exist_ok=True);x=proc(images=im,return_tensors='pt');start=time.time()
 with torch.inference_mode():raw=model(**x).predicted_depth[0].cpu().numpy().astype('float32')
 elapsed=time.time()-start;finite=np.isfinite(raw);lo=float(raw[finite].min());hi=float(raw[finite].max());np.save(out/'relative-inverse-depth-model-grid.npy',raw,allow_pickle=False);Image.fromarray(np.round(np.clip((raw-lo)/(hi-lo),0,1)*65535).astype('uint16')).save(out/'relative-inverse-depth-gray16-model-grid.png');up=torch.nn.functional.interpolate(torch.from_numpy(raw)[None,None],size=(im.height,im.width),mode='bicubic',align_corners=False)[0,0].numpy();Image.fromarray(np.round(np.clip((up-lo)/(hi-lo),0,1)*255).astype('uint8')).save(out/'relative-inverse-depth-gray8-resampled-display.png')
 mask=Image.new('L',im.size);d=ImageDraw.Draw(mask)
 if label=='front':
  d.rectangle((0,885,1920,1080),fill=4);d.rectangle((735,815,1195,1040),fill=1);d.rectangle((1145,975,1919,1079),fill=2);d.rectangle((730,0,1175,105),fill=2)
 else:
  d.rectangle((0,745,1920,1080),fill=4);d.rectangle((425,350,1460,900),fill=1)
 mask.save(out/'manual-exclusion-classes.png');Image.new('L',im.size,255).save(out/'confidence-unknown.png')
 report={'source':{'path':str(sp.relative_to(r)),'BV':'BV15e4deGE1R','time_seconds':t,'dimensions':im.size,'crop':[0,0,im.width,im.height],'bytes':sp.stat().st_size,'sha256':expected,'quality':'actual1080high,4Ktarget buffering per companion-manifest; not old identical frame'},'model':{'repo':'depth-anything/Depth-Anything-V2-Small-hf','revision':'5426e4f0f36572d16453bbda7a8389317b1bef99','weights_sha256':sha(modelpath/'model.safetensors'),'license':'Apache-2.0','versions':{n:md.version(n) for n in ['torch','transformers','safetensors','numpy','pillow']},'device':'CPU','threads':2,'input_tensor':list(x['pixel_values'].shape),'output_grid':list(raw.shape),'forward_seconds':elapsed,'dtype':'float32','processor_config':json.loads((modelpath/'preprocessor_config.json').read_text()),'trust_remote_code':False,'safetensors_only':True,'local_files_only':True},'range':{'min':lo,'max':hi,'nonfinite':int((~finite).sum())},'definition':'Relative inverse-depth-like learned estimate. Larger/whiter generally near; minmax per image. No absolute scale/meters or unique camera. NOT luminance grayscale.','display':'Bicubic align_corners=False upscale from model grid to source size only for display; clipped minmax, not native high-res depth; raw high-res float deliberately not duplicated','masks':{'0':'unlabelled not certified valid','1':'conservative dynamic character-group rectangle includes background','2':'screen subtitle/event title uncertain region','4':'reflective stage/fish/lighting lower region; incomplete conservative exclusion','confidence-unknown':'255 entire image means no calibrated confidence provided, NOT high confidence','unmasked_issues':'light beams/sparks throughout, transparent/reflective pieces, thin rods, star identity/state unknown; no exhaustive segmentation'},'limits':'All three are training images from same2024event, not independent replay; source reconstruction and geometry unaccepted'}
 report['outputs']=[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(out.iterdir()) if p.is_file()];(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(label,raw.shape,lo,hi,elapsed,flush=True)
