import bpy,json,bmesh
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/workspace/scratch/fa58bfcf0425/seaside_scene_fullscene/source/models/Seafront_Textured.blend')
out={'collections':{},'cameras':[]}
for c in bpy.data.collections:
 obs=[]
 for o in c.objects:
  d={'name':o.name,'type':o.type,'loc':list(o.location),'dims':list(o.dimensions)}
  if o.type=='MESH':
   bm=bmesh.new();bm.from_mesh(o.data);d.update(v=len(bm.verts),f=len(bm.faces),boundary=sum(e.is_boundary for e in bm.edges),nonmanifold=sum(not e.is_manifold for e in bm.edges));bm.free()
  obs.append(d)
 out['collections'][c.name]=obs
for o in bpy.data.objects:
 if o.type=='CAMERA':out['cameras'].append({'name':o.name,'loc':list(o.location),'rotation':list(o.rotation_euler),'lens':o.data.lens})
json.dump(out,open('/workspace/scratch/fa58bfcf0425/seaside_scene_fullscene/qa/original_inventory.json','w'),indent=2)
