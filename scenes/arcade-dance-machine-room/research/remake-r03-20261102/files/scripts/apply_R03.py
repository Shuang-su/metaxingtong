import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(D/'models/arcade_remake_R02_material.blend'));s=bpy.context.scene

def snapshot():
 return {o.name:{'v':[list(v.co)for v in o.data.vertices],'faces':[list(p.vertices)for p in o.data.polygons],'matrix':[list(v)for v in o.matrix_world],'uv':{layer.name:[list(d.uv)for d in layer.data]for layer in o.data.uv_layers}}for o in s.objects if o.type=='MESH'}
a=snapshot();cam={o.name:{'matrix':[list(v)for v in o.matrix_world],'lens':o.data.lens}for o in s.objects if o.type=='CAMERA'};lights={o.name:{'matrix':[list(v)for v in o.matrix_world],'energy':o.data.energy}for o in s.objects if o.type=='LIGHT'}
o=bpy.data.objects['M01_header_blue'];uv=o.data.uv_layers.new(name='R03_conditional_source_plane');o.data.uv_layers.active=uv
for poly in o.data.polygons:
 for li in poly.loop_indices:
  v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=((v.x+.86)/1.72,(v.z+.77)/1.54)
m=bpy.data.materials.new('R03 M01 partial source-lit NOT albedo');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(D/'textures/R03/DERIVED_SOURCE_LIT_BASE.png'));tex.image.pack();tex.interpolation='Linear';tex.extension='EXTEND';uvn=n.new('ShaderNodeUVMap');uvn.uv_map=uv.name;l.new(uvn.outputs['UV'],tex.inputs['Vector']);l.new(tex.outputs['Color'],n.get('Principled BSDF').inputs['Base Color']);n.get('Principled BSDF').inputs['Roughness'].default_value=.6
o.data.materials.append(m);front=[]
for poly in o.data.polygons:
 if poly.normal.y<-.9:poly.material_index=len(o.data.materials)-1;front.append(poly.index)
o['partial_texture']='2522.827654 source-only; live foreground excluded; unknown neutral; conditional four-round-unit H not true UV calibration'
b=snapshot();changes=[]
for name in a:
 aa=dict(a[name]);bb=dict(b[name]);au=aa.pop('uv');bu=bb.pop('uv');assert aa==bb
 for layer in au:assert au[layer]==bu[layer]
 if set(au)!=set(bu):changes.append(name)
assert changes==['M01_header_blue']
assert cam=={o.name:{'matrix':[list(v)for v in o.matrix_world],'lens':o.data.lens}for o in s.objects if o.type=='CAMERA'}
assert lights=={o.name:{'matrix':[list(v)for v in o.matrix_world],'energy':o.data.energy}for o in s.objects if o.type=='LIGHT'}
for name,loc in [('R03_DETAIL_FRONT',(-3.5,-4,3.7)),('R03_DETAIL_OBLIQUE',(-5.1,-4,4.0))]:
 d=bpy.data.cameras.new(name);d.lens=55;d.sensor_width=36;c=bpy.data.objects.new(name,d);s.collection.objects.link(c);c.location=loc;c.rotation_euler=(Vector((-3.5,-.12,3.66))-c.location).to_track_quat('-Z','Y').to_euler();c['status']='local inspection camera, not source calibration'
s['status']='R03 partial single-panel source texture; geometry/source camera still FAIL'
(D/'qa/R03/scope.json').write_text(json.dumps({'all_R02_mesh_vertices_faces_matrix_unchanged':True,'all_existing_UV_layers_unchanged':True,'new_UV_layer_objects':changes,'new_front_material_polygons':front,'all_original_cameras_lights_unchanged':True,'inspection_cameras_added':['R03_DETAIL_FRONT','R03_DETAIL_OBLIQUE'],'no_other_cabinet_propagation':True},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/arcade_remake_R03_material.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'models/arcade_remake_R03_material.glb'),export_format='GLB',export_cameras=True,export_lights=True)
w=bpy.data.materials.new('R03 persistent same geometry white');w.use_nodes=True;w.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.62,.62,.62,1);w.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.6
for ob in s.objects:
 if ob.type=='MESH':
  ob.data.materials.clear();ob.data.materials.append(w)
  for po in ob.data.polygons:po.material_index=0
assert b==snapshot()
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/arcade_remake_R03_white.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'models/arcade_remake_R03_white.glb'),export_format='GLB',export_cameras=True,export_lights=True)
