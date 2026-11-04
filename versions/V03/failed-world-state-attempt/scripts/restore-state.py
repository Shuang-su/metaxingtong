# Usage from Blender console: exec(open('/path/restore-state.py').read())
# Or blender -b imported.blend --python restore-state.py -- material
# Applies exact archived state to an already imported V03 GLB; no geometry edits.
import bpy,json,sys
from pathlib import Path
from mathutils import Matrix
V=Path(__file__).resolve().parents[1]
variant=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'material'
state=json.load(open(V/f'qa/{variant}-scene-state.json'));s=bpy.context.scene
for k,v in state['render'].items():setattr(s.render,k,v)
for k,v in state['cycles'].items():setattr(s.cycles,k,v)
for k,v in state['color_management'].items():setattr(s.view_settings,k,v)
s.display_settings.display_device=state['display_device']
if s.world is None:s.world=bpy.data.worlds.new('Restored world')
s.world.color=state['world']['color'];s.world.use_nodes=state['world']['use_nodes']
for name,c in state['cameras'].items():
 o=bpy.data.objects.get(name)
 if o is None:o=bpy.data.objects.new(name,bpy.data.cameras.new(name));s.collection.objects.link(o)
 o.matrix_world=Matrix(c['matrix_world'])
 for k in ['type','lens','sensor_width','sensor_height','sensor_fit','clip_start','clip_end','shift_x','shift_y']:setattr(o.data,k,c[k])
 o.data.dof.use_dof=c['dof_use_dof']
for name,l in state['lights'].items():
 o=bpy.data.objects.get(name)
 if o is None:o=bpy.data.objects.new(name,bpy.data.lights.new(name,l['type']));s.collection.objects.link(o)
 o.matrix_world=Matrix(l['matrix_world'])
 for k in ['energy','color','shape','size','size_y','use_shadow']:setattr(o.data,k,l[k])
s.camera=bpy.data.objects[state['active_camera']];bpy.context.view_layer.update()
