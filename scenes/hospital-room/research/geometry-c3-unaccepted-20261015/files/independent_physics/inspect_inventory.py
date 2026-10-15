import bpy,json,sys
from pathlib import Path
out=Path('/workspace/scratch/fa58bfcf0425/hospital_geometry_candidate_20261015/independent_physics')
r=[]
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
 if o.type != 'MESH': continue
 if any(k in o.name.lower() for k in ['curtain','window','blind','room_shell','pillar','connector']):
  oe=o.evaluated_get(dg);m=oe.to_mesh();v=[oe.matrix_world@v.co for v in m.vertices]
  r.append({'name':o.name,'raw_verts':len(o.data.vertices),'eval_verts':len(m.vertices),'eval_faces':len(m.polygons),'bounds':[list(map(min,zip(*v))),list(map(max,zip(*v)))], 'mods':[{'name':x.name,'type':x.type,'viewport':x.show_viewport,'render':x.show_render,'thickness':getattr(x,'thickness',None),'offset':getattr(x,'offset',None)} for x in o.modifiers]});oe.to_mesh_clear()
p=out/(Path(bpy.data.filepath).stem+'_inventory.json');p.write_text(json.dumps(r,ensure_ascii=False,indent=2));print(p)
for a in r:
 if not a['name'].startswith('Blind'):print(a)
