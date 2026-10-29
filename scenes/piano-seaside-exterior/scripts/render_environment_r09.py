"""Render explicit global states. No camera selection ever changes state or geometry."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];Q=R/'qa/r09';mode=sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/r09/piano_seaside_material.blend'));sc=bpy.context.scene
source=['source_N4037','source_N6318','source_N2518','source_N2453','source_N6766'];checks=[f'check_{i:02d}' for i in range(8)]+['check_top']
def render(name,path,width,samples):
 sc.camera=bpy.data.objects[name];sc.render.resolution_x=width;sc.render.resolution_y=width*9//16;sc.render.resolution_percentage=100;sc.eevee.taa_render_samples=samples;sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)
# Extra close camera is only an environment diagnostic; no scene object is hidden.
d=bpy.data.cameras.new('diagnostic_lantern');o=bpy.data.objects.new('diagnostic_lantern',d);sc.collection.objects.link(o);o.location=(-1.8,.1,1.0);o.rotation_euler=(Vector((-.92,1.22,.21))-o.location).to_track_quat('-Z','Y').to_euler();d.lens=55
if mode=='preview':
 out=Q/'low';out.mkdir(exist_ok=True)
 for state in ['S40_sunset','S105_bluehour']:
  sc.world=bpy.data.worlds['R09 '+state+' global environment']
  for name in source+['main']+(checks+['diagnostic_lantern'] if state=='S40_sunset' else []):render(name,out/(state+'_'+name+'.png'),640,8)
else:
 sc.world=bpy.data.worlds['R09 S40_sunset global environment']
 for name in source+['main']+checks+['diagnostic_lantern']:render(name,Q/(name+'.png'),960 if name.startswith('check') else 1920,32)
 # Render every source in alternate state too, independently of source time labels.
 out=Q/'alternate_S105';out.mkdir(exist_ok=True);sc.world=bpy.data.worlds['R09 S105_bluehour global environment']
 for name in source+['main']:render(name,out/(name+'.png'),960,16)
print('R09_RENDER_FINISHED',mode)
