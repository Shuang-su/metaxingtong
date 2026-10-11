import bpy,json,hashlib,os
from mathutils import Vector
from mathutils.kdtree import KDTree
R='/workspace/scratch/fa58bfcf0425/ktv_fullroom/delivery/models/'
def gather():
 d={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or any(c.name=='09_Optional_Moving_Balloon_Dog' for c in o.users_collection):continue
  o.data.calc_loop_triangles()
  d[o.name]={'points':[tuple(o.matrix_world@v.co) for v in o.data.vertices],'triangles':len(o.data.loop_triangles),'materials':[m.name if m else '' for m in o.data.materials]}
 return d
def dist(a,b):
 kd=KDTree(len(b))
 for i,p in enumerate(b):kd.insert(Vector(p),i)
 kd.balance();return max(kd.find(Vector(p))[2] for p in a)
def compare(a,b):
 out={'count_before':len(a),'count_after':len(b),'missing':sorted(set(a)-set(b)),'extra':sorted(set(b)-set(a)),'triangle_mismatch':[],'vertex_distance_max':0,'vertex_distance_over_1e-5':[],'material_slots_mismatch':[]}
 for n,v in a.items():
  if n not in b:continue
  w=b[n]
  if v['triangles']!=w['triangles']:out['triangle_mismatch'].append(n)
  if set(v['points'])!=set(w['points']):
   m=max(dist(v['points'],w['points']),dist(w['points'],v['points']));out['vertex_distance_max']=max(out['vertex_distance_max'],m)
   if m>1e-5:out['vertex_distance_over_1e-5'].append([n,m])
  if len(v['materials'])!=len(w['materials']):out['material_slots_mismatch'].append([n,v['materials'],w['materials']])
 out['triangles_before']=sum(v['triangles'] for v in a.values());out['triangles_after']=sum(v['triangles'] for v in b.values());return out
names=['KTV_Complete_Open_Stage.blend','KTV_Complete_Open_Stage.glb','KTV_Complete_Open_Stage_White.blend']
res={'sha256':{n:hashlib.sha256(open(R+n,'rb').read()).hexdigest() for n in names if os.path.exists(R+n)}}
bpy.ops.wm.open_mainfile(filepath=R+names[0]);a=gather()
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=R+names[1]);b=gather();res['actual_glb_import']=compare(a,b)
if os.path.exists(R+names[2]):
 bpy.ops.wm.open_mainfile(filepath=R+names[2]);c=gather();res['white_geometry']=compare(a,c)
json.dump(res,open('/workspace/scratch/fa58bfcf0425/ktv_fullroom/independent_qa/independent_roundtrip.json','w'),indent=2)
