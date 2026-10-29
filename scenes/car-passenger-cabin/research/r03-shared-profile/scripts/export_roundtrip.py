"""Actual glTF export, fresh-scene import, geometric and state comparison."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[1]
def snapshot():
 bpy.context.view_layer.update();out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();points=[o.matrix_world@v.co for v in o.data.vertices]
  out[o.get('object_id',o.name)]={'points':set(tuple(round(float(c),5) for c in v) for v in points),'raw_points':points,'triangles':len(o.data.loop_triangles),'bounds':[[min(v[a] for v in points) for a in range(3)],[max(v[a] for v in points) for a in range(3)]],'hidden':o.hide_render}
 return out
bpy.ops.wm.open_mainfile(filepath=str(R/'models/D1_shared_dashboard_white.blend'))
s=bpy.context.scene;s.frame_set(1);white1=snapshot();s.frame_set(2);white2=snapshot()
bpy.ops.wm.open_mainfile(filepath=str(R/'models/D1_shared_dashboard_material.blend'))
s=bpy.context.scene;s.frame_set(1);original1=snapshot();s.frame_set(2);original2=snapshot();s.frame_set(1)
equal=lambda a,b: set(a)==set(b) and all(a[n]['points']==b[n]['points'] and a[n]['triangles']==b[n]['triangles'] for n in a)
def distance(a,b):
 kd=KDTree(len(b))
 for i,v in enumerate(b):kd.insert(v,i)
 kd.balance()
 return max(kd.find(v)[2] for v in a)
def geometric_errors(a,b):
 return {n:max(distance(a[n]['raw_points'],b[n]['raw_points']),distance(b[n]['raw_points'],a[n]['raw_points'])) for n in a if n in b}
ident={'closed_equal':equal(white1,original1),'open_equal':equal(white2,original2),'mesh_count':len(original1),'no_hidden_meshes':not any(x['hidden'] for x in original1.values())}
assert ident['closed_equal'] and ident['open_equal']
bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
 if o.type=='MESH' or o.name=='STATE_passenger_door_hinge':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'models/D1_shared_dashboard.glb'),export_format='GLB',use_selection=True,export_extras=True,export_animations=True,export_frame_range=True,export_force_sampling=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_image_format='AUTO')
# Fresh empty scene ensures this is a real read-back, not inspection of original objects.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(R/'models/D1_shared_dashboard.glb'))
s=bpy.context.scene;s.frame_set(1);read1=snapshot();s.frame_set(2);read2=snapshot();s.frame_set(1)
diff=[]
for n in original1:
 if n not in read1:diff.append({'id':n,'error':'missing'});continue
 a=original1[n];b=read1[n];err=max(abs(a['bounds'][i][j]-b['bounds'][i][j]) for i in range(2) for j in range(3))
 diff.append({'id':n,'original_triangles':a['triangles'],'imported_triangles':b['triangles'],'bound_max_abs_error':err,'same_unique_positions_rounded_1e5':a['points']==b['points']})
mesh_quality=[]
for o in s.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);raw=sum(not e.is_manifold for e in bm.edges);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
 mesh_quality.append({'id':o.get('object_id',o.name),'raw_seam_boundary_edges':raw,'welded_nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'welded_zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'welded_signed_volume':bm.calc_volume(signed=True)});bm.free()
errs1=geometric_errors(original1,read1);errs2=geometric_errors(original2,read2)
report={'operation':'Blender 4.3.2 actual export, delete all scene objects, actual glTF importer, no original geometry present during read-back','white_material_identity':ident,'original_meshes':len(original1),'imported_meshes':len(read1),'closed_geometry_within_1e5':max(errs1.values())<1e-5,'open_geometry_within_1e5':max(errs2.values())<1e-5,'closed_max_bidirectional_vertex_distance':max(errs1.values()),'open_max_bidirectional_vertex_distance':max(errs2.values()),'exact_rounded_point_set_open':equal(original2,read2),'open_vertex_errors':errs2,'comparisons':diff,'import_mesh_quality':mesh_quality,'limitations':['Open quaternion conversion produces sub-microunit position changes; rounded sets are not a distance test; max bidirectional nearest-vertex errors reported','UV/normal split vertices are welded only in disposable bmesh for topology statistics; imported file preserved unchanged','Procedural fine bump not exported; basecolor and roughness raster textures supported','Not another DCC application smoke test','Does not establish source alignment, dimensions, or continuous collision-free door sweep']}
bpy.ops.wm.save_as_mainfile(filepath=str(R/'qa/glb_actual_reimport.blend'))
(R/'qa/glb-roundtrip-report.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:v for k,v in report.items() if k not in ['comparisons','import_mesh_quality','limitations']})
