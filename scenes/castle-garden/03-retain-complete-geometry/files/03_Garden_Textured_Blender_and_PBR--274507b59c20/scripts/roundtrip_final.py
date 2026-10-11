import bpy,json,struct
from mathutils.kdtree import KDTree
R='/workspace/scratch/fa58bfcf0425/castle_garden_fullscene';D=R+'/delivery'
bpy.ops.wm.open_mainfile(filepath=D+'/models/Garden_Complete_Textured.blend')
def coords():return list(set(tuple(o.matrix_world@v.co) for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices))
def triangles():
 t=0
 for o in bpy.context.scene.objects:
  if o.type=='MESH':o.data.calc_loop_triangles();t+=len(o.data.loop_triangles)
 return t
native=coords();nt=triangles();kd=KDTree(len(native))
for i,p in enumerate(native):kd.insert(p,i)
kd.balance()
for variant,out in [('Textured','GLB真实回导.json'),('White','白模GLB真实回导.json')]:
 bpy.ops.wm.read_factory_settings(use_empty=True);path=D+'/models/Garden_Complete_'+variant+'.glb';bpy.ops.import_scene.gltf(filepath=path)
 pts=coords();ki=KDTree(len(pts))
 for i,p in enumerate(pts):ki.insert(p,i)
 ki.balance();err1=max(kd.find(p)[2] for p in pts);err2=max(ki.find(p)[2] for p in native)
 used={n.image for o in bpy.context.scene.objects if o.type=='MESH' for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image};imgs=[{'name':i.name,'size':list(i.size),'pixels':len(i.pixels),'has_data':i.has_data} for i in used]
 blob=open(path,'rb').read();ln=struct.unpack_from('<I',blob,12)[0];g=json.loads(blob[20:20+ln]);r={'source_variant':variant,'native_triangles':nt,'imported_triangles':triangles(),'imported_meshes':len([o for o in bpy.context.scene.objects if o.type=='MESH']),'native_unique_points':len(native),'imported_unique_points':len(pts),'bidirectional_nearest_world_vertex_max_error':max(err1,err2),'within_1e_5_model_units':max(err1,err2)<1e-5,'embedded_images':len(g.get('images',[])),'all_images_embedded':all('bufferView' in i for i in g.get('images',[])),'imported_used_images':imgs,'all_used_images_decoded':all(i['pixels']>0 and min(i['size'])>0 for i in imgs),'double_sided_materials':sum(m.get('doubleSided',False) for m in g.get('materials',[])),'note':'逐向最近点误差验证；避免坐标落在十进制量化边界两侧导致假不等。三角多重集由独立报告另验。'}
 json.dump(r,open(D+'/qa/'+out,'w'),ensure_ascii=False,indent=2)
