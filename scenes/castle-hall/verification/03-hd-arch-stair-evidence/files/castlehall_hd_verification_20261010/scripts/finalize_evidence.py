from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,zipfile
R=Path(__file__).resolve().parents[1]
for p in (R/'references').glob('*.jpg'):Image.open(p).crop((0,27,1180,691)).save(p.with_name(p.stem+'_core.png'))
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
files=[R/'references/hall_A_2712_paused_core.png',R/'renders/baseline_A_1180_raw.png',R/'qa/overlay50_baseline_A_HD2712.png'];labels=['HD SOURCE 2712.991552 | original crop','UNCHANGED BASELINE | old A camera (approx.)','50% DIRECT OVERLAY | no warp | residuals remain']
im=Image.new('RGB',(1180,704*3),(20,25,30));d=ImageDraw.Draw(im)
for i,(p,l) in enumerate(zip(files,labels)):
 im.paste(Image.open(p).convert('RGB'),(0,i*704+40));d.text((12,i*704+8),l,font=font,fill='white')
im.save(R/'qa/HD_A_source_baseline_overlay.jpg',quality=93)
files=[R/'references/hall_right_arch_4528_paused_core.png',R/'references/hall_right_arch_4529_natural_ui_clear_core.png'];labels=['4528.936245 | right arch + ascending steps | player bar retained','4529.796014 | UI cleared naturally | paused / ready4']
im=Image.new('RGB',(1180,1408),(20,25,30));d=ImageDraw.Draw(im)
for i,(p,l) in enumerate(zip(files,labels)):
 im.paste(Image.open(p).convert('RGB'),(0,i*704+40));d.text((12,i*704+8),l,font=font,fill='white')
im.save(R/'qa/HD_right_arch_stair_evidence.jpg',quality=94)
ledger={'scene_id':'castlehall','phase':'20261010_hd_verification_before_shared_geometry_revision','source_url':'https://www.bilibili.com/video/BV1aw411T7ws/','broadcast_date':'2023-11-10','broadcast_title':'回城堡咯！','browser':'dot cloud browser tab 2, not user computer','decoded_pixels':[1920,1080],'viewport_pixels':[1180,757],'core_crop_xyxy':[0,27,1180,691],'core_pixels':[1180,664],'native_video_export':False,'source_image_manipulation':'Rectangular crop only; no warp, inpainting, resizing or screenshot-texture geometry. Contact sheets may scale display thumbnails only.','frames':[],'motion':{'metadata':'references/motion_right_4529/metadata.json','sample_intervals_seconds':[[4530.473704,4535.494112],[4547.491698,4549.782618]],'gap_seconds':[4535.494112,4547.491698],'screenshots':90,'all_native_frames':False,'ready4_both_checks':69,'warning':'Repeated 4549.782618 ready2 buffering frames do not count as new views; sampled camera movement is not a solved extrinsic baseline.'},'ui_exclusion_mask':'qa/masks/UI_only_validity_mask.png','ui_exclusion_regions_core_xyxy':[[0,626,1180,664],[1068,535,1159,611]],'ui_mask_scope':'Diagnostic validity mask only. Original images/overlays remain unmodified. This is not a complete character-occlusion mask.','baseline_blend_sha':'b04ebc7091ce5bc6a2c8419a634effc5e6999f68a8db68701a832e69259a174e','model_changes':'None in this verification phase','structural_finding':'Right wall arched opening and visible ascending steps are absent from baseline; shared white-model revision required. Endpoint and onward connection unknown.','acceptance':'Not source accepted. Baseline residuals remain; technical mesh/GLB parity does not mean source-fit pass.'}
for p in sorted((R/'references').glob('*.json')):
 x=json.loads(p.read_text())
 if 'before' not in x:continue
 a,b=x['before'],x['after'];fname=p.stem
 ledger['frames'].append({'id':fname,'metadata':str(p.relative_to(R)),'screenshot':str(p.with_suffix('.jpg').relative_to(R)) if p.with_suffix('.jpg').exists() else 'in original source_supplements/20261010_transition','core':str(p.with_name(fname+'_core.png').relative_to(R)),'time_before':a['time'],'time_after':b['time'],'paused_both':a['paused'] and b['paused'],'ready_before':a['ready'],'ready_after':b['ready'],'same_time':a['time']==b['time'],'note':'Natural UI clear verified' if 'natural_ui_clear' in fname else ('Dynamic cart/character, playing screenshot; not empty static room reference' if 'cart' in fname else 'Player UI retained if visible; filename clean alone does not assert UI absence')})
(R/'source_ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2))
files=[p for p in sorted(R.rglob('*')) if p.is_file() and p.name not in ['SHA256.json'] and p.suffix!='.zip']
(R/'SHA256.json').write_text(json.dumps([{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],ensure_ascii=False,indent=2))
D=R/'delivery';D.mkdir(exist_ok=True)
groups={'CastleHall_HD_Verification_Evidence_20261010.zip':[p for p in files if 'motion_right_4529' not in str(p)]+[R/'SHA256.json'], 'CastleHall_HD_Motion_Evidence_20261010.zip':[p for p in files if 'motion_right_4529' in str(p)]+[R/'source_ledger.json',R/'SHA256.json']}
for name,paths in groups.items():
 p=D/name
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for f in paths:z.write(f,str(f.relative_to(R)))
 assert p.stat().st_size<18000000,(p,p.stat().st_size)
 print(p,p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest())
