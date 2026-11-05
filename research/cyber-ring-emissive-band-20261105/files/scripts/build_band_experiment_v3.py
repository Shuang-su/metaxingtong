import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent;src=P.parent/'cyber-roof-paired-shell-study-20261105/export/roof-paired-a055.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:];mode=args[0];candidate=mode=='freeze' or args[1]=='candidate';recipe=json.loads((P/'textures-v2/pattern-recipe.json').read_text());o=bpy.data.objects['STAGE_OUTER LED front full circumference inferred'];m=o.data
assert recipe['author_parameters']['columns']==1024
for filename,sha in recipe['files'].items():assert hashlib.sha256((P/'textures-v2'/filename).read_bytes()).hexdigest()==sha
# One author-defined diagnostic camera, not a recovered source camera; no lighting changes.
bpy.ops.object.camera_add(location=(0,-17,2.1));c=bpy.context.object;c.name='DIAG outer LED surface close';c.rotation_euler=(Vector((0,-10.5,.245))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=52
if candidate:
 mat=m.materials[0].copy();mat.name='Outer LED matrix author surface experiment';b=mat.node_tree.nodes.get('Principled BSDF');b.inputs['Emission Strength'].default_value=recipe['candidate_strength_luminance_matched'];m.materials.append(mat)
 for file,socket in [('outer-band-basecolor.png','Base Color'),('outer-band-emission.png','Emission Color')]:
  im=bpy.data.images.load(str(P/'textures-v2'/file),check_existing=False);im.colorspace_settings.name='sRGB';im.pack();tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;tex.interpolation='Linear';tex.extension='REPEAT';mat.node_tree.links.new(tex.outputs['Color'],b.inputs[socket])
 uv=m.uv_layers.new(name='OuterBand_Cylindrical_AuthorUV');chosen=[]
 for f in m.polygons:
  rr=[math.hypot(m.vertices[i].co.x,m.vertices[i].co.y) for i in f.vertices];zz=[m.vertices[i].co.z for i in f.vertices]
  if min(rr)>10.54 and max(zz)-min(zz)>.16:
   chosen.append(f.index);f.material_index=1;ii=[i%128 for i in f.vertices]
   for li,vi,idx in zip(f.loop_indices,f.vertices,ii):
    u=idx/128
    if 0 in ii and 127 in ii and idx==0:u=1.
    uv.data[li].uv=(u,(m.vertices[vi].co.z-.16)/.17)
 assert len(chosen)==128
else:chosen=[]
s.render.engine='CYCLES';s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100;s.cycles.samples=8;s.cycles.use_denoising=False
s.camera=bpy.data.objects['SOURCE11 conditional camera'];bpy.context.view_layer.update()
geo={}
for ob in s.objects:
 if ob.type=='MESH':
  payload={'vertices':[list(v.co) for v in ob.data.vertices],'polygons':[list(p.vertices) for p in ob.data.polygons],'matrix':[list(r) for r in ob.matrix_world]};geo[ob.name]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
record={'recipe_file_sha256':hashlib.sha256((P/'textures-v2/pattern-recipe.json').read_bytes()).hexdigest(),'actual_emission_strength':float(b.inputs['Emission Strength'].default_value) if candidate else 2.,'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'candidate':candidate,'mesh_geometry_hashes':geo,'modified_face_ids':chosen,'texture_recipe':recipe,'scope':'author surface pattern only; original positions/curvature/source failures persist; no physical LED count claim'}
if mode=='render':
 view=args[2];s.camera=c if view=='close' else bpy.data.objects['SOURCE11 conditional camera'];s.render.filepath=str(P/'renders'/f'{args[1]}-v3-{view}-8s.png');bpy.ops.render.render(write_still=True);record['camera']=s.camera.name;record['camera_matrix']=[list(r) for r in s.camera.matrix_world];record['image_sha256']=hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest();(P/'renders'/f'{args[1]}-v3-{view}-recipe.json').write_text(json.dumps(record,indent=2))
else:
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'export/roof-led-surface-v3.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'export/roof-led-surface-v3.glb'),export_format='GLB',export_cameras=True,export_extras=True)
 d=json.loads((P.parent/'cyber-roof-paired-shell-study-20261105/export/roof-paired-a055-recovery.json').read_text());d['source_blend']='roof-led-surface-v3.blend';d['glb']='roof-led-surface-v3.glb';d['render_products']={'scope':'LED surface experiment SOURCE FAILED; only material source11 and diagnostic close baseline/candidate 8samples','source10':'not rendered; target front band out of frame; no second-source validation','white':'technical shared geometry only; no white render','all_old_render_claims':'not current experiment imagery'};d['led_surface_experiment']=record;d['objects'].append({'name':c.name,'type':'CAMERA','matrix_world':[list(r) for r in c.matrix_world],'properties':{'purpose':'author diagnostic camera not source'},'camera':{k:getattr(c.data,k) for k in ['lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','type','clip_start','clip_end']}});(P/'export/roof-led-surface-v3-recovery.json').write_text(json.dumps(d,indent=2))
 w=bpy.data.materials.new('White LED surface technical');w.use_nodes=True;bs=w.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.66,.66,.66,1);bs.inputs['Roughness'].default_value=.7
 for ob in s.objects:
  if ob.type=='MESH':
   ob.data.materials.clear();ob.data.materials.append(w)
   for f in ob.data.polygons:f.material_index=0
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'export/roof-led-surface-v3-white.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'export/roof-led-surface-v3-white.glb'),export_format='GLB',export_cameras=True,export_extras=True)
 (P/'export/execution-record-v3.json').write_text(json.dumps(record,indent=2))
