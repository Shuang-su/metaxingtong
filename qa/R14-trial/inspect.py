import bpy,json
bpy.ops.wm.open_mainfile(filepath='/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105/models/R13_material.blend')
for o in bpy.context.scene.objects:
 if o.type=='MESH' and ('pearl' in o.name.lower() or 'bead' in o.name.lower() or 'TABLE_top' == o.name):
  v=[o.matrix_world@p.co for p in o.data.vertices];print(o.name,len(v),len(o.data.polygons),[[min(p[i] for p in v),max(p[i] for p in v)]for i in range(3)])
