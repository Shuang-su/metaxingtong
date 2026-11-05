import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent
construction=P/'scripts/single_pair_candidate.py';exec(compile(construction.read_text().split('tri={};tree={};bounds={}')[0],str(construction),'exec'))
for name in [n for n in objs if n.startswith('ROOF_MAIN')]:
 o=objs[name];inv=o.matrix_world.inverted()
 for vert,co in zip(o.data.vertices,new[name]):vert.co=inv@Vector(co)
 o.data.update()
bpy.context.view_layer.update();s=bpy.context.scene;s.camera=bpy.data.objects['SOURCE11 conditional camera'];s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100;s.cycles.samples=8;s.cycles.use_denoising=False
geo={}
for o in s.objects:
 if o.type=='MESH':
  payload={'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons],'matrix':[list(r) for r in o.matrix_world]};geo[o.name]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
recipe=json.loads((P/'renders/candidate-source11-recipe.json').read_text());assert geo==recipe['actual_mesh_hashes']
bpy.ops.wm.save_as_mainfile(filepath=str(P/'export/roof-paired-a055.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'export/roof-paired-a055.glb'),export_format='GLB',export_cameras=True,export_extras=True)
d=json.loads((P.parent/'cyber-roof-stage-20261105/models/roof-r05-recovery.json').read_text());d['source_blend']='roof-paired-a055.blend';d['glb']='roof-paired-a055.glb';d['render']['samples']=8;d['render_products']={'scope':'experimental single a=.55; SOURCE FAILED; not full inspection suite','candidate_material_images':['../renders/candidate-source10-8s.png','../renders/candidate-source11-8s.png'],'timing':'images rendered before editable export; exact post-assignment mesh-hash equivalence checked by exporter; independent QA pending','white_images':[],'old_R05_check_images':'not included as current experiment renders; original camera objects retained only'};d['paired_experiment']={'a':.55,'basis_input_sha256':recipe['input_sha256'],'construction_script_sha256':recipe['construction_script_sha256'],'executed_geometry_collection_sha256':recipe['actual_geometry_collection_sha256'],'source_status':'FAILED','no_production_replacement':True,'limitations':'original intersection persists; normal-relative projected thickness changes; two-source height/silhouette failures retained'}
(P/'export/roof-paired-a055-recovery.json').write_text(json.dumps(d,indent=2))
w=bpy.data.materials.new('White paired a055 technical shared geometry');w.use_nodes=True;w.diffuse_color=(.66,.66,.66,1);b=w.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(.66,.66,.66,1);b.inputs['Roughness'].default_value=.7
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(w)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'export/roof-paired-a055-white.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'export/roof-paired-a055-white.glb'),export_format='GLB',export_cameras=True,export_extras=True)
files=[]
for f in sorted((P/'export').iterdir()):
 if f.is_file():files.append({'path':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size})
(P/'export/artifact-manifest.json').write_text(json.dumps({'files':files,'actual_mesh_hashes':geo,'render_geometry_equivalent':True,'independent_QA':'pending'},indent=2))
