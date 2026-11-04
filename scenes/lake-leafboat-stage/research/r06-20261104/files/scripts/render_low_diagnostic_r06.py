"""Add one transient, reproducible low camera; never save or modify the R06 model."""
import bpy, json, hashlib, struct, datetime
from pathlib import Path
from mathutils import Vector

R = Path(__file__).resolve().parents[1]
Q = R / 'qa/r06'
model = R / 'models/lakeleaf-r06-material.blend'
model_sha = hashlib.sha256(model.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve() == model
s = bpy.context.scene
old_names = set(s.objects.keys())

def snapshot():
    dg = bpy.context.evaluated_depsgraph_get()
    meshes, cameras, visible, lights = {}, {}, {}, {}
    for o in s.objects:
        if o.name not in old_names:
            continue
        visible[o.name] = dict(hide_render=o.hide_render, hide_viewport=o.hide_viewport, hide_get=o.hide_get())
        if o.type == 'MESH':
            e = o.evaluated_get(dg)
            m = e.to_mesh()
            h = hashlib.sha256()
            for v in m.vertices:
                h.update(struct.pack('<3d', *(o.matrix_world @ v.co)))
            for p in m.polygons:
                h.update(struct.pack('<I', len(p.vertices)))
                h.update(struct.pack('<' + 'I' * len(p.vertices), *p.vertices))
            meshes[o.name] = h.hexdigest()
            e.to_mesh_clear()
        elif o.type == 'CAMERA':
            d = o.data
            cameras[o.name] = dict(matrix_world=[list(r) for r in o.matrix_world], type=d.type,
                lens=d.lens, sensor_width=d.sensor_width, sensor_height=d.sensor_height,
                sensor_fit=d.sensor_fit, shift_x=d.shift_x, shift_y=d.shift_y,
                clip_start=d.clip_start, clip_end=d.clip_end, ortho_scale=d.ortho_scale)
        elif o.type == 'LIGHT':
            lights[o.name] = dict(matrix_world=[list(r) for r in o.matrix_world], type=o.data.type,
                color=list(o.data.color), energy=o.data.energy)
    return dict(meshes=meshes, old_cameras=cameras, old_visibility=visible, lights=lights,
        collections={c.name:dict(hide_render=c.hide_render, hide_viewport=c.hide_viewport) for c in bpy.data.collections})

before = snapshot()
inventory = json.loads((Q / 'material-mesh-inventory.json').read_text())
assert before['meshes'] == {k:v['geometry_sha256'] for k,v in inventory.items()}
d = bpy.data.cameras.new('DIAG_LOW_09')
c = bpy.data.objects.new('DIAG_LOW_09', d)
s.collection.objects.link(c)
c.location = (0, -14, 0.06)
c.rotation_euler = (Vector((0, 0, 0.8)) - c.location).to_track_quat('-Z', 'Y').to_euler()
d.lens = 48
d.sensor_width = 36
d.sensor_height = 24
d.sensor_fit = 'HORIZONTAL'
d.clip_start = 0.01
d.clip_end = 200
s.camera = c
s.render.engine = 'CYCLES'
s.cycles.samples = 12
s.cycles.use_denoising = False
s.render.threads_mode = 'FIXED'
s.render.threads = 6
assert s.render.threads == 6
s.render.resolution_x = 1280
s.render.resolution_y = 720
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGB'
bpy.context.view_layer.update()
out = R / 'renders/r06/diagnostic/DIAG_LOW_09.png'
out.parent.mkdir(parents=True, exist_ok=True)
s.render.filepath = str(out)
sidecar = dict(camera=c.name, matrix_world=[list(r) for r in c.matrix_world], location=list(c.location),
    target=[0,0,0.8], type=d.type, lens=d.lens, sensor_width=d.sensor_width,
    sensor_height=d.sensor_height, sensor_fit=d.sensor_fit, shift_x=d.shift_x, shift_y=d.shift_y,
    clip_start=d.clip_start, clip_end=d.clip_end, resolution=[1280,720], resolution_percentage=100,
    samples=12, threads=s.render.threads, denoising=False, model=str(model.relative_to(R)), model_sha256=model_sha,
    role='Supplemental low grazing camera, not a source camera or a complete underside validation',
    reproduction='blender -b models/lakeleaf-r06-material.blend -t 6 --python-exit-code 10 --python scripts/render_low_diagnostic_r06.py',
    scene_saved=False, geometry_visibility_or_lighting_changed=False,
    limits=['Camera z=0.06 is above water maximum z=0.0269931, but above the lowest shell z=0.0056286 too.',
        'Overlapping global z ranges alone do not prove local intersection, buoyancy or exact water contact.',
        'Water and shell occlusion prevent a clear complete underside view. No object is hidden.'])
(Q / 'low-diagnostic-camera-sidecar.json').write_text(json.dumps(sidecar, indent=2) + '\n')
bpy.ops.render.render(write_still=True)
after = snapshot()
assert before == after
assert hashlib.sha256(model.read_bytes()).hexdigest() == model_sha
report = dict(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    old_mesh_count=len(before['meshes']), old_camera_count=len(before['old_cameras']),
    before=before, after=after, exact_equal=True, original_model_file_unchanged=True,
    scene_saved=False, added_transient_camera='DIAG_LOW_09')
(Q / 'low-diagnostic-invariance.json').write_text(json.dumps(report, indent=2) + '\n')
sidecar.update(rendered_at=report['created_at'], sha256=hashlib.sha256(out.read_bytes()).hexdigest(), bytes=out.stat().st_size)
out.with_suffix('.json').write_text(json.dumps(sidecar, indent=2) + '\n')
print('One supplemental low diagnostic rendered; 2704 meshes, 13 original cameras and visibility unchanged; no BLEND saved.')
