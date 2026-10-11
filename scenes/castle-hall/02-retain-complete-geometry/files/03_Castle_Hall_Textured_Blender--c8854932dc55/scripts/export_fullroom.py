import bpy,json,hashlib,os
from pathlib import Path
from mathutils import Vector,kdtree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/Xingtong_Castle_Hall_FullRoom.blend'));S=bpy.context.scene
# Backface culling exposes real material-side normals, rather than masking holes with double-sided surfaces.
for m in bpy.data.materials:
 if m.users:m.use_backface_culling=True
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/Xingtong_Castle_Hall_FullRoom.blend'),compress=True)
def capture():
 out={};tris=0;area=0
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  vs=[tuple(o.matrix_world@v.co) for v in o.data.vertices];o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles);out[o.name]=vs
  for t in o.data.loop_triangles:
   a,b,c=[Vector(vs[i]) for i in t.vertices];area+=(b-a).cross(c-a).length/2
 return out,tris,area
base,tri,area=capture();bpy.ops.object.select_all(action='DESELECT')
for o in S.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'models/Xingtong_Castle_Hall_FullRoom.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_extras=True,export_cameras=False,export_lights=False)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'models/Xingtong_Castle_Hall_FullRoom.glb'));imp,itri,iarea=capture();errors=[]
for n,a in base.items():
 if n not in imp:continue
 for aa,bb in ((a,imp[n]),(imp[n],a)):
  kd=kdtree.KDTree(len(bb))
  for j,p in enumerate(bb):kd.insert(p,j)
  kd.balance()
  errors.extend(kd.find(p)[2] for p in aa)
r={'original_meshes':len(base),'imported_meshes':len(imp),'same_names':set(base)==set(imp),'triangles_original':tri,'triangles_imported':itri,'max_bidirectional_vertex_error_m':max(errors),'surface_area_relative_error':abs(iarea/area-1),'used_images_embedded':all(n.image and n.image.packed_file for m in bpy.data.materials if m.users and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE'),'all_meshes_uv':all(bool(o.data.uv_layers) for o in bpy.context.scene.objects if o.type=='MESH')}
r['pass']=r['same_names'] and tri==itri and max(errors)<1e-4 and r['surface_area_relative_error']<1e-5 and r['used_images_embedded'] and r['all_meshes_uv'];json.dump(r,open(R/'qa/fullroom_glb_roundtrip.json','w'),indent=2);print(json.dumps(r,indent=2))
