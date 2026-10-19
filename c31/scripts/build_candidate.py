import bpy,json,hashlib,ast
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=R/'c31';loops=json.load(open(R/'c31_diagnosis/actual_endboard_hole_geometry.json'))['loops'];holes=loops[1:];h=sum(a['world_max'][2]-a['world_min'][2] for a in holes)/2;center=sum((a['world_max'][2]+a['world_min'][2])/2 for a in holes)/2;targets={'Bed end • moulded central recess':1.225*h,'Bed end • cream inset face':.95*h};t=ast.parse((R/'c29/scripts/build_valid_candidate.py').read_text());f=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='state');exec(compile(ast.Module(body=[f],type_ignores=[]),'state','exec'))
def box(o):
 vs=[o.matrix_world@v.co for v in o.data.vertices];return {'min':[min(v[i] for v in vs) for i in range(3)],'max':[max(v[i] for v in vs) for i in range(3)]}
audit={}
for kind in ['MATERIAL','WHITE']:
 src=R/'c29'/('hospital_C29_curtain_'+kind+'_CONDITIONAL.blend');bpy.ops.wm.open_mainfile(filepath=str(src));before=state();changes={}
 for n,height in targets.items():
  o=bpy.data.objects[n];bb=box(o);oldh=bb['max'][2]-bb['min'][2];oldc=(bb['max'][2]+bb['min'][2])/2;inv=o.matrix_world.inverted()
  if o.data.users>1:o.data=o.data.copy()
  for v in o.data.vertices:
   w=o.matrix_world@v.co;w.z=center+(w.z-oldc)*height/oldh;v.co=inv@w
  o.data.update();o['C31_EVIDENCE']='Native1801/1804 central-slot/aperture relative vertical proportion and aligned centers; no camera calibration';o['C31_UNCERTAINTY']='Manual soft-edge bounds; x/y and depth retained; partial G projection check required';changes[n]={'before':bb,'after':box(o),'z_scale':height/oldh,'new_center_world_z':center,'target_height_over_hole_height':height/h}
 bpy.context.view_layer.update();after=state();changed=[n for n in before if before[n]!=after[n]];assert set(changed)==set(targets);dst=P/('hospital_C31_recess_'+kind+'_CONDITIONAL.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True);bpy.ops.wm.open_mainfile(filepath=str(dst));assert state()==after
 audit[kind]={'source_C29_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'changed_objects':changed,'changes':changes,'aperture_height':h,'aperture_center_z':center,'all_other_recorded_states_unchanged':True,'reopen_equal':True,'before_state':before,'after_state':after}
(P/'build_verification.json').write_text(json.dumps(audit,indent=2));print('C31_CANDIDATES_READY',targets,center)
