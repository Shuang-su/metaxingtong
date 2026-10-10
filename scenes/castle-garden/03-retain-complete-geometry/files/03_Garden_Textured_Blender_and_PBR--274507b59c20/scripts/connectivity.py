import bpy,json
from mathutils.bvhtree import BVHTree
R='/workspace/scratch/fa58bfcf0425/castle_garden_fullscene';bpy.ops.wm.open_mainfile(filepath=R+'/delivery/models/Garden_Complete_Textured.blend');obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('surface_class')!='天然双面薄叶/花瓣'];vs={o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in obs};bb={n:[(min(v[i] for v in vv),max(v[i] for v in vv)) for i in range(3)] for n,vv in vs.items()};trees={o.name:BVHTree.FromPolygons(vs[o.name],[p.vertices[:] for p in o.data.polygons],epsilon=.00001) for o in obs};links={o.name:set() for o in obs}
for i,a in enumerate(obs):
 for b in obs[i+1:]:
  if any(bb[a.name][k][1]<bb[b.name][k][0]-.00001 or bb[b.name][k][1]<bb[a.name][k][0]-.00001 for k in range(3)):continue
  if trees[a.name].overlap(trees[b.name]):links[a.name].add(b.name);links[b.name].add(a.name)
seen=set();comps=[]
for n in links:
 if n in seen:continue
 todo=[n];comp=set()
 while todo:
  x=todo.pop()
  if x in seen:continue
  seen.add(x);comp.add(x);todo+=list(links[x]-seen)
 comps.append(sorted(comp))
comps.sort(key=len,reverse=True);json.dump(comps,open(R+'/independent_qa/structural_components.json','w'),ensure_ascii=False,indent=2);print('component sizes',[len(x) for x in comps]);print('disconnected',comps[1:])
