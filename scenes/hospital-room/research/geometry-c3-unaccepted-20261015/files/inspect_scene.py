import bpy,sys,json,hashlib
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]);s=bpy.context.scene
r={'meshes':{},'cameras':{},'render':{'engine':s.render.engine,'resolution':[s.render.resolution_x,s.render.resolution_y],'percentage':s.render.resolution_percentage}}
for o in bpy.data.objects:
 if o.type=='MESH':
  vv=[o.matrix_world@v.co for v in o.data.vertices];r['meshes'][o.name]={'vertices':[list(v) for v in vv],'polygons':[list(p.vertices) for p in o.data.polygons],'bounds':[[min(v[i] for v in vv) for i in range(3)],[max(v[i] for v in vv) for i in range(3)]],'materials':[m.name if m else None for m in o.data.materials],'hide_render':o.hide_render,'modifiers':[{'name':m.name,'type':m.type} for m in o.modifiers]}
 elif o.type=='CAMERA':r['cameras'][o.name]={'matrix':[list(row) for row in o.matrix_world],'lens':o.data.lens,'sensor_width':o.data.sensor_width,'sensor_fit':o.data.sensor_fit,'shift_x':o.data.shift_x,'shift_y':o.data.shift_y,'clip_start':o.data.clip_start}
out.write_text(json.dumps(r,ensure_ascii=False))
print('WROTE',out)
for n,m in r['meshes'].items():
 if any(x in n.lower() for x in ['sofa','curtain','armchair','chair','mullion']): print(n,m['bounds'],len(m['vertices']),m['modifiers'])
