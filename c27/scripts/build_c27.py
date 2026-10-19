import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];P=R/'c27';fit=json.loads((P/'bank1_fit.json').read_text());names=fit['target_group'];nremove=fit['selected_H_G_only']['removed_bottom_count'];trim=fit['selected_H_G_only']['right_trim_scene_units']
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
for kind,src in [('WHITE',R/'c26/hospital_C26_structure_controls_CONDITIONAL.blend'),('MATERIAL',R/'v2b/hospital_C25_structural_volume_CONDITIONAL.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(src));before=state();mods=[]
 for i,n in enumerate(names):
  o=bpy.data.objects[n]
  if i<nremove:
   bpy.data.objects.remove(o,do_unlink=True);continue
  assert o.type=='MESH' and not o.animation_data,'Unexpected animation'
  if o.data.users>1:o.data=o.data.copy()
  m=o.matrix_world.copy();inv=m.inverted();w=[m@v.co for v in o.data.vertices];lo=min(v.x for v in w);hi=max(v.x for v in w)
  for v,q in zip(o.data.vertices,w):q.x=lo+(q.x-lo)*(hi+trim-lo)/(hi-lo);v.co=inv@q
  o.data.update();o['C27_CHANGE']='Bank1 right endpoint trimmed from H/G lowest-slat tip evidence; remaining spacing and left endpoints preserved'
  o['C27_UNCERTAINTY']='Local multi-view silhouette improvement only; conditional cameras and absolute scale'
  mods.append({'name':n,'left_world_x_preserved':lo,'right_world_x_before':hi,'right_world_x_after':hi+trim})
 bpy.context.view_layer.update();after=state()
 changes=[n for n in before if n not in after or before[n]!=after[n]]
 assert set(changes)==set(names),(changes,names)
 assert all(before[n]==after[n] for n in before if n not in names)
 bpy.context.scene['C27_STATUS']='CONDITIONAL bank1 geometry candidate; frozen original cameras and chair; NOT calibrated/accepted'
 path=P/('hospital_C27_bank1_'+kind+'_CONDITIONAL.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
 bpy.ops.wm.open_mainfile(filepath=str(path));reopened=state();assert reopened==after
 audit[kind]={'source':str(src.relative_to(R)),'source_sha256':sha(src),'candidate':path.name,'candidate_sha256':sha(path),'removed_objects':names[:nremove],'modified_meshes':mods,'changed_objects':changes,'unchanged_other_object_count':len(before)-len(names),'camera_and_chair_unchanged':True,'reopen_state_equal':True,'before_state':before,'after_state':after}
(P/'build_verification.json').write_text(json.dumps(audit,indent=2)+'\n')
print('C27_READY',nremove,'removed',len(names)-nremove,'trimmed; all other object states invariant')
