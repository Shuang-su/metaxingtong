import bpy,json
from pathlib import Path
from mathutils import Euler
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r03.blend'));s=bpy.context.scene;records=json.loads((P/'qa/render-cameras.json').read_text())
for r in records:
 if r['camera'] in bpy.data.objects:continue
 bpy.ops.object.camera_add(location=r['location']);c=bpy.context.object;c.name=r['camera'];c.rotation_euler=Euler(r['rotation']);c.data.lens=r['lens'];c.data.sensor_width=r['sensor_width'];c.data.sensor_fit=r['sensor_fit'];c['purpose']='internal inspection; not observed source baseline'
s.camera=bpy.data.objects['SOURCE11 conditional camera']
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models/roof-r04.blend'))
bpy.ops.export_scene.gltf(filepath=str(P/'models/roof-r04.glb'),export_format='GLB',export_cameras=True,export_extras=True)
d=json.loads((P/'models/roof-r03-recovery.json').read_text());d['source_blend']='roof-r04.blend';d['glb']='roof-r04.glb';d['render_products']='R03 pixels reused: mesh/material/light/source cameras unchanged. Inspection cameras materialized from exact render-cameras.json Euler/location/lens.'
d['objects']=[r for r in d['objects'] if r['type']!='CAMERA']
for o in s.objects:
 if o.type=='CAMERA':
  c=o.data;d['objects'].append({'name':o.name,'type':'CAMERA','matrix_world':[list(r) for r in o.matrix_world],'properties':dict(o.items()),'camera':{k:getattr(c,k) for k in ['lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','type','clip_start','clip_end']}})
(P/'models/roof-r04-recovery.json').write_text(json.dumps(d,indent=2))
w=bpy.data.materials.new('White diagnostic R04');w.use_nodes=True;w.diffuse_color=(.66,.66,.66,1);b=w.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(.66,.66,.66,1);b.inputs['Roughness'].default_value=.7
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(w)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models/roof-r04-white.blend'))
bpy.ops.export_scene.gltf(filepath=str(P/'models/roof-r04-white.glb'),export_format='GLB',export_cameras=True,export_extras=True)
