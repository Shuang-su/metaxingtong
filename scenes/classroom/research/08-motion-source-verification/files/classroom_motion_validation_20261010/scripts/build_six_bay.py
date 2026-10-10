import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
p=Path('/workspace/scratch/fa58bfcf0425/classroom_motion_validation_20261010/six_bay_candidate');s=bpy.context.scene;delta=4*.5816229294917844;changes=[]
def bounds(o):
 v=[o.matrix_world@Vector(v) for v in o.bound_box];return [[min(x[i] for x in v) for i in range(3)],[max(x[i] for x in v) for i in range(3)]]
def resize_y(o,newlo,newhi,why):
 lo,hi=bounds(o);old=[lo,hi];inv=o.matrix_world.inverted();o.data=o.data.copy()
 for v in o.data.vertices:
  w=o.matrix_world@v.co;w.y=newlo+(w.y-lo[1])/(hi[1]-lo[1])*(newhi-newlo);v.co=inv@w
 o.data.update();changes.append({'object':o.name,'operation':'resize shared mesh alongY','before':old,'after':bounds(o),'reason':why})
for o in list(bpy.data.objects):
 n=o.name
 if n.startswith('Extended front glass ') and int(n.split()[3])>=6 or n.startswith('Extended front upright ') and int(n.split()[-1])>=7:
  changes.append({'object':n,'operation':'remove four unsupported added bays globally','before':bounds(o)});bpy.data.objects.remove(o,do_unlink=True)
for o in list(bpy.data.objects):
 n=o.name
 if n.startswith(('V3 rear ','V3 transparent rear ')) or n in ['V3 broad masonry pier','FULLROOM inferred central pier outer return']:
  old=bounds(o);o.location.y-=delta;bpy.context.view_layer.update();changes.append({'object':n,'operation':'shared Y translation','dy':-delta,'before':old,'after':bounds(o)})
 elif n.startswith('V3 front horizontal ') or n=='V3 front sill ledge':
  lo,hi=bounds(o);resize_y(o,lo[1],hi[1]-delta,'Retain six front bays, preserve front jamb/open casements')
 elif n in ['V3 inferred rear window-end masonry','FULLROOM inferred rear pier outer return']:
  lo,hi=bounds(o);resize_y(o,lo[1]-delta,hi[1],'Extend actual rear solid return to meet shifted rear-window end; hidden extension remains inferred')
bpy.context.view_layer.update();cam=bpy.data.objects['SOURCE_B'];copy=cam.copy();copy.data=cam.data.copy();copy.name='BASELINE_B_CAMERA_UNSHIFTED';s.collection.objects.link(copy);cam.location.y-=delta
s['source_window_evidence']='B_front16-19 continuous first-window/pier linkage supports6 bays; actual metric lengths remain inferred';s['candidate_status']='UNACCEPTED architecture candidate; furniture unchanged; all scenes retain same geometry per camera';s.camera=bpy.data.objects['SOURCE_C'];bpy.ops.wm.save_as_mainfile(filepath=str(p/'Classroom_SixBay_CANDIDATE.blend'),compress=True)
(p/'qa/shared_changes.json').write_text(json.dumps({'front_bays_before':10,'front_bays_candidate':6,'delta_y':-delta,'new_pier_y':[6.607613563537598-delta,7.1070637702941895-delta],'new_rear_window_end_y':9.893865585327148-delta,'changes':changes,'B_camera_y_before':copy.location.y,'B_camera_y_candidate':cam.location.y,'camera_rationale':'Real window-segment identity shift. Not a per-view object movement. Same geometric correction applies to all cameras. Foreground furniture may regress and must be reported.','geometry_only_candidate_not_final':True},indent=2));print('CANDIDATE BUILT',len(changes))
