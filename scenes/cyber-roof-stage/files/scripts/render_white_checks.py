import bpy,json
from mathutils import Vector,Euler
from pathlib import Path
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r03-white.blend'));s=bpy.context.scene;s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_percentage=100
records=json.loads((P/'qa/render-cameras.json').read_text());out=[]
for r in records:
 if r['file']=='source11-r03.png':continue
 if r['camera'] in bpy.data.objects:c=bpy.data.objects[r['camera']]
 else:
  bpy.ops.object.camera_add(location=r['location']);c=bpy.context.object;c.name=r['camera'];c.rotation_euler=Euler(r['rotation']);c.data.lens=r['lens'];c.data.sensor_width=r['sensor_width'];c.data.sensor_fit=r['sensor_fit']
 s.camera=c;s.render.resolution_x=r['resolution'][0];s.render.resolution_y=r['resolution'][1];name=r['file'].replace('.png','-white.png');s.render.filepath=str(P/'renders'/name);bpy.ops.render.render(write_still=True);out.append(dict(r,file=name,material='white same geometry and original lights/world'))
(P/'qa/white-render-cameras.json').write_text(json.dumps(out,indent=2))
