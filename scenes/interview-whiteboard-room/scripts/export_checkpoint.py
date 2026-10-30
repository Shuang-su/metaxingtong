"""Early evaluated geometry export for validation while slow image renders proceed.
Main build later writes equivalent exports from the same model.
"""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'models/r03'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'interview-room-material.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'interview-room-material.glb'),export_format='GLB',export_apply=True,export_cameras=False,export_lights=False,export_extras=True)
white=bpy.data.materials.get('WHITE MODEL same geometry')
if white is None:
    white=bpy.data.materials.new('WHITE MODEL same geometry');white.use_nodes=True
    p=white.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.72,.72,.72,1);p.inputs['Roughness'].default_value=.8
for o in bpy.context.scene.objects:
    if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'interview-room-white.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'interview-room-white.glb'),export_format='GLB',export_apply=True,export_cameras=False,export_lights=False,export_extras=True)
