"""Bounded junction checks; not global mechanical certification."""
import bpy,bmesh,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
root=Path(__file__).resolve().parents[1];stage=sys.argv[-1];bpy.ops.wm.open_mainfile(filepath=str(root/'models'/stage/'piano_seaside_material.blend'))
body=bpy.data.objects['P01 grand piano curved rim and bottom'];bm=bmesh.new();bm.from_mesh(body.data)
left=set(bm.verts);components=[]
while left:
 stack=[left.pop()];count=0
 while stack:
  v=stack.pop();count+=1
  for e in v.link_edges:
   w=e.other_vert(v)
   if w in left:left.remove(w);stack.append(w)
 components.append(count)
bm.free();deps=bpy.context.evaluated_depsgraph_get()
def bvh(o):
 ev=o.evaluated_get(deps);me=ev.to_mesh();v=[o.matrix_world@x.co for x in me.vertices];f=[list(x.vertices) for x in me.polygons];tree=BVHTree.FromPolygons(v,f);ev.to_mesh_clear();return tree
bt=bvh(body);key_collisions=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith(('P04 white key','P04 black key')):
  pairs=bt.overlap(bvh(o))
  if pairs:key_collisions.append({'object':o.name,'surface_intersection_pairs':len(pairs)})
prop=bpy.data.objects['P03 lid support'];ends=[prop.matrix_world@Vector((0,0,z)) for z in [-prop.dimensions.z/2,prop.dimensions.z/2]]
# Cylinder local mesh depth is unchanged scale=1, endpoints coincide with physical seats.
seat=bpy.data.objects['P03 prop foot seat'];lid=bpy.data.objects['P02 raised lid'];expected=Vector((.760,.55,1.185));distances=[(p-expected).length for p in ends]
result={'stage':stage,'body_with_fused_cheeks_connected_components':len(components),'component_vertex_counts':components,'body_key_surface_intersections':key_collisions,'prop_lower_endpoint_distance_to_seat_center':min(distances),'prop_top_point_lid_local':[list(lid.matrix_world.inverted()@p) for p in ends],'limits':['Mesh connectivity and bounded body/key collision checks only.','Lid seat and hidden joint design are inferred; no engineering load analysis.','Keyboard action internals and soft upholstery physics are not reconstructed.']}
(root/'qa'/stage/'junction-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
