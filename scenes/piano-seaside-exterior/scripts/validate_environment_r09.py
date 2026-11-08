"""Read saved R08/R09 files; verify freeze, lamp openings/supports, native bytes."""
import bpy,json,hashlib,array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];Q=R/'qa/r09'
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def geometry(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();v=array.array('f',[0])*(len(m.vertices)*3);ix=array.array('i',[0])*len(m.loops);m.vertices.foreach_get('co',v);m.loops.foreach_get('vertex_index',ix)
 d={'v':hashlib.sha256(v.tobytes()).hexdigest(),'ix':hashlib.sha256(ix.tobytes()).hexdigest(),'faces':[(p.loop_start,p.loop_total,p.use_smooth) for p in m.polygons],'matrix':[list(v) for v in o.matrix_world]};ev.to_mesh_clear();return digest(d)
def material(m):
 inputs=[]
 for n in m.node_tree.nodes:
  a={}
  for s in n.inputs:
   if not hasattr(s,'default_value'):continue
   v=s.default_value
   try:v=list(v) if not isinstance(v,str) else v
   except TypeError:pass
   a[s.identifier]=v
  inputs.append({'name':n.name,'type':n.bl_idname,'inputs':a,'image_sha256':hashlib.sha256(n.image.packed_file.data).hexdigest() if hasattr(n,'image') and n.image and n.image.packed_file else None})
 return digest({'diffuse':list(m.diffuse_color),'nodes':inputs,'links':[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links]})
def read(stage):
 bpy.ops.wm.open_mainfile(filepath=str(R/f'models/{stage}/piano_seaside_material.blend'));objs={};deck={};cams={}
 for o in bpy.context.scene.objects:
  if o.type=='MESH':
   if o.get('evidence_id')=='D01_deck':deck[o.name]=geometry(o)
   if o.get('evidence_id') in ['D01_deck','L01_lantern','L02_lantern'] or o.name in ['S01 local sand patch','E01 water environment']:continue
   objs[o.name]={'geometry':geometry(o),'materials':[(m.name,material(m)) for m in o.data.materials if m]}
  if o.type=='CAMERA':cams[o.name]={'matrix':[list(v) for v in o.matrix_world],'lens':o.data.lens,'shift':[o.data.shift_x,o.data.shift_y],'clip':[o.data.clip_start,o.data.clip_end],'sensor':[o.data.sensor_width,o.data.sensor_height],'type':o.data.type}
 return {'frozen':objs,'deck':deck,'cameras':cams}
a=read('r08');b=read('r09');assert a==b,'frozen mismatch in actual reopened files'
lamps=[]
for id,(x,y,z),size in [('L01_lantern',(-.92,1.22,0),.25),('L02_lantern',(7.2,-5.5,-.08),.27)]:
 o=bpy.data.objects[id+' open thin paper shell'];h=size*1.55;tests=[]
 for k,(cx,cz) in enumerate([(-size*.16,z+.014+h*.74),(size*.19,z+.014+h*.22)]):
  hit,p,n,i=o.ray_cast(Vector((x+cx,y-.5,cz)),Vector((0,1,0)))
  tests.append({'star':k+1,'ray_from_front_hits_far_inner_wall':hit and p.y>y,'hit_position':list(p) if hit else None})
 hit,p,n,i=o.ray_cast(Vector((x,y,z+1)),Vector((0,0,-1)))
 opened=hit and abs(p.z-(z+.0172))<1e-4
 tests.append({'open_top_ray_reaches_inner_floor':opened,'hit_z':p.z if hit else None})
 support=[]
 for target in [a for a in bpy.context.scene.objects if a.type=='MESH' and (a.get('evidence_id')=='D01_deck' or a.name=='S01 local sand patch')]:
  inv=target.matrix_world.inverted();hit,p,n,idx=target.ray_cast(inv@Vector((x,y,z+.2)),inv.to_3x3()@Vector((0,0,-1)))
  if hit:support.append(float((target.matrix_world@p).z))
 nearest=max(support) if support else None
 assert all(t.get('ray_from_front_hits_far_inner_wall',t.get('open_top_ray_reaches_inner_floor',False)) for t in tests),(id,tests)
 lamps.append({'id':id,'anchor_unchanged':[x,y,z],'component_count':len([a for a in bpy.context.scene.objects if a.type=='MESH' and a.get('evidence_id')==id]),'tests':tests,'support_z':nearest,'support_gap':None if nearest is None else z-nearest,'support_contact_within_0_005':nearest is not None and abs(z-nearest)<.005})
manifest=json.loads((R/'sources/source-manifest.json').read_text());src=[]
for p in (R/'sources/native').glob('*.png'):
 data=p.read_bytes();src.append({'path':str(p.relative_to(R)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
report={'saved_files_reopened':True,'frozen_non_environment_objects':len(a['frozen']),'frozen_geometry_assigned_material_nodes_and_packed_images_identical':a['frozen']==b['frozen'],'frozen_hash':digest(a['frozen']),'all_camera_count':len(a['cameras']),'all_cameras_identical':a['cameras']==b['cameras'],'camera_hash':digest(a['cameras']),'deck_mesh_and_transforms_identical':a['deck']==b['deck'],'deck_count':len(a['deck']),'lamp_count':len(lamps),'lamps':lamps,'source_native_bytes_read_again':src,'limitations':['Hole and support probes sample modeled candidate, not source accuracy.','Hidden rear paper panels and emissive interior approximation inferred.','Two retained instance anchors are not a verified global lamp inventory.','Shared water/shore/HDR are authored approximations. No source or user acceptance.']}
(Q/'saved-environment-checks.json').write_text(json.dumps(report,indent=2)+'\n');print('R09_SAVED_FREEZE_AND_OPENINGS_PASS',len(a['frozen']),len(a['cameras']))
