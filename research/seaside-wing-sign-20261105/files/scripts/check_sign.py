import bpy,bmesh,json,os,hashlib
from mathutils.bvhtree import BVHTree
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));out={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=r+'/models/'+mode+'.blend');res=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or not o.name.startswith('SIGN_'):continue
  b=bmesh.new();b.from_mesh(o.data);res.append({'name':o.name,'vertices':len(b.verts),'faces':len(b.faces),'nonmanifold_edges':sum(not e.is_manifold for e in b.edges),'zeroarea_faces':sum(f.calc_area()<1e-12 for f in b.faces),'volume':b.calc_volume(signed=True)});b.free()
 out[mode]=res
json.dump(out,open(r+'/qa/sign-topology-r00.json','w'),indent=2);print(out)
