import bpy,json,os
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[1];jobs=json.loads(os.environ.get('R10_JOBS','[["BASE","FRONT"],["BASE","RIGHT"]]'));coords={'FRONT':((-3.35,-5,3.74),(-3.35,0,3.65)),'RIGHT':((-.55,-5,3.95),(-3.35,0,3.65))}
for variant,view in jobs:
 path='/workspace/shared/arcade-header-local-20261030/models/arcade_header_R09b_material.blend' if variant=='BEFORE' else str(D/'models'/('arcade_partial_white_R10.blend' if variant=='WHITE' else 'arcade_partial_material_R10.blend'))
 bpy.ops.wm.open_mainfile(filepath=path);s=bpy.context.scene
 if variant in ['STRESS_A','STRESS_B']:
  node=bpy.data.materials['R10 M01 CONDITIONAL source poster partial - NOT calibrated'].node_tree.nodes['DERIVED_POSTER_ATLAS'];node.image=bpy.data.images.load(str(D/f'textures/DERIVED_EXISTING_UV_ATLAS_{variant}.png'))
 d=bpy.data.cameras.new('R10 temporary inspection '+view);d.lens=55;d.sensor_width=36;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);loc,target=coords[view];o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.resolution_x=960;s.render.resolution_y=720;s.render.resolution_percentage=int(os.environ.get('R10_PERCENT','75'));s.render.engine='CYCLES';s.cycles.samples=int(os.environ.get('R10_SAMPLES','12'));s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(D/f'renders/{os.environ.get("R10_PREFIX","preview")}_{variant}_{view}.png');bpy.ops.render.render(write_still=True)
(D/'qa/inspection_camera_parameters.json').write_text(json.dumps({'cameras':coords,'lens_mm':55,'sensor_width':36,'saved_to_production_models':False,'scope':'temporary fixed inspection cameras, before/after same; NOT calibrated source camera','RIGHT_reason':'left-shift of old left-oblique camera would fall beyond existing left wall; use right-side inspection without hiding or moving wall'},indent=2))
