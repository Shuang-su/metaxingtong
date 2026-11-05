import bpy,json,hashlib,pathlib
from mathutils.bvhtree import BVHTree
R=pathlib.Path('/workspace/scratch/fa58bfcf0425'); out={}
for kind in ['material','white']:
 p=R/f'forest-diagnostic-replay-20261104/models/R15_log-contact-diagnostic_{kind}.blend';bpy.ops.wm.open_mainfile(filepath=str(p)); rows=[]
 for o in sorted(bpy.context.scene.objects,key=lambda o:o.name):
  if o.name.startswith('FLOWER_') and o.name.endswith('_centre'):
   v=[list(o.matrix_world@x.co) for x in o.data.vertices];f=[list(x.vertices) for x in o.data.polygons];stem=bpy.data.objects[o.name.replace('_centre','_stem')];sv=[stem.matrix_world@x.co for x in stem.data.vertices];sf=[list(x.vertices) for x in stem.data.polygons]
   rows.append(dict(name=o.name,location=list(o.matrix_world.translation),bounds=[[min(x[i] for x in v),max(x[i] for x in v)] for i in range(3)],vertices=len(v),faces=len(f),world_geometry_sha256=hashlib.sha256(json.dumps([v,f]).encode()).hexdigest(),stem_surface_overlap_pairs=len(BVHTree.FromPolygons(v,f).overlap(BVHTree.FromPolygons(sv,sf))),materials=[m.name for m in o.data.materials]))
 out[kind]={'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'centres':rows,'meshes':len([o for o in bpy.context.scene.objects if o.type=='MESH'])}
(R/'forest-stamen-readonly-notes-20261105/saved-state-inspection.json').write_text(json.dumps(out,indent=2))
print('READ_ONLY_INSPECTION',json.dumps(out))
