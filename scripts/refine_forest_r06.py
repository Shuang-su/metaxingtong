import bpy,pathlib,json,math
ROOT=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/R05_material.blend'))
# Real cross-software PBR representation, replacing nonexportable shader expressions in BOTH saved blend and GLB.
for name,texname in [('Bark','bark_color'),('Leaf','leaf_color'),('Moss_and_earth','moss_color')]:
 m=bpy.data.materials[name];n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');p=n.new('ShaderNodeBsdfPrincipled');p.inputs['Roughness'].default_value=.82 if name!='Leaf' else .65;im=n.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(ROOT/'textures'/(texname+'.png')),check_existing=True);im.image.pack();im.image.filepath='//../textures/'+texname+'.png';im.interpolation='Linear';im.extension='REPEAT';m.node_tree.links.new(im.outputs['Color'],p.inputs['Base Color']);m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface'])
# Remaining old noise-bump not representable as normal map: remove in the saved current material, preserving old versions.
for m in bpy.data.materials:
 if m.use_nodes:
  p=m.node_tree.nodes.get('Principled BSDF')
  if p:
   for l in list(p.inputs['Normal'].links):m.node_tree.links.remove(l)
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 me=ob.data
 if not me.uv_layers:me.uv_layers.new(name='PBR_UV')
 uv=me.uv_layers.active.data;mat=me.materials[0].name if me.materials else ''
 xs=[v.co.x for v in me.vertices];ys=[v.co.y for v in me.vertices];cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2
 leaf_family=('leaves' in ob.name.lower() or 'leaflet' in ob.name.lower() or 'foliage' in ob.name.lower() or 'crown' in ob.name.lower() or 'turf_blades' in ob.name.lower() or 'SHRUB' in ob.name or 'UNDERSTORY' in ob.name or 'BROAD_LEAF' in ob.name)
 for poly in me.polygons:
  for li in poly.loop_indices:
   idx=me.loops[li].vertex_index;v=me.vertices[idx].co
   if mat=='Leaf' and leaf_family and len(me.vertices)%6==0:
    lut=[(0,.5),(1,.5),(.5,0),(.5,1),(.5,.5),(.5,.5)];uv[li].uv=lut[idx%6]
   elif mat=='Bark':uv[li].uv=(math.atan2(v.y-cy,v.x-cx)/math.tau,v.z*.35)
   else:uv[li].uv=(v.x*.18,v.y*.18)
 me.update()
s=bpy.context.scene;s.cycles.use_denoising=False;s.render.resolution_percentage=100;s.cycles.samples=32;s.camera=bpy.data.objects['SOURCE_F_top']
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R06_material.blend'));bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R06_material.glb'),export_format='GLB',export_apply=True,export_cameras=True)
white=bpy.data.materials.get('WHITE_clay')
if white is None:white=bpy.data.materials.new('WHITE_clay');white.use_nodes=True;white.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.65,.65,.65,1)
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R06_white.blend'));bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R06_white.glb'),export_format='GLB',export_apply=True,export_cameras=True)
print('R06_SAVED',len([o for o in s.objects if o.type=='MESH']))
