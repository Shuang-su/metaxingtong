import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Star_Awards_Candidate.blend'))
rep={'mesh_count':0,'vertices':0,'triangles':0,'zero_area_faces':[],'nonmanifold_objects':[],'negative_volume':[],'missing_uv':[],'nonfinite':[],'area_lights':[],'assumptions':['Unseen back thickness, floor underside, corner posts and short front ramp are inferred.','Finite covered stage with open front; no audience hall or invented doors.','Dimensions are arbitrary reconstruction units, not measured meters.']}
verts=[];faces=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 rep['mesh_count']+=1;rep['vertices']+=len(o.data.vertices);o.data.calc_loop_triangles();rep['triangles']+=len(o.data.loop_triangles)
 bm=bmesh.new();bm.from_mesh(o.data)
 bad=sum(f.calc_area()<1e-10 for f in bm.faces)
 if bad:rep['zero_area_faces'].append([o.name,bad])
 nb=sum(not e.is_manifold for e in bm.edges)
 if nb:rep['nonmanifold_objects'].append([o.name,nb])
 if bm.calc_volume(signed=True)<-1e-8:rep['negative_volume'].append(o.name)
 if not o.data.uv_layers:rep['missing_uv'].append(o.name)
 if any(not math.isfinite(v) for x in o.data.vertices for v in x.co):rep['nonfinite'].append(o.name)
 off=len(verts);verts.extend([o.matrix_world@v.co for v in o.data.vertices]);faces.extend([tuple(off+i for i in p.vertices)for p in o.data.polygons]);bm.free()
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=False)
for o in bpy.context.scene.objects:
 if o.type!='LIGHT' or o.data.type!='AREA':continue
 # Disk emitter is contained in its full square bounding face. Test 21x21 samples and each edge segment.
 u=o.matrix_world.to_3x3()@Vector((1,0,0));v=o.matrix_world.to_3x3()@Vector((0,1,0));n=o.matrix_world.to_3x3()@Vector((0,0,1));r=o.data.size/2
 minclear=1e9;hits=[]
 for i in range(21):
  for j in range(21):
   pt=o.location+u*(-r+2*r*i/20)+v*(-r+2*r*j/20)
   near=bvh.find_nearest(pt)
   if near[0] is not None:minclear=min(minclear,near[3])
   hit=bvh.ray_cast(pt-n*.01,n,.02)
   if hit[0]is not None:hits.append([i,j])
 rep['area_lights'].append({'name':o.name,'full_bounding_face_samples':441,'intersections':hits,'minimum_distance_to_structure':minclear})
# Actual GLB round trip through Blender importer, texture/file proof, named bounds compared.
def bounds(o):
 vv=[o.matrix_world@Vector(v)for v in o.bound_box];return [min(v[a]for v in vv)for a in range(3)]+[max(v[a]for v in vv)for a in range(3)]
orig={o.name:bounds(o) for o in bpy.context.scene.objects if o.type=='MESH'}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(P/'Star_Awards_Candidate.glb'))
new={o.name:bounds(o)for o in bpy.context.scene.objects if o.type=='MESH'}
errs=[]
for n,bb in orig.items():
 if n in new:errs.append(max(abs(a-b)for a,b in zip(bb,new[n])))
rep['glb_roundtrip']={'imported_mesh_count':len(new),'original_mesh_count':len(orig),'matching_named_objects':len(errs),'maximum_bbox_error':max(errs)if errs else None,'images':[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)}for im in bpy.data.images if im.type=='IMAGE'],'bounds_missing_names':list(set(orig)-set(new))}
bpy.ops.wm.save_as_mainfile(filepath=str(P/'qa/GLB_实际回导验证.blend'))
(P/'qa/technical_audit.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2));print(json.dumps(rep,ensure_ascii=False,indent=2))
