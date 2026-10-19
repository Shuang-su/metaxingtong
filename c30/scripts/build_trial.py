import bpy,json,hashlib,ast
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];P=R/'c30';fit=json.load(open(R/'c30_diagnosis/height_projection_fit.json'));dz=fit['fits']['joint']['delta_z'];translate=['Bed • mattress and sheet','Bed • continuous base tray','Bed • integrated side rail','Bed • integrated side rail.001','Bed • inferred low foot bumper'];supports=['Bed • caster upright'+s for s in ['', '.001','.002','.003']];allowed=set(translate+supports)
# Reuse exact scene-state recorder from C29 for comparable frozen-object checks.
t=ast.parse((R/'c29/scripts/build_valid_candidate.py').read_text());f=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='state');exec(compile(ast.Module(body=[f],type_ignores=[]),'state','exec'))
def bounds(o):
 q=[o.matrix_world@v.co for v in o.data.vertices];return {'min':[min(v[i] for v in q) for i in range(3)],'max':[max(v[i] for v in q) for i in range(3)]}
audit={}
for kind in ['MATERIAL','WHITE']:
 src=R/'c29'/('hospital_C29_curtain_'+kind+'_CONDITIONAL.blend');bpy.ops.wm.open_mainfile(filepath=str(src));before=state();bb={n:bounds(bpy.data.objects[n]) for n in allowed};anchors={}
 for n in translate:
  o=bpy.data.objects[n];m=o.matrix_world.copy();m.translation.z+=dz;o.matrix_world=m;o['C30_CONDITIONAL']='Rigid deck rise; dimensions preserved. Visible covering edge is not an independently measured mattress boundary.'
 bpy.context.view_layer.update()
 for n in supports:
  o=bpy.data.objects[n];top=bb[n]['max'][2];anchor=0.19420463405549526;anchors[n]={'anchor_world_z':anchor,'old_top':top,'delta_top':dz,'status':'unobserved support completion assumption'};inv=o.matrix_world.inverted()
  if o.data.users>1:o.data=o.data.copy()
  for v in o.data.vertices:
   w=o.matrix_world@v.co;w.z+=dz*max(0,min(1,(w.z-anchor)/(top-anchor)));v.co=inv@w
  o.data.update();o['C30_UNCONFIRMED_SUPPORT']='Extend upper support to connect raised tray; no observed support dimensions.'
 bpy.context.view_layer.update();after=state();changed=[n for n in before if before[n]!=after[n]];assert set(changed)==allowed
 ba={n:bounds(bpy.data.objects[n]) for n in allowed};mb=bb[translate[0]];ma=ba[translate[0]];assert abs((ma['max'][2]-ma['min'][2])-(mb['max'][2]-mb['min'][2]))<1e-6
 dst=P/('hospital_C30_beddeck_'+kind+'_TRIAL.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True);bpy.ops.wm.open_mainfile(filepath=str(dst));assert state()==after
 audit[kind]={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'delta_z':dz,'changed_objects':changed,'before_bounds':bb,'after_bounds':ba,'support_assumptions':anchors,'mattress_thickness_preserved':True,'reopen_state_equal':True,'before_state':before,'after_state':after}
(P/'build_verification.json').write_text(json.dumps(audit,indent=2));print('C30_TRIAL_MODELS_READY',dz)
