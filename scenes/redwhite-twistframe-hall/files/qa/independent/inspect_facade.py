import bpy,bmesh,json
from pathlib import Path
ob=bpy.data.objects['central red facade with real opening'];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
r={'raw_polygons':len(ob.data.polygons),'evaluated_polygons':len(me.polygons),'evaluated_degenerate':[],'raw_degenerate':[]}
for f in bm.faces:
 if f.calc_area()<1e-12:r['evaluated_degenerate'].append({'area':f.calc_area(),'coords':[list(ob.matrix_world@v.co)for v in f.verts]})
bm.free();bm=bmesh.new();bm.from_mesh(ob.data)
for f in bm.faces:
 if f.calc_area()<1e-12:r['raw_degenerate'].append({'area':f.calc_area(),'coords':[list(ob.matrix_world@v.co)for v in f.verts]})
Path('independent-twistframe-model-qa-20261104/R04_facade_degeneracy.json').write_text(json.dumps(r,indent=2));print(r)
