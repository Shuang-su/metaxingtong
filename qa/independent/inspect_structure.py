import bpy,json,sys,hashlib,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];out=Path(args[0]);scene=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();trees={};bounds={}
for o in scene.objects:
 if o.type not in ['MESH','CURVE']:continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];ps=[list(p.vertices)for p in me.polygons];trees[o.name]=BVHTree.FromPolygons(vs,ps,all_triangles=False);bounds[o.name]=[[min(v[i]for v in vs)for i in range(3)],[max(v[i]for v in vs)for i in range(3)]];ev.to_mesh_clear()
floor_names=[n for n in trees if n=='finite pale stage slab' or 'continuous tunnel floor' in n]
def ray(names,origin,direction,distance):
 hits=[]
 for n in names:
  loc,normal,index,dist=trees[n].ray_cast(Vector(origin),Vector(direction),distance)
  if loc is not None:hits.append({'name':n,'point':list(loc),'distance':dist})
 return sorted(hits,key=lambda h:h['distance'])
# Explicit finite floor inspection domain within the side returns and through the back depth.
floor_tests=[]
for ix in range(33):
 x=-3.8+7.6*ix/32
 for iy in range(41):
  y=4.5+9.8*iy/40;hits=ray(floor_names,(x,y,.4),(0,0,-1),.9);floor_tests.append({'point':[x,y],'hit':hits[0]if hits else None})
portal_tests=[]
facade=[n for n in trees if n=='central red facade with real opening']
for x in [-3.5,-2.5,-1.5,0,1.5,2.5,3.5]:
 for z in [.25,.75,1.25,1.75,2.25,2.75,3.25,3.75,4.25,4.75,5.25]:
  portal_tests.append({'x':x,'z':z,'facade_hits':ray(facade,(x,0,z),(0,1,0),7)})
keys=['finite pale stage slab','inferred continuous tunnel floor','tunnel left return','tunnel right return','tunnel upper dark return','tunnel distant dark stop','white curved upper fascia','upper curved dark glazing','tilted crimson circular disc']
result={'blend':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'test_scope':'Finite floor rays over x[-3.8,3.8],y[4.5,14.3]; central facade-only rays at stated x,z; key evaluated world bounds. Not whole-scene watertightness, collision freedom, or source truth.','floor_names':floor_names,'floor_rays':floor_tests,'floor_ray_count':len(floor_tests),'floor_misses':sum(t['hit']is None for t in floor_tests),'portal_rays':portal_tests,'key_bounds':{n:bounds[n]for n in keys if n in bounds},'suspension_bounds':{n:bounds[n]for n in bounds if 'suspension'in n or 'hanging'in n or 'support'in n}}
out.write_text(json.dumps(result,indent=2));print('STRUCTURE_OUT',out,'FLOOR_RAYS',len(floor_tests),'MISSES',result['floor_misses'])
