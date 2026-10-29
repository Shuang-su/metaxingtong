import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=R/'c26';j=json.loads((P/'candidate_manifest.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(P/'hospital_C26_structure_controls_CONDITIONAL.blend'))
bad=[]
for n,old in j['protected_state'].items():
 o=bpy.data.objects[n]
 if o.type=='MESH':new={'matrix':[list(r) for r in o.matrix_world],'vertices':hashlib.sha256(str([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest(),'faces':hashlib.sha256(str([tuple(p.vertices) for p in o.data.polygons]).encode()).hexdigest()}
 else:new={'matrix':[list(r) for r in o.matrix_world],'lens':o.data.lens,'sensor':o.data.sensor_width,'shift':[o.data.shift_x,o.data.shift_y]}
 if new!=old:bad.append(n)
ctl=bpy.data.objects['C26_PARAMETERS__defaults_preserve_C25'];o=bpy.data.objects[j['groups']['column'][0]];key=o['C26_control_key'];s0=list(o.scale)
ctl[key]=1.01;ctl.update_tag();bpy.context.view_layer.update();s1=list(o.scale)
ctl[key]=1.0;ctl.update_tag();bpy.context.view_layer.update();s2=list(o.scale)
test=all(abs(b/a-1.01)<1e-5 for a,b in zip(s0,s1)) and s0==s2
out={'reopen_protected_mesh_camera_mismatches':bad,'protected_count':len(j['protected_state']),'column_control_changes_and_restores':test,'test_only_not_saved':True}
(P/'verification.json').write_text(json.dumps(out,indent=2)+'\n');assert not bad and test,out;print(out)
