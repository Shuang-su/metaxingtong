import bpy,pathlib,json,hashlib
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parents[1];records=[]
def bounds(o):
 w=[o.matrix_world@v.co for v in o.data.vertices];return [[min(v[i]for v in w),max(v[i]for v in w)]for i in range(3)]
faces0=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R06_{mode}.blend'));cb=bounds(bpy.data.objects['CEILING_center_rail']);rs=[]
 for o in list(bpy.data.objects):
  if not o.name.startswith('CEILING_crossrail_'):continue
  old=bounds(o); mats=list(o.data.materials);v=[];f=[]
  for x0,x1 in [(old[0][0],cb[0][0]),(cb[0][1],old[0][1])]:
   assert x1>x0
   y0,y1=old[1];z0,z1=old[2];base=len(v);w=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
   v.extend([tuple(o.matrix_world.inverted()@Vector(a))for a in w]);f.extend([tuple(base+j for j in a)for a in faces0])
  d=bpy.data.meshes.new(o.name+'_R07_two_finite_parts');d.from_pydata(v,[],f);d.update();o.data=d
  for m in mats:d.materials.append(m)
  uv=d.uv_layers.new(name='UVMap')
  for face in d.polygons:
   for j,k in enumerate(face.loop_indices):uv.data[k].uv=[(0,0),(1,0),(1,1),(0,1)][j]
  o['r07_scope']='Two closed parts; center rail fills removed overlapping middle. Touching interfaces, NOT Boolean-welded.'
  new=bounds(o);rs.append({'object':o.name,'old_world_bounds':old,'new_world_bounds':new,'removed_middle_x':cb[0],'components':2,'uv':'new local face UV, constant trim/clay; not original UV claim'})
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R07_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R07_{mode}.glb'),export_format='GLB',export_cameras=True)
 records.append({'mode':mode,'center_bounds':cb,'crossrails':rs,'scope':'preserve occupied union; remove duplicate coplanar bottom region. Independent verification pending.'})
(P/'qa/R07-grid-change.json').write_text(json.dumps(records,indent=2))
