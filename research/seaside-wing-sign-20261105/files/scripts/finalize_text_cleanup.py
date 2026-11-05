import bpy,bmesh,os,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));report={}
def stats(b):
 seen=set();components=[]
 for v in b.verts:
  if v in seen:continue
  stack=[v];seen.add(v);n=0
  while stack:
   a=stack.pop();n+=1
   for e in a.link_edges:
    x=e.other_vert(a)
    if x not in seen:seen.add(x);stack.append(x)
  components.append(n)
 return {'v':len(b.verts),'e':len(b.edges),'f':len(b.faces),'components':sorted(components),'euler':len(b.verts)-len(b.edges)+len(b.faces),'nonmanifold':sum(not e.is_manifold for e in b.edges),'zero_polygon':sum(f.calc_area()<1e-12 for f in b.faces),'volume':b.calc_volume(signed=True)}
def tree(mesh):
 mesh.calc_loop_triangles();return BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(t.vertices) for t in mesh.loop_triangles],all_triangles=True)
def rays(t):
 mask=[]
 for j in range(180):
  z=2.74+(j+.5)*.83/180
  for i in range(640):
   x=-1.52+(i+.5)*3.04/640;hit=t.ray_cast(Vector((x,2.8,z)),Vector((0,1,0)),1.0);mask.append(hit[0] is not None)
 return mask
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=r+'/models/'+mode+'.blend');o=bpy.data.objects['SIGN_QQ炫舞_font_proxy'];oldcoords=[v.co.copy() for v in o.data.vertices];b=bmesh.new();b.from_mesh(o.data);before=stats(b);mask0=rays(tree(o.data)) if mode=='material' else None
 for k in range(6):
  bmesh.ops.dissolve_limit(b,angle_limit=1e-5,use_dissolve_boundaries=False,verts=list(b.verts),edges=list(b.edges),delimit={'NORMAL'});bmesh.ops.dissolve_degenerate(b,dist=1e-7,edges=list(b.edges));bmesh.ops.recalc_face_normals(b,faces=list(b.faces))
 after=stats(b);b.to_mesh(o.data);b.free();o.data.calc_loop_triangles();area=[((o.data.vertices[t.vertices[1]].co-o.data.vertices[t.vertices[0]].co).cross(o.data.vertices[t.vertices[2]].co-o.data.vertices[t.vertices[0]].co)).length/2 for t in o.data.loop_triangles];mask1=rays(tree(o.data)) if mode=='material' else None
 report[mode]={'before':before,'after':after,'max_same_index_coordinate_change':max((a-v.co).length for a,v in zip(oldcoords,o.data.vertices)),'triangle_count':len(area),'zero_triangles':sum(a<1e-12 for a in area),'min_triangle_area':min(area),'font_front_orthographic_mask_grid':[640,180],'mask_disagreements':sum(a!=b for a,b in zip(mask0,mask1)) if mask0 else None,'mask_hit_count_before':sum(mask0) if mask0 else None,'mask_hit_count_after':sum(mask1) if mask1 else None,'mask_scope':'115200 front rays preserve sampled outline/holes for bevel-free pre/post cleanup only; no original glyph-reconstruction or continuous-hole proof'}
 bpy.ops.wm.save_as_mainfile(filepath=r+'/models/'+mode+'.blend');bpy.ops.export_scene.gltf(filepath=r+'/models/'+mode+'.glb',export_format='GLB',export_cameras=True,export_lights=False)
json.dump(report,open(r+'/qa/sign-text-cleanup-r03.json','w'),indent=2);print(report)
