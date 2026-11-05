"""Run: blender -b -t 1 --python scripts/restore_glb.py. GLB+sidecar restores area lights and world; no blend dependency."""
import bpy,json
from pathlib import Path
from mathutils import Matrix
P=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(P/'models/roof-r04.glb'))
d=json.loads((P/'models/roof-r04-recovery.json').read_text());s=bpy.context.scene
for ob in d['objects']:
 if ob['type']=='LIGHT':
  o=bpy.data.objects.get(ob['name'])
  if o is not None:bpy.data.objects.remove(o,do_unlink=True)
  x=ob['light'];l=bpy.data.lights.new(ob['name'],x['type']);l.energy=x['energy'];l.color=x['color'];l.size=x['size'];l.shape='DISK'
  o=bpy.data.objects.new(ob['name'],l);s.collection.objects.link(o);o.matrix_world=Matrix(ob['matrix_world'])
 if ob['type']=='CAMERA':
  o=bpy.data.objects.get(ob['name']);x=ob['camera']
  if o:o.matrix_world=Matrix(ob['matrix_world']);o.data.lens=x['lens'];o.data.sensor_width=x['sensor_width'];o.data.clip_start=x['clip_start'];o.data.clip_end=x['clip_end'];o.data.sensor_fit=x['sensor_fit'];o.data.sensor_height=x['sensor_height'];o.data.shift_x=x['shift_x'];o.data.shift_y=x['shift_y'];o.data.type=x['type']
s.world=bpy.data.worlds.new('Restored world');s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs[0].default_value=d['world']['background'];s.world.node_tree.nodes['Background'].inputs[1].default_value=d['world']['strength']
s.camera=bpy.data.objects['SOURCE11 conditional camera'];s.render.engine='CYCLES';s.cycles.samples=d['render']['samples'];s.cycles.use_denoising=False;s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
s.render.pixel_aspect_x=d['render']['pixel_aspect'][0];s.render.pixel_aspect_y=d['render']['pixel_aspect'][1];s.view_settings.look=d['render']['look'];s.view_settings.exposure=d['render']['exposure'];s.view_settings.gamma=d['render']['gamma']
bpy.ops.wm.save_as_mainfile(filepath=str(P/'qa/restored-r04-from-glb.blend'))
