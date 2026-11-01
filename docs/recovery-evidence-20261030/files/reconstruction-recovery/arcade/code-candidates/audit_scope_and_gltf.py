import bpy,json
from pathlib import Path
D=Path(__file__).resolve().parents[1]
def snap():
 out={}
 for o in bpy.context.scene.objects:
  d={'type':o.type,'matrix':[list(r)for r in o.matrix_world]}
  if o.type=='MESH':d.update(vertices=[list(v.co)for v in o.data.vertices],polygons=[list(p.vertices)for p in o.data.polygons],uv=[[list(q.uv)for q in lay.data]for lay in o.data.uv_layers],materials=[m.name if m else None for m in o.data.materials])
  elif o.type=='CAMERA':d.update(lens=o.data.lens,shift=[o.data.shift_x,o.data.shift_y],sensor=o.data.sensor_width)
  elif o.type=='LIGHT':d.update(energy=o.data.energy,color=list(o.data.color),light_type=o.data.type)
  out[o.name]=d
 return out
bpy.ops.wm.open_mainfile(filepath='/workspace/shared/arcade-header-local-20261030/models/arcade_header_R09b_material.blend');a=snap();bpy.ops.wm.open_mainfile(filepath=str(D/'models/arcade_partial_material_R10.blend'));b=snap();assert set(a)==set(b)
changed=[]
for n in a:
 if a[n]!=b[n]:changed.append(n)
assert changed==['M01_header_blue'],changed
am=a['M01_header_blue'].copy();bm=b['M01_header_blue'].copy();am.pop('materials');bm.pop('materials');assert am==bm
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(D/'models/arcade_partial_material_R10.glb'));o=bpy.data.objects['M01_header_blue'];images=[]
for m in o.data.materials:
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE' and n.image:images.append({'name':n.image.name,'size':list(n.image.size),'packed':bool(n.image.packed_file),'node':n.name})
assert any(i['size']==[2048,2048]for i in images)
(D/'qa/final_scope_and_gltf_material.json').write_text(json.dumps({'baseline':'R09b caab61f3d3566d9eb4d77b163f504bffb74bd1e8','same_object_set':True,'changed_only_material_slot':changed,'all_373_mesh_positions_vertices_topology_uv_unchanged':True,'all_cameras_lights_unchanged':True,'gltf_M01_actual_reimport_image_nodes':images,'note':'GLB actual image exists; other procedural materials/AREA lights retain prior limitations'},indent=2))
