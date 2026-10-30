"""R05 cheap pixel check before expensive complete final render; not final QA resolution."""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/r05/interview-room-material.blend'))
s=bpy.context.scene;s.cycles.samples=20;s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100
for key in ['front','oblique']:
 s.camera=next(o for o in s.objects if o.type=='CAMERA' and o.name.startswith('SOURCE') and key in o.name)
 s.render.filepath=str(ROOT/f'qa/r05/quick-{key}-640x360.png');bpy.ops.render.render(write_still=True)
