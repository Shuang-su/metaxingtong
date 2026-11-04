import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).parent;R=O.parent/'dreamfold-phone-study-20261104';out={};snaps={}
f=json.load(open(R/'qa/camera-fit.json'));T=Matrix(f['rotation']).to_4x4();T.translation=Vector(f['translation']);A=Matrix.Rotation(math.radians(45),4,'X');A.translation=Vector((0,.6,-.025))+A.to_3x3()@Vector((0,-.6,0));expected=T@A
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'versions/V04/models/phone-{mode}.blend'));s=bpy.context.scene;d={};audit=[]
 for o in s.objects:
  if o.type!='MESH':continue
  m=o.data;m.calc_loop_triangles();v=[list(o.matrix_world@x.co) for x in m.vertices];faces=[list(t.vertices) for t in m.loop_triangles];bm=bmesh.new();bm.from_mesh(m);audit.append({'name':o.name,'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.calc_area()<1e-12 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True)});bm.free();d[o.name]={'v':v,'f':faces,'uv':[[list(x.uv) for x in l.data] for l in m.uv_layers],'hide':[o.hide_render,o.hide_viewport]}
 n='P04_rear_leaf_unseen_geometry_INFERRED';o=s.objects[n];bv={k:BVHTree.FromPolygons(x['v'],x['f'],all_triangles=True) for k,x in d.items()};out[mode]={'mesh_count':len(d),'audit':audit,'P04_expected45_matrix_error':max(abs(o.matrix_world[i][j]-expected[i][j]) for i in range(4) for j in range(4)),'rear_contacts':[{'other':k,'triangle_pairs':len(bv[n].overlap(v))} for k,v in bv.items() if k!=n]};snaps[mode]=d
out['shared_world_geometry_uv_visibility_exact']=snaps['material']==snaps['white'];(O/'saved-check.json').write_text(json.dumps(out,indent=2))
