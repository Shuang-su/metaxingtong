import bpy,json,sys
from pathlib import Path
from mathutils import Vector,Quaternion
import math
R=Path(__file__).resolve().parents[1];d=json.loads((R/'docs/diagnostic-configuration-b.json').read_text());C=d['camera'];L=d['light'];preview='preview' in sys.argv;receipts=[]
for label,file in [('baseline',R/'inputs/keyring-material.blend'),('candidate',R/'models'/('r07b-material.blend' if (R/'models/r07b-material.blend').exists() else 'r07-material.blend'))]:
 bpy.ops.wm.open_mainfile(filepath=str(file));s=bpy.context.scene;c=s.objects.get(C['name'])
 if c is None:bpy.ops.object.camera_add();c=bpy.context.object;c.name=C['name']
 c.location=C['location'];c.data.lens=C['lens'];c.data.sensor_width=C['sensor_width'];c.rotation_mode='QUATERNION';c.rotation_quaternion=(Vector(C['target'])-c.location).to_track_quat('-Z','Y')@Quaternion((0,0,1),math.radians(C['roll_degrees']));s.camera=c
 bpy.ops.object.light_add(type='AREA',location=L['location']);l=bpy.context.object;l.name=L['name'];l.data.energy=L['energy'];l.data.color=L['color'];l.data.size=L['size'];l.data.shape='SQUARE';l.rotation_euler=(Vector(L['target'])-l.location).to_track_quat('-Z','Y').to_euler()
 bpy.context.view_layer.update()
 lights=[{'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'shape':o.data.shape,'size':o.data.size,'matrix':[list(row) for row in o.matrix_world]} for o in s.objects if o.type=='LIGHT']
 assert len(lights)==4 and sum(x['name']==L['name'] for x in lights)==1
 bg=s.world.node_tree.nodes['Background'];receipts.append({'label':label,'input_file':str(file),'lights':lights,'world_background':list(bg.inputs['Color'].default_value),'world_strength':bg.inputs['Strength'].default_value,'camera_matrix':[list(row) for row in c.matrix_world],'camera_lens':c.data.lens,'scope':'artificial underside diagnostic only'})
 s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.samples=8 if preview else 32;s.cycles.use_denoising=False;s.render.resolution_percentage=40 if preview else 100;s.render.filepath=str(R/'renders'/f'{"preview-b" if preview else "diagnostic-b"}-{label}.png');bpy.ops.render.render(write_still=True)

assert receipts[0]['lights']==receipts[1]['lights'] and receipts[0]['world_background']==receipts[1]['world_background'] and receipts[0]['camera_matrix']==receipts[1]['camera_matrix']
(R/'docs'/('diagnostic-preview-state.json' if preview else 'diagnostic-render-state.json')).write_text(json.dumps(receipts,indent=2))
