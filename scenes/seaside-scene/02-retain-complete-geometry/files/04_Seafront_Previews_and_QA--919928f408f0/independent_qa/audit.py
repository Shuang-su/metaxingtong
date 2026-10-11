import bpy,bmesh,json,math,hashlib,os
from mathutils import Vector,kdtree
from mathutils.bvhtree import BVHTree
R='/workspace/scratch/fa58bfcf0425/seaside_scene_fullscene';O=R+'/independent_qa';report={}
def world(o):return [o.matrix_world@v.co for v in o.data.vertices]
def audit():
 out={};data={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  vs=world(o); bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-4);bm.normal_update();o.data.calc_loop_triangles()
  thin=any(x in o.name.lower() for x in ['leaflet','groundcover','ocean'])
  out[o.name]={'vertices':len(vs),'triangles':len(o.data.loop_triangles),'boundary':sum(e.is_boundary for e in bm.edges),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.calc_area()<1e-10 for f in bm.faces),'volume':bm.calc_volume(signed=True),'thin_allowed':thin,'hidden':o.hide_render,'modifiers':[m.type for m in o.modifiers]};bm.free()
  data[o.name]=vs
 return out,data
bpy.ops.wm.open_mainfile(filepath=R+'/models/Seafront_Textured.blend');S=bpy.context.scene;S.view_layers[0].update();inv,base=audit();report['objects']=inv
report['animation']={'actions':len(bpy.data.actions),'drivers':[(o.name,len(o.animation_data.drivers)) for o in S.objects if o.animation_data and o.animation_data.drivers]};report['images']=[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE']
# Structural seam sampling in road-relative positions, independent world-space BVH.
names=['Two_way_road_7m20','Promenade_2m25','Inland_walk_1m10','Curb_top','Curb_top.001','Continuous_rocky_seawall_slope','Undulating_coastal_land_slope','Inferred_finite_roadbed_core'];trees={}
for n in names:
 o=bpy.data.objects[n];trees[n]=BVHTree.FromPolygons(world(o),[tuple(p.vertices) for p in o.data.polygons])
def pos(s,off,z):
 d=-.00044*max(s-38,0);f=math.sqrt(1+d*d);return Vector((-.00022*max(s-38,0)**2+off/f,s-off*d/f,z))
seams=[]
for off,lo,hi in [(-5.995,-89,314),(-3.755,-94,549),(-3.60,-94,549),(3.60,-94,549),(3.755,-94,549),(4.845,-84,392)]:
 bad=[];heights=[];bottom_misses=0
 for i in range(1200):
  s=lo+(hi-lo)*i/1199
  for delta in [-.012,-.006,0,.006,.012]:
   p=pos(s,off+delta,20);hits=[t.ray_cast(p,Vector((0,0,-1)),30)[0] for t in trees.values()];zs=[v.z for v in hits if v is not None]
   bottomhit=any(t.ray_cast(pos(s,off+delta,-20),Vector((0,0,1)),30)[0] is not None for t in trees.values())
   if not bottomhit:bottom_misses+=1
   if not zs or (off!=-5.995 and max(zs)<-.01):bad.append([s,off+delta,max(zs) if zs else None])
   if zs:heights.append(max(zs))
 seams.append({'off':off,'samples':6000,'bottom_misses':bottom_misses,'bad_count':len(bad),'bad_examples':bad[:15],'top_range':[min(heights),max(heights)] if heights else None})
report['dense_vertical_seams']=seams
# Luminaire complete diffuser boundary projected into housing local XY, top intersects housing lower shell slightly as intended.
lights=[]
for o in S.objects:
 if not o.name.endswith('emissive_diffuser'):continue
 h=bpy.data.objects[o.name.replace('emissive_diffuser','luminaire_housing')];hb=[v.co for v in h.data.vertices];vs=[h.matrix_world.inverted()@p for p in world(o)];extent=[(min(v[i] for v in hb),max(v[i] for v in hb)) for i in range(3)]
 lights.append({'name':o.name,'all_vertices_within_housing_xy':all(extent[i][0]-1e-5<=v[i]<=extent[i][1]+1e-5 for v in vs for i in [0,1]),'diffuser_z_in_housing_local':[min(v.z for v in vs),max(v.z for v in vs)],'housing_z':extent[2]})
report['diffuser_full_vertices']=lights
# True independent imports, comparing all world-space vertices to original object point sets.
report['roundtrip']={}
for variant in ['Textured','White']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=R+'/models/Seafront_'+variant+'.glb');imp,dat=audit();diff=[];worst=0
 for n,vs in dat.items():
  if n not in base:diff.append({'extra':n});continue
  kd=kdtree.KDTree(len(base[n]));
  for i,v in enumerate(base[n]):kd.insert(v,i)
  kd.balance();err=max(kd.find(v)[2] for v in vs);rev=kdtree.KDTree(len(vs))
  for i,v in enumerate(vs):rev.insert(v,i)
  rev.balance();err=max(err,max(rev.find(v)[2] for v in base[n]));worst=max(worst,err)
  if err>1e-4 or imp[n]['triangles']!=inv[n]['triangles']:diff.append({'name':n,'max_error':err,'triangles':[inv[n]['triangles'],imp[n]['triangles']]})
 report['roundtrip'][variant]={'objects':len(dat),'max_world_vertex_error':worst,'differences':diff,'missing':list(set(base)-set(dat)),'nonthin_boundary':[n for n,d in imp.items() if d['boundary'] and not d['thin_allowed']],'degenerate':sum(d['degenerate'] for d in imp.values()),'images':[{'name':i.name,'packed':bool(i.packed_file),'size':list(i.size)} for i in bpy.data.images if i.source=='FILE']}
for variant in ['Textured','White']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/Seafront_'+variant+'.blend');ii,dd=audit();report[variant+'_blend_matches_world_vertices']=set(dd)==set(base) and all(len(dd[n])==len(base[n]) and max((a-b).length for a,b in zip(dd[n],base[n]))<1e-6 for n in dd)
report['sha256']={f:hashlib.sha256(open(R+'/models/'+f,'rb').read()).hexdigest() for f in ['Seafront_Textured.blend','Seafront_White.blend','Seafront_Textured.glb','Seafront_White.glb']}
json.dump(report,open(O+'/independent_audit.json','w'),ensure_ascii=False,indent=2)
print('AUDIT_DONE',json.dumps({k:v for k,v in report.items() if k not in ['objects','images']},ensure_ascii=False))
