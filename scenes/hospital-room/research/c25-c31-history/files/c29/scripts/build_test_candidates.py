import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=R/'c29';params=json.load(open(P/'profile_candidates.json'));name='Curtain • rebuilt uniform eight-fold drape'
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
for tag,p in params.items():
 src=R/'c28/hospital_C28_bank1_MATERIAL_CONDITIONAL.blend';bpy.ops.wm.open_mainfile(filepath=str(src));before=state();o=bpy.data.objects[name];assert len(o.data.vertices)==29250
 if o.data.users>1:o.data=o.data.copy()
 for i,v in enumerate(o.data.vertices):v.co.x+=p['local_x_delta'][i%225]
 o.data.update();o['C29_CHANGE']='Internal fold-frequency hypothesis '+tag+' nominal cycles; first/last complete period unchanged';o['C29_UNCERTAINTY']='Visible major-fold candidate, not proven complete cloth fold count'
 bpy.context.view_layer.update();after=state();changes=[n for n in before if before[n]!=after[n]];assert changes==[name]
 path=P/('hospital_C29_TEST_'+tag+'fold_MATERIAL.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));assert state()==after
 audit[tag]={'source_sha256':sha(src),'candidate':path.name,'candidate_sha256':sha(path),'changed_objects':changes,'reopen_state_equal':True,'unchanged_other_objects':len(before)-1,'before_state':before,'after_state':after}
(P/'test_build_verification.json').write_text(json.dumps(audit,indent=2));print('C29_TEST_MODELS_READY')
