import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];Q=R/'qa/front-camera-diagnostic';bpy.ops.wm.open_mainfile(filepath=str(R/'models/ferris_remake_R05_material.blend'));s=bpy.context.scene;c=bpy.data.objects['SRC_front'];g=json.loads((Q/'actual-mesh-edges.json').read_text());j=json.loads((Q/'fit-report.json').read_text());rows=[]
for row in j['selected_training']['rows']:
 edge=g['training_edges_world'][row['edge']]
 for p,expected in zip(edge,row['projected_model_finite_edge']):
  xy=world_to_camera_view(s,c,Vector(p));actual=[xy.x*1920,(1-xy.y)*1080];rows.append({'edge':row['edge'],'actual_Blender_px':actual,'optimizer_px':expected,'delta_px':math.dist(actual,expected)})
changes=json.loads((Q/'R05-change-verification.json').read_text());same=changes[0]['mesh_hashes']==changes[1]['mesh_hashes'];assert same;maxerr=max(r['delta_px'] for r in rows);assert maxerr<.01
(Q/'R05-actual-projection-check.json').write_text(json.dumps({'maximum_Blender_vs_optimizer_px':maxerr,'points':rows,'material_white_geometry_exact':same,'R04_geometry_faces_worldvertices_equal':all(x['R04_geometry_worldvertex_face_hash_equal'] for x in changes),'other_cameras_equal':all(x['all_other_cameras_equal'] for x in changes),'camera_scope':'only SRC_front updated; no geometry, material, light or other camera changes'},indent=2));print(maxerr,same)
