"""Camera-only revision after actual 8-angle contact sheet showed clipping."""
import bpy,pathlib,json,hashlib,struct
P=pathlib.Path(__file__).resolve().parents[1]
report=[]
def geo():
 r={}
 for o in bpy.data.objects:
  if o.type=='MESH':
   data=b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)+b''.join(struct.pack('<I',i) for p in o.data.polygons for i in p.vertices)
   r[o.name]=hashlib.sha256(data).hexdigest()
 return r
for tag in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/f'models/R04_{tag}.blend'));before=geo();src=[];changes=[]
 for o in bpy.data.objects:
  if o.type=='CAMERA':
   if o.name.startswith('CHECK'):
    changes.append({'camera':o.name,'old_lens':o.data.lens,'new_lens':32.0,'matrix_world_unchanged':[list(r) for r in o.matrix_world]});o.data.lens=32
   else:src.append({'camera':o.name,'lens_unchanged':o.data.lens,'matrix_world_unchanged':[list(r) for r in o.matrix_world]})
 assert before==geo()
 bpy.context.scene['revision']='R04C camera-only inspection framing; identical R04 mesh/material/source cameras; source FAILED'
 bpy.ops.wm.save_as_mainfile(filepath=str(P/f'models/R04C_{tag}.blend'))
 bpy.ops.export_scene.gltf(filepath=str(P/f'models/R04C_{tag}.glb'),export_format='GLB',export_cameras=True,export_lights=True,export_extras=True,export_apply=True)
 report.append({'tag':tag,'geometry_hashes_unchanged':True,'mesh_hashes':before,'inspection_camera_changes':changes,'source_cameras_unchanged':src})
(P/'qa/R04C-camera-only-diff.json').write_text(json.dumps(report,indent=2))
