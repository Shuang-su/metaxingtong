from pathlib import Path
import shutil,hashlib,json,datetime
R=Path(__file__).resolve().parents[1];old=R.parent/'castlehall_hd_verification_20261010'
for stem in ['hall_right_arch_4528_paused','hall_right_arch_4529_natural_ui_clear','hall_B_4509_paused']:
 for suf in ['.jpg','.json','_core.png']:shutil.copy2(old/'references'/(stem+suf),R/'inputs'/(stem+suf))
shutil.copy2(old/'source_ledger.json',R/'inputs/source_ledger_previous_evidence.json')
shutil.copy2(old/'shared_white_model_plan.md',R/'inputs/shared_white_model_plan.md')
files=list((R/'inputs').glob('*'))+[R.parent/'castle_hall_fullroom/models/Xingtong_Castle_Hall_FullRoom.blend']
files += [R/'qa'/x for x in ['source_camera_fits.json','planar_camera_fit_4528.json','static_wall_patch_matches.json','holdout_camera_4527.json','holdout_camera_4509.json']]
d={'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Freeze before final held-out renders; prior heldout images used only for camera calibration against unchanged wall or columns, excluded from aperture/tread geometry fitting.','files':[{'path':str(p.relative_to(R)) if p.is_relative_to(R) else str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files if p.is_file()]}
(R/'inputs_frozen_sha256.json').write_text(json.dumps(d,indent=2))
models={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (R/'models').iterdir() if p.suffix in ['.blend','.glb']}
(R/'models_frozen_sha256.json').write_text(json.dumps(models,indent=2))
print(json.dumps(models,indent=2))
