import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/scratch/fa58bfcf0425/seaside_scene_fullscene';bpy.ops.wm.open_mainfile(filepath=R+'/models/Seafront_Textured.blend');bpy.context.view_layer.update();res={}
for name in ['Undulating_coastal_land_slope','Inland_walk_1m10']:
 o=bpy.data.objects[name];res[name]={'matrix':[list(x) for x in o.matrix_world],'firstverts':[list(v.co) for v in o.data.vertices[:20]],'count':len(o.data.vertices)}
ls=[]
for o in bpy.context.scene.objects:
 if not o.name.endswith('emissive_diffuser'):continue
 h=bpy.data.objects[o.name.replace('emissive_diffuser','luminaire_housing')];vs=[o.matrix_world@v.co for v in o.data.vertices];tree=BVHTree.FromPolygons([h.matrix_world@v.co for v in h.data.vertices],[tuple(p.vertices) for p in h.data.polygons]);top=max(v.z for v in vs);samples=[]
 for e in o.data.edges:
  a,b=[vs[i] for i in e.vertices]
  for k in range(11):
   v=a.lerp(b,k/10);hit,_,_,_=tree.ray_cast(Vector((v.x,v.y,top-1)),Vector((0,0,1)),2)
   samples.append(None if hit is None else hit.z-top)
 ls.append({'name':o.name,'samples':len(samples),'misses':samples.count(None),'max_gap':max(x for x in samples if x is not None),'min_gap':min(x for x in samples if x is not None)})
res['lights']=ls;json.dump(res,open(R+'/independent_qa/contact_probe.json','w'),indent=2)
