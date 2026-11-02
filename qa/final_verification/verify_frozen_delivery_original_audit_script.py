from pathlib import Path
from PIL import Image
import numpy as np,subprocess,hashlib,json
R=Path(__file__).resolve().parents[1]/'camp-remake-20261102';O=Path(__file__).resolve().parent;head='82694151a2af4f3761325ab34296bd00464322ae';sha=lambda b:hashlib.sha256(b).hexdigest();assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==head
names=subprocess.check_output(['git','ls-tree','-r','--name-only','-z',head],cwd=R).decode().rstrip('\0').split('\0');files=[]
for n in names:
 git=subprocess.check_output(['git','show',f'{head}:{n}'],cwd=R);local=(R/n).read_bytes();files.append({'path':n,'bytes':len(git),'sha256':sha(git),'working_equal':local==git})
old=subprocess.check_output(['git','ls-tree','-r','--name-only','-z','6589cbbc391f1a4aba04bc570df87a82751d3ab8'],cwd=R).decode().rstrip('\0').split('\0');history=subprocess.check_output(['git','log','--format=%H %s',head],cwd=R,text=True).splitlines();q={'scope':'ALL tracked files at frozen HEAD, not last-commit subset','head':head,'tracked_count':len(names),'all_bytes_equal':all(x['working_equal'] for x in files),'C05_tracked_count':len(old),'C05_paths_missing_at_final':sorted(set(old)-set(names)),'history_commits':history,'files':files,'report_location':'external audit only; frozen model repo HEAD unmodified'};(O/'all_249_git_object_readback.json').write_text(json.dumps(q,ensure_ascii=False,indent=2))
frames={1:'1541.38851',2:'1570.44087',3:'1566.095177'};overlays=[]
def check(src,ren,out,role):
 a=np.array(src.convert('RGB'),dtype=np.uint16);b=np.array(Image.open(ren).convert('RGB'),dtype=np.uint16);z=np.array(Image.open(out).convert('RGB'),dtype=np.uint16);expected=(a+b)//2;delta=np.abs(expected.astype(np.int16)-z.astype(np.int16));overlays.append({'path':str(out.relative_to(R)),'formula':'floor((sourceRGB_uint16 + renderRGB_uint16)/2), independently numpy recomputed','source_transform':role,'dimensions':[a.shape[1],a.shape[0]],'max_channel_error':int(delta.max()),'different_pixels':int(np.any(delta!=0,axis=2).sum()),'render_sha256':sha(ren.read_bytes()),'overlay_sha256':sha(out.read_bytes())})
for version in ['C05','C06']:
 for i,tm in frames.items():
  src=Image.open(R/f'sources/BV169Y96rEo1_P1_{tm}.png');prefix=f'{version}_SOURCE{i}' if i<3 else f'{version}_SOURCE3_F2500_NOT_BLIND'
  for mode in ['materials','white']:check(src,R/f'renders/{prefix}_{mode}_1920.png',R/f'renders/{prefix}_{mode}_direct50_1920.png','native unchanged full source 1920x1080')
 src=Image.open(R/'sources/BV169Y96rEo1_P1_1566.095177.png').convert('RGB').resize((960,540))
 for f in [1800,2500,3200]:check(src,R/f'renders/{version}_SOURCE3_F{f}_NOT_BLIND_960.png',R/f'renders/{version}_SOURCE3_F{f}_NOT_BLIND_direct50_960.png','PIL resize source to960x540, explicit derived diagnostic')
boxes=json.load(open(R/'qa/roll_c06/crop_coordinates.json'))['native_crop_boxes']
for i in [1,2]:
 src=Image.open(R/f'sources/BV169Y96rEo1_P1_{frames[i]}.png').crop(boxes[str(i)]);check(src,R/f'renders/C06_SOURCE{i}_roll_materials_native_crop.png',R/f'renders/C06_SOURCE{i}_roll_direct50_native_crop.png','native-coordinate crop, no resize, box='+str(boxes[str(i)]))
(O/'all_20_direct50_pixel_verification.json').write_text(json.dumps({'scope':'C05+finalC06 full native material/white, all third focal low diagnostics, C06 roll native crops','count':len(overlays),'all_exact':all(x['different_pixels']==0 for x in overlays),'does_not_validate':'source geometry/camera/acceptance; only pixel formula and stated transforms','results':overlays},indent=2));print('all tracked',len(files),q['all_bytes_equal'],'C05 missing',q['C05_paths_missing_at_final'],'overlays',len(overlays),all(x['different_pixels']==0 for x in overlays))
