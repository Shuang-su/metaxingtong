import bpy,json
from pathlib import Path
D=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath='/workspace/shared/arcade-header-local-20261030/models/arcade_header_R09b_material.blend');s=bpy.context.scene

def sig(o):return {'matrix':[list(r)for r in o.matrix_world],'verts':[list(v.co)for v in o.data.vertices],'polys':[list(p.vertices)for p in o.data.polygons],'uv':[[list(v.uv)for v in lay.data]for lay in o.data.uv_layers]}
a={o.name:sig(o)for o in s.objects if o.type=='MESH'}
m=bpy.data.materials.new('R10 M01 CONDITIONAL source poster partial - NOT calibrated');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.5;tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.name='DERIVED_POSTER_ATLAS';im=bpy.data.images.load(str(D/'textures/DERIVED_EXISTING_UV_ATLAS_BASE.png'));im.pack();tex.image=im;tex.interpolation='Closest';uv=m.node_tree.nodes.new('ShaderNodeUVMap');uv.uv_map='UVMap';m.node_tree.links.new(uv.outputs['UV'],tex.inputs['Vector']);m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);o=bpy.data.objects['M01_header_blue'];o.data.materials.clear();o.data.materials.append(m);o['R10_scope']='Single panel only. Source low-left cabinet conditionally mapped M01, adjacent claw machine supports left-end but continuity not proven. Other cabinets remain neutral.'
assert a=={o.name:sig(o)for o in s.objects if o.type=='MESH'}
s['R10_scope']='Material-only partial observed source; same 373 geometry meshes and UVs, source cameras/lights unchanged. No invented texture. Missing remains gray. Source-lit color, not intrinsic albedo.'
# Inspection cameras will be added only in render memory; saved original scene cameras unchanged.
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/arcade_partial_material_R10.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'models/arcade_partial_material_R10.glb'),export_format='GLB',export_cameras=True,export_lights=True)
(D/'qa/build_scope.json').write_text(json.dumps({'all_mesh_vertices_topology_matrices_and_uv_exact':True,'mesh_count':len(a),'only_material_changed':'M01_header_blue','source_cabinet_identity':'conditional M01 because low-left neighboring claw machine, not proven exact slot','saved_cameras_added':0,'image_atlas_packed':True},indent=2))
# Actual shared white variant, same geometry and existing UV. All image data retained but not used by white shader.
w=bpy.data.materials.new('R10 shared geometry white');w.use_nodes=True;w.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.62,.62,.62,1)
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(w)
assert a=={o.name:sig(o)for o in s.objects if o.type=='MESH'}
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/arcade_partial_white_R10.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'models/arcade_partial_white_R10.glb'),export_format='GLB',export_cameras=True,export_lights=True)
