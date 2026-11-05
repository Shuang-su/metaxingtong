import bpy,pathlib,json,hashlib,struct
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=pathlib.Path(__file__).resolve().parents[1];report=[]
def geo():
 return {o.name:hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)+b''.join(struct.pack('<I',i) for p in o.data.polygons for i in p.vertices)).hexdigest() for o in bpy.data.objects if o.type=='MESH'}
for tag in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/f'models/R04C_{tag}.blend'));before=geo();s=bpy.context.scene;changes=[]
 for name,loc,target in [('CHECK03_left_profile',(-42,-12,9),(0,0,7)),('CHECK04_right_profile',(42,10,8),(0,0,7)),('CHECK07_high_front',(0,-28,34),(0,0,7))]:
  o=bpy.data.objects[name];o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.context.view_layer.update()
 # Bound all retained visible assembly, excluding deliberately cropped floor slab.
 vertices=[o.matrix_world@v.co for o in bpy.data.objects if o.type=='MESH' and not o.name.startswith('STAGE_') for v in o.data.vertices]
 for o in bpy.data.objects:
  if o.type=='CAMERA' and o.name.startswith('CHECK'):
   oldlens=o.data.lens;pts=[world_to_camera_view(s,o,v) for v in vertices];r=max(max(abs(p.x-.5),abs(p.y-.5)) for p in pts)
   if r>.45:o.data.lens*=.45/r
   bpy.context.view_layer.update();pts=[world_to_camera_view(s,o,v) for v in vertices]
   bounds=[min(p.x for p in pts),max(p.x for p in pts),min(p.y for p in pts),max(p.y for p in pts)]
   assert min(bounds[0],bounds[2])>=.049 and max(bounds[1],bounds[3])<=.951
   changes.append({'camera':o.name,'lens_before':oldlens,'lens_final':o.data.lens,'location':list(o.location),'matrix_world':[list(row) for row in o.matrix_world],'assembly_projected_bounds':bounds,'floor_crop_excluded':True})
 assert before==geo()
 s['revision']='R04D camera-only final inspection framing with actual 5% projected assembly margin; R04 source geometry unchanged; SOURCE FAILED'
 bpy.ops.wm.save_as_mainfile(filepath=str(P/f'models/R04D_{tag}.blend'))
 bpy.ops.export_scene.gltf(filepath=str(P/f'models/R04D_{tag}.glb'),export_format='GLB',export_cameras=True,export_lights=True,export_extras=True,export_apply=True)
 report.append({'tag':tag,'geometry_hashes_identical_to_R04C':before,'inspection_changes':changes,'note':'Source02 and both source05 cameras untouched. Stage crop may extend beyond frame by design; all other retained meshes projected inside 5% margin.'})
(P/'qa/R04D-camera-framing-proof.json').write_text(json.dumps(report,indent=2))
