import bpy,json,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=R/'c28';audit=json.load(open(P/'build_verification.json'));out={}
for kind in ['WHITE','MATERIAL']:
 states=[]
 for v in ['c27','c28']:
  bpy.ops.wm.open_mainfile(filepath=str(R/v/('hospital_'+v.upper()+'_bank1_'+kind+'_CONDITIONAL.blend')))
  states.append({n:np.array([list(bpy.data.objects[n].matrix_world@q.co) for q in bpy.data.objects[n].data.vertices]) for n in audit[kind]['changed_objects']})
 diffs=[]
 for a in audit[kind]['mesh_translations']:
  n=a['name'];d=states[1][n]-states[0][n];expected=np.array([0,0,a['world_z_translation']]);diffs.append({'name':n,'max_world_vertex_deviation_from_intended_translation':float(np.abs(d-expected).max())})
 out[kind]=diffs
 assert max(q['max_world_vertex_deviation_from_intended_translation'] for q in diffs)<1e-6
(P/'world_translation_verification.json').write_text(json.dumps(out,indent=2));print('PASS exact intended world translations within 1e-6 scene units')
