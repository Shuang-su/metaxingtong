import bpy,json,hashlib,numpy as np,sys
from pathlib import Path
P=Path(__file__).resolve().parent.parent
mode,source=sys.argv[sys.argv.index('--')+1:];assert mode in ['baseline','candidate'] and source in ['10','11']
# Execute only the frozen array construction, before triangulation/checks. It fresh-loads original R05.
construction=P/'scripts/single_pair_candidate.py';prefix=construction.read_text().split('tri={};tree={};bounds={}')[0];exec(compile(prefix,str(construction),'exec'))
if mode=='candidate':
 for name in main if 'main' in globals() else [n for n in objs if n.startswith('ROOF_MAIN')]:
  o=objs[name];inv=o.matrix_world.inverted()
  from mathutils import Vector
  for vert,co in zip(o.data.vertices,new[name]):vert.co=inv@Vector(co)
  o.data.update()
bpy.context.view_layer.update();scene=bpy.context.scene;scene.camera=bpy.data.objects['SOURCE'+source+(' conditional camera' if source=='11' else ' auxiliary different state')];scene.render.resolution_x=1192;scene.render.resolution_y=671;scene.render.resolution_percentage=100;scene.cycles.samples=8;scene.cycles.use_denoising=False;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(P/'renders'/f'{mode}-source{source}-8s.png')
# Hash actual post-assignment mesh geometry including object world matrices. This is not a saved model hash.
geo={}
for o in scene.objects:
 if o.type=='MESH':
  payload={'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons],'matrix':[list(r) for r in o.matrix_world]};geo[o.name]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
record={'mode':mode,'source':source,'parameter':.55 if mode=='candidate' else .74,'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'construction_script_sha256':hashlib.sha256(construction.read_bytes()).hexdigest(),'render_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'actual_mesh_hashes':geo,'actual_geometry_collection_sha256':hashlib.sha256(json.dumps(geo,sort_keys=True).encode()).hexdigest(),'saved_model':None,'camera':scene.camera.name,'camera_matrix':[list(r) for r in scene.camera.matrix_world],'camera_lens':scene.camera.data.lens,'samples':scene.cycles.samples,'denoise':scene.cycles.use_denoising,'resolution':[1192,671,100],'exposure':scene.view_settings.exposure,'gamma':scene.view_settings.gamma,'view_transform':scene.view_settings.view_transform,'lights':{o.name:{'matrix':[list(r) for r in o.matrix_world],'energy':o.data.energy,'color':list(o.data.color)} for o in scene.objects if o.type=='LIGHT'}}
bpy.ops.render.render(write_still=True);f=Path(scene.render.filepath);record['image_sha256']=hashlib.sha256(f.read_bytes()).hexdigest();record['bytes']=f.stat().st_size;(P/'renders'/f'{mode}-source{source}-recipe.json').write_text(json.dumps(record,indent=2))
