import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent;ns={'__file__':str(OUT/'audit_physics.py')}
exec(Path(ns['__file__']).read_text().split('for s in sys.argv[sys.argv.index')[0],ns)
bpy.ops.wm.open_mainfile(filepath='/workspace/scratch/fa58bfcf0425/hospital_anchor_preparation_20261014/restored/hospital_D_before_J1_cameras.blend');dg=bpy.context.evaluated_depsgraph_get()
a=ns['extract'](bpy.data.objects[ns['CURTAIN']],dg);b=ns['extract'](bpy.data.objects['ROOM_SHELL__joined_solid__hidden_extents_inferred'],dg)
v=[p+Vector((0,-.04011060774326324,0)) for p in a['verts']];tree=BVHTree.FromPolygons(v,a['triangles'],all_triangles=True,epsilon=0)
by_shell={}
for ia,ib in tree.overlap(b['bvh']):by_shell[ib]=by_shell.get(ib,0)+1
r=[]
for ib,n in by_shell.items():
 vv=[b['verts'][k] for k in b['triangles'][ib]];bb=ns['bounds'](vv);r.append({'shell_triangle':ib,'candidate_pairs':n,'bounds':bb,'constant_axes':{['X','Y','Z'][i]:bb[0][i] for i in range(3) if bb[1][i]-bb[0][i]<1e-7}})
(OUT/'P0_boundary_contact_diagnosis.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
