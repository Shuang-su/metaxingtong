"""Create editable material variant and GLB-compatible image UVs from shared white geometry."""
import bpy, math, json, hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/car_passenger_cabin_white.blend'))
s=bpy.context.scene;s.cycles.use_denoising=False;s.cycles.samples=64
def mat(name,color,rough=.5,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;return m
materials={
 'leather':mat('PBR_dark_door_leather_inferred',(.022,.018,.016),.42),
 'rubber':mat('PBR_rubber',(.008,.010,.012),.68),
 'headliner':mat('PBR_charcoal_headliner',(.065,.065,.059),.94),
 'visor':mat('PBR_visor_warm_gray',(.20,.19,.17),.90),
 'dash_top':mat('PBR_light_dashboard_top',(.38,.38,.35),.78),
 'carbon':mat('PBR_woven_synthetic_approximation',(.12,.12,.12),.48,.15),
 'trim':mat('PBR_satin_edge',(.20,.21,.21),.32,.50),
 'metal':mat('PBR_dark_metal',(.32,.34,.36),.21,.88),
 'mirror':mat('PBR_mirror_no_scene_reflection_claim',(.025,.030,.035),.14,.95),
 'glass':mat('PBR_thin_window',(.52,.61,.65),.08),
 'seat':mat('PBR_black_seat_edge',(.018,.019,.020),.49),
 'vent':mat('PBR_vent_louvers',(.048,.052,.056),.35,.3),
 'carpet':mat('PBR_inferred_floor_carpet',(.026,.028,.030),.95)
}
glass=materials['glass'].node_tree.nodes.get('Principled BSDF');glass.inputs['Transmission Weight'].default_value=1;glass.inputs['IOR'].default_value=1.45
def img_node(m,name,space):
    n=m.node_tree.nodes.new('ShaderNodeTexImage');im=bpy.data.images.load(str(R/'textures'/name),check_existing=True);im.colorspace_settings.name=space;im.filepath='//../textures/'+name;n.image=im;return n
carbon=materials['carbon'];bs=carbon.node_tree.nodes.get('Principled BSDF');tex=img_node(carbon,'woven_basecolor.png','sRGB');carbon.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);ro=img_node(carbon,'woven_roughness.png','Non-Color');carbon.node_tree.links.new(ro.outputs['Color'],bs.inputs['Roughness'])
for k in ['leather','headliner','visor','dash_top','seat','carpet']:
    m=materials[k];te=img_node(m,'fine_grain_height.png','Non-Color');b=m.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.23;b.inputs['Distance'].default_value=.002;m.node_tree.links.new(te.outputs['Color'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],m.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
def geometry_digest():
    arr=[]
    for o in sorted([o for o in s.objects if o.type=='MESH'],key=lambda o:o.name):
        arr.append([o.name,[[round(float(v),7) for v in vert.co] for vert in o.data.vertices],[list(p.vertices) for p in o.data.polygons]])
    return hashlib.sha256(json.dumps(arr,separators=(',',':')).encode()).hexdigest()
digest_before=geometry_digest()
for o in s.objects:
    if o.type!='MESH':continue
    o.data.materials.clear();o.data.materials.append(materials[o['material_group']])
    uv=o.data.uv_layers.new(name='UV_synthetic_repeat')
    for p in o.data.polygons:
        axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
        for li in p.loop_indices:
            co=o.data.vertices[o.data.loops[li].vertex_index].co
            uv.data[li].uv=(co[axes[0]]*4,co[axes[1]]*4)
assert geometry_digest()==digest_before
s['geometry_digest']=digest_before;s['material_notes']='Synthetic PBR approximations; no source-extracted texture or source lighting match claim. UV image textures exported; fine bump is Blender detail only.'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/car_passenger_cabin_material.blend'))
(R/'qa/material-geometry-identity.json').write_text(json.dumps({'vertex_polygon_digest_before':digest_before,'vertex_polygon_digest_after':geometry_digest(),'same_geometry':True,'material_groups':list(materials),'geometry_objects':len([o for o in s.objects if o.type=='MESH']),'procedural_bump_export_limit':'Blender bump nodes not guaranteed in GLB; basecolor and roughness image textures supported'},indent=2)+'\n')
print('MATERIAL_SAVED',digest_before)
