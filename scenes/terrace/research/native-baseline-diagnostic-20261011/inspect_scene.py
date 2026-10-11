import bpy,json,pathlib
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parent
d={'scene':bpy.context.scene.name,'engine':bpy.context.scene.render.engine,'resolution':[bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y,bpy.context.scene.render.resolution_percentage],'cameras':[],'objects':[],'scenes':[]}
for sc in bpy.data.scenes:
 d['scenes'].append({'name':sc.name,'camera':sc.camera.name if sc.camera else None,'objects':len(sc.objects),'custom':{k:str(v) for k,v in sc.items()}})
for o in bpy.data.objects:
 a={'name':o.name,'type':o.type,'hide_render':o.hide_render,'location':list(o.location),'rotation':list(o.rotation_euler),'dimensions':list(o.dimensions),'collections':[c.name for c in o.users_collection]}
 if o.type=='MESH':
  b=[o.matrix_world@Vector(v) for v in o.bound_box];a['bounds']=[[min(v[i] for v in b),max(v[i] for v in b)] for i in range(3)];a['materials']=[m.name if m else None for m in o.data.materials]
 if o.type=='CAMERA':
  a.update({'lens':o.data.lens,'shift_x':o.data.shift_x,'shift_y':o.data.shift_y,'sensor_width':o.data.sensor_width,'sensor_height':o.data.sensor_height,'sensor_fit':o.data.sensor_fit,'matrix_world':[list(row) for row in o.matrix_world]});d['cameras'].append(a)
 d['objects'].append(a)
(P/'scene_audit.json').write_text(json.dumps(d,ensure_ascii=False,indent=2))
print('SCENEAUDIT',json.dumps({k:d[k] for k in ['scene','scenes','engine','resolution','cameras']},ensure_ascii=False))
print('STRUCTURAL',json.dumps([o for o in d['objects'] if any(s in o['name'].lower() for s in ['wall','beam','grid','perg','rail','arch','rear','post','门','墙','井','梁'])],ensure_ascii=False))
