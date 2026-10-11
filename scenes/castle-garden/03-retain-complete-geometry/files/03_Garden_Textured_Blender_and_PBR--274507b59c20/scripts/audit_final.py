import bpy,bmesh,json,hashlib,os,math,collections
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/scratch/fa58bfcf0425/castle_garden_fullscene';D=R+'/delivery/models';Q=R+'/independent_qa';report={}
def sha(p):return hashlib.sha256(open(p,'rb').read()).hexdigest()
def bvh(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
def topology(obs):
 out=[]
 for o in obs:
  b=bmesh.new();b.from_mesh(o.data);bmesh.ops.remove_doubles(b,verts=list(b.verts),dist=1e-6)
  out.append(dict(name=o.name,plant=o.get('surface_class')=='天然双面薄叶/花瓣',inconsistent_winding=sum(e.is_manifold and not e.is_contiguous for e in b.edges),boundary=sum(e.is_boundary for e in b.edges),nonmanifold=sum(not e.is_manifold for e in b.edges),degenerate=sum(f.calc_area()<1e-10 for f in b.faces),signed_volume=b.calc_volume(signed=True)));b.free()
 return out
def geom(obs):
 # Quantized world triangle multiset independent of vertex splits/material partition.
 ts=[]
 for o in obs:
  o.data.calc_loop_triangles();vs=[tuple(round(float(a),4) for a in o.matrix_world@v.co) for v in o.data.vertices]
  ts.extend(tuple(sorted(vs[i] for i in t.vertices)) for t in o.data.loop_triangles)
 return collections.Counter(ts)
bpy.ops.wm.open_mainfile(filepath=D+'/Garden_Complete_Textured.blend');s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH'];native=geom(obs);report['sha256']={f:sha(D+'/'+f) for f in ['Garden_Complete_Textured.blend','Garden_Complete_White.blend','Garden_Complete_Textured.glb','Garden_Complete_White.glb']};report['topology']=topology(obs);report['native_triangles']=sum(native.values());report['hidden_meshes']=[o.name for o in obs if o.hide_render or o.hide_viewport];report['unit_system']=s.unit_settings.system
wall=bvh(bpy.data.objects['Visible_violet_masonry_facade_patch']);leaves=[bvh(o) for o in obs if o.name.startswith(('Pointed_double_door','Tall_cyan_leaded_window'))];errors=[];hole=solid=0
for ix in range(261):
 x=-6.499+12.998*ix/260
 for iz in range(137):
  z=.001+6.798*iz/136;v=Vector((x,-2,z));d=Vector((0,1,0));h=wall.ray_cast(v,d)[0] is not None;l=any(b.ray_cast(v,d)[0] is not None for b in leaves)
  if h and l:errors.append([x,z,'wall_blocks_leaf_silhouette'])
  if not h and not l:errors.append([x,z,'unexpected_wall_hole'])
  hole+=int(l);solid+=int(h)
report['facade_dense_rays']={'samples':261*137,'hole_samples':hole,'solid_samples':solid,'errors':errors}
slab=bvh(bpy.data.objects['推定_有限基础板_闭合底面']);fail=[]
for ix in range(201):
 for iy in range(101):
  x=-6.549+13.098*ix/200;y=-5.499+6.348*iy/100;top=slab.ray_cast(Vector((x,y,1)),Vector((0,0,-1)))[0];bot=slab.ray_cast(Vector((x,y,-1)),Vector((0,0,1)))[0]
  if top is None or bot is None or abs((top.z-bot.z)-.4)>1e-4:fail.append([x,y])
report['slab_dense_rays']={'samples':201*101*2,'errors':fail}
zmin=min((o.matrix_world@v.co).z for o in obs for v in o.data.vertices);zmax=max((o.matrix_world@v.co).z for o in obs for v in o.data.vertices);lights=[]
for o in s.objects:
 if o.type=='LIGHT' and o.data.type=='AREA':
  a=o.data.size/2;b=(o.data.size_y if o.data.shape in ['RECTANGLE','ELLIPSE'] else o.data.size)/2;zs=[(o.matrix_world@Vector((x,y,0))).z for x in [-a,a] for y in [-b,b]];lights.append({'name':o.name,'plane_z_bounds':[min(zs),max(zs)],'entire_plane_clear_by_z':min(zs)>zmax or max(zs)<zmin})
report['lights']=lights;report['roundtrip']={}
for variant in ['Textured','White']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=D+'/Garden_Complete_'+variant+'.glb');oo=[o for o in bpy.context.scene.objects if o.type=='MESH'];g=geom(oo)
 ims=[]
 for i in bpy.data.images:
  try:pix=i.pixels[0] if len(i.pixels) else None
  except:pix=None
  ims.append({'name':i.name,'size':list(i.size),'readable':pix is not None})
 report['roundtrip'][variant]={'triangles':sum(g.values()),'triangle_multiset_equal_1e4':g==native,'missing_native_triangles':sum((native-g).values()),'extra_imported_triangles':sum((g-native).values()),'objects':len(oo),'images':ims,'topology':topology(oo)}
bpy.ops.wm.open_mainfile(filepath=D+'/Garden_Complete_White.blend');wg=geom([o for o in bpy.context.scene.objects if o.type=='MESH']);report['white_blend_triangle_multiset_equal_1e4']=wg==native
json.dump(report,open(Q+'/independent_final.json','w'),ensure_ascii=False,indent=2);print('AUDIT_DONE')
