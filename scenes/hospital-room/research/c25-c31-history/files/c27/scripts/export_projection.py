import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];bpy.ops.wm.open_mainfile(filepath=str(R/'c26/hospital_C26_structure_controls_CONDITIONAL.blend'))
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
j={'objects':{},'cameras':{}}
for o in bpy.data.objects:
 if 'vertical mullion' in o.name:
  ev=o.evaluated_get(dg);mesh=ev.to_mesh()
  j['objects'][o.name]={'location':list(o.location),'matrix': [list(r) for r in o.matrix_world],'vertices': [list(v.co) for v in mesh.vertices],'world_vertices':[list(o.matrix_world@v.co) for v in mesh.vertices],'dimensions':list(o.dimensions),'mesh_users':o.data.users,'modifiers':[m.type for m in o.modifiers]}
  ev.to_mesh_clear()
for k in ['H','G','665']:
 c=bpy.data.objects['C10_'+k+'_shared_sofa_height_CONDITIONAL'];m=c.calc_matrix_camera(dg,x=1920,y=1080,scale_x=1,scale_y=1)@c.matrix_world.inverted()
 j['cameras'][k]={'projection':[list(r) for r in m],'matrix':[list(r) for r in c.matrix_world],'lens':c.data.lens}
(R/'c27/projection_source.json').write_text(json.dumps(j,indent=2))
print([(n,o['dimensions']) for n,o in j['objects'].items()])
