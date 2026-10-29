import bpy,json,hashlib,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=R/'c29';p=json.load(open(P/'valid_shell_profile.json'));old=json.load(open(R/'c29_diagnosis/c28_curtain_mesh_readonly.json'));vv=np.array(old['verts_local']);front_delta=np.array(p['front_new_local_xy'])-vv[:225,:2];back_delta=np.array(p['back_new_local_xy'])-vv[14625:14850,:2];name='Curtain • rebuilt uniform eight-fold drape'
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
for kind in ['MATERIAL','WHITE']:
 src=R/'c28'/('hospital_C28_bank1_'+kind+'_CONDITIONAL.blend');bpy.ops.wm.open_mainfile(filepath=str(src));before=state();o=bpy.data.objects[name];assert len(o.data.vertices)==29250
 if o.data.users>1:o.data=o.data.copy()
 for i,v in enumerate(o.data.vertices):
  d=front_delta[i%225] if i<14625 else back_delta[i%225];v.co.x+=d[0];v.co.y+=d[1]
 o.data.update();o['C29_CHANGE']='Seven nominal cycles, internal spacing correction with valid backside reconstruction';o['C29_UNCERTAINTY']='Visible-fold improvement only; cloth total count, top height and normal gauge unresolved'
 bpy.context.view_layer.update();after=state();assert [n for n in before if before[n]!=after[n]]==[name]
 path=P/('hospital_C29_curtain_'+kind+'_CONDITIONAL.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));assert state()==after
 audit[kind]={'source_sha256':sha(src),'candidate':path.name,'candidate_sha256':sha(path),'changed_objects':[name],'reopen_state_equal':True,'unchanged_other_objects':len(before)-1,'before_state':before,'after_state':after}
 o=bpy.data.objects[name];verts=np.array([list(q.co) for q in o.data.vertices]);(P/(kind+'_actual_curtain_vertices.json')).write_text(json.dumps(verts.tolist()))
(P/'build_verification.json').write_text(json.dumps(audit,indent=2));print('C29_VALID_SHELL_MODELS_READY')
