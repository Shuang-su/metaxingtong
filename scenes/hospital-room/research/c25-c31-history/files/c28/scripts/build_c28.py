import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];P=R/'c28';fit=json.load(open(P/'spacing_fit.json'));f=json.load(open(R/'c27/bank1_fit.json'));names=f['target_group'][2:];scale=fit['scale'];anchor=fit['anchor_world_z']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def state():
 d={}
 for o in bpy.data.objects:
  x={'type':o.type,'matrix':[list(r) for r in o.matrix_world],'hide_render':o.hide_render,'hide_viewport':o.hide_viewport}
  if o.type=='MESH':x['vertex_sha256']=hashlib.sha256(str([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest();x['faces_sha256']=hashlib.sha256(str([tuple(p.vertices) for p in o.data.polygons]).encode()).hexdigest()
  if o.type=='CAMERA':x['camera']={k:getattr(o.data,k) for k in ['lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','clip_start','clip_end','type']}
  d[o.name]=x
 return d
audit={}
for kind in ['WHITE','MATERIAL']:
 src=R/'c27'/('hospital_C27_bank1_'+kind+'_CONDITIONAL.blend');bpy.ops.wm.open_mainfile(filepath=str(src));before=state();mods=[]
 for n in names:
  o=bpy.data.objects[n];assert o.type=='MESH' and not o.animation_data
  if o.data.users>1:o.data=o.data.copy()
  m=o.matrix_world.copy();inv=m.inverted();w=[m@v.co for v in o.data.vertices];center=sum(v.z for v in w)/len(w);dz=(scale-1)*(center-anchor)
  for v,q in zip(o.data.vertices,w):q.z+=dz;v.co=inv@q
  o.data.update();o['C28_CHANGE']='Uniform bank1 world-Z center-spacing correction; cross-section unchanged'
  o['C28_UNCERTAINTY']='Visible multi-view spacing supported; unseen top connection and absolute scale unresolved'
  mods.append({'name':n,'center_world_z_before':center,'center_world_z_after':center+dz,'world_z_translation':dz})
 bpy.context.view_layer.update();after=state();changes=[n for n in before if n not in after or before[n]!=after[n]]
 assert set(changes)==set(names);assert all(before[n]==after[n] for n in before if n not in names)
 bpy.context.scene['C28_STATUS']='CONDITIONAL spacing candidate; no camera or chair changes; not accepted'
 path=P/('hospital_C28_bank1_'+kind+'_CONDITIONAL.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));assert state()==after
 audit[kind]={'source':str(src.relative_to(R)),'source_sha256':sha(src),'candidate':path.name,'candidate_sha256':sha(path),'scale':scale,'anchor_world_z':anchor,'changed_objects':changes,'mesh_translations':mods,'unchanged_other_object_count':len(before)-len(names),'reopen_state_equal':True,'before_state':before,'after_state':after}
(P/'build_verification.json').write_text(json.dumps(audit,indent=2));print('C28_READY',len(names),'center translations; minimum slat and all other objects frozen')
