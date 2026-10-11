from pathlib import Path
from PIL import Image
import json,hashlib,shutil,zipfile
p=Path('classroom_hd_alignment_20261010')
# Preserve initial16 sample images; use64 sample C/D as final render inputs with no material/geometry changes.
for n in ['classroom_4284_wide','classroom_5447_key']:
 f=p/'renders'/f'{n}.png';old=p/'renders'/f'{n}_16samples.png'
 if not old.exists():shutil.copy2(f,old)
 shutil.copy2(p/'renders'/f'{n}_64samples.png',f)
exec((p/'scripts/make_overlays.py').read_text());exec((p/'scripts/make_diagnostics.py').read_text())
shutil.copy2(p/'renders/classroom_4284_wide_64samples_denoised.png',p/'主视角_正常材质_广角.png');shutil.copy2(p/'renders/classroom_5447_key_64samples_denoised.png',p/'主视角_正常材质_D斜角.png')
verification=json.load(open(p/'qa/saved_main_verification.json'));assert verification['geometry_material_visibility_exact_match'] and verification['all_existing_cameras_exactly_preserved'];source_hash=hashlib.sha256(Path('classroom_fullroom/Classroom_FullRoom_REVIEW.blend').read_bytes()).hexdigest();assert source_hash=='77be8336b43f7cf6c413369c6bef2bd46b5e8508f1958b0fb4d8a172e457c908'
summary={'status':'HD_EVIDENCE_CHAIN_GEOMETRY_UNCHANGED_D_AUXILIARY_UNLINKED_PRIMARY_RESIDUALS','source_count':5,'new_independent_camera_count_not_claimed':True,'student_desks_total':20,'D_visible_student_desks':12,'D_source_visible_units_lower_bound':14,'D_zero_visible_desks_all_fully_outside_left':True,'accepted_geometry_change':False,'rejected_trial':{'visible_count':14,'new_sliver_pixels':[110,477],'C_corner_drift_px':[41.06545,26.24568]},'same_source_BV_only':True,'capture_kind':'1080 decoded viewport screenshots;1180x664 crops;not native1080 export','main_blend':'Classroom_HD_Evidence_REVIEW.blend','main_review_images':['主视角_正常材质_广角.png','主视角_正常材质_D斜角.png'],'overlay_sheet':'五张高清补帧_直接叠图总览.jpg','D_evidence_sheet':'D数量冲突_来源与投影ID.jpg','report':'高清验证说明.md','source_main_sha256':source_hash,'files_sha256':{str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file() and f.suffix in ['.png','.jpg','.blend'] and '__pycache__' not in str(f)}}
(p/'阶段结果.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in summary.items() if k!='files_sha256'},ensure_ascii=False,indent=2))
