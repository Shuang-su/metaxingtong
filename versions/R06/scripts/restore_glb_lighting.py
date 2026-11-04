"""After importing the matching GLB, restore documented Blender World and Area lights.
Usage blender -b --python this.py -- glb sidecar output.blend.
Does not claim render equivalence in non-Blender applications.
"""
import bpy,json,sys
from mathutils import Matrix
args=sys.argv[sys.argv.index('--')+1:];glb,sidecar,out=args
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=glb)
d=json.load(open(sidecar));s=bpy.context.scene
s.world=bpy.data.worlds.new('Restored World');s.world.use_nodes=True
n=s.world.node_tree.nodes['Background'];n.inputs['Color'].default_value=d['world_background_rgba'];n.inputs['Strength'].default_value=d['world_background_strength']
for x in d['lights']:
 ld=bpy.data.lights.new(x['name'],x['type']);ld.energy=x['energy'];ld.color=x['color'];ld.shape='DISK';ld.size=x['size'];o=bpy.data.objects.new(x['name'],ld);s.collection.objects.link(o);o.matrix_world=Matrix(x['matrix_world'])
s.render.engine=d['engine'];s.cycles.samples=d['samples'];s.cycles.use_denoising=d['denoising'];s.render.threads_mode='FIXED';s.render.threads=d['threads'];s.render.resolution_x,s.render.resolution_y=d['resolution'];s.render.resolution_percentage=100;s.view_settings.view_transform=d['view_transform'];s.camera=bpy.data.objects['source21-conditional'];bpy.ops.wm.save_as_mainfile(filepath=out)
