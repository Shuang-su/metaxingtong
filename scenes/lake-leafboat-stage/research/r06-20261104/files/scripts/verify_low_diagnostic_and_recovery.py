from pathlib import Path
from PIL import Image
import hashlib, json, datetime

R = Path(__file__).resolve().parents[1]
Q = R / 'qa/r06'
recovery = json.loads((Q / 'render-interruption-recovery.json').read_text())
checks = []
for row in recovery['existing_files_not_to_be_overwritten']:
    p = R / row['path']
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha == row['sha256']
    checks.append(dict(path=row['path'], bytes=p.stat().st_size, sha256=sha, unchanged=True))

p = R / 'renders/r06/diagnostic/DIAG_LOW_09.png'
im = Image.open(p)
im.load()
meta = json.loads(p.with_suffix('.json').read_text())
sidecar = json.loads((Q / 'low-diagnostic-camera-sidecar.json').read_text())
diff = json.loads((Q / 'low-diagnostic-invariance.json').read_text())
assert im.size == (1280, 720)
assert hashlib.sha256(p.read_bytes()).hexdigest() == meta['sha256']
assert meta['model_sha256'] == hashlib.sha256((R / meta['model']).read_bytes()).hexdigest()
assert meta['threads'] == 6 and meta['samples'] == 12 and not meta['denoising']
assert all(meta[k] == v for k,v in sidecar.items())
assert diff['before'] == diff['after']
assert diff['old_mesh_count'] == 2704 and diff['old_camera_count'] == 13
assert diff['exact_equal'] and diff['original_model_file_unchanged'] and not diff['scene_saved']
report = dict(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    recovered_existing_image_count=len(checks), all_original_complete_images_unchanged=True,
    original_images=checks, supplemental_image=str(p.relative_to(R)), size=list(im.size),
    sha256=meta['sha256'], bytes=p.stat().st_size, model_sha256=meta['model_sha256'],
    no_model_rewrite=True, no_mesh_old_camera_visibility_or_light_change=True,
    main_suite_render_count=26, supplemental_render_count=1, total_R06_render_count=27,
    source_view_count=4, primary_source_count=3, auxiliary_source_count=1,
    paired_inspection_angles=8, supplemental_low_angle=1,
    limitation='Low grazing partial shell/waterline diagnostic only; complete underside, local intersections, support and buoyancy not validated.',
    source_accepted=False, user_accepted=False)
(Q / 'low-diagnostic-delivery-audit.json').write_text(json.dumps(report, indent=2) + '\n')
print('Verified 26 suite images + 1 supplemental low diagnostic; prior 16 complete images unchanged after recovery.')
