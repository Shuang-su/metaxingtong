import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1];out=r/'versions/R01D';out.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(r/'versions/R01C/ring-remake-R01C-shared-candidate.blend'));s=bpy.context.scene;changes=[]
for o in s.objects:
 if o.type!='MESH':continue
 if o.name.startswith('SIDE_MAIN_') and o.name.endswith('_EDGE'):
  side=-1 if '_-1_' in o.name else 1;center=Vector((side*8.1,1.3,.05));beta=math.radians(side*-15);u=Vector((math.cos(beta),math.sin(beta),0));v=Vector((0,0,1))
  for p in o.data.vertices:
   d=p.co-center;rad=u*d.dot(u)+v*d.dot(v);p.co+=rad.normalized()*.012
  changes.append({'object':o.name,'change':'edge radial +.012 to remove coincident exterior faces; intentional fitted trim remains partly embedded'})
 bm=bmesh.new();bm.from_mesh(o.data);vol=bm.calc_volume(signed=True)
 if vol<0:
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);changes.append({'object':o.name,'change':'face winding only','prior_signed_volume':vol})
 bm.free();o.data.update()
# Eight visible structural diagnostics, no hidden objects or clipping planes.
checks=[('01',(0,-30,17)),('02',(24,-22,20)),('03',(-24,-22,20)),('04',(0,23,31)),('05',(25,10,28)),('06',(-25,10,28)),('07',(0,0,38)),('08',(0,-32,8))]
for name,loc in checks:
 d=bpy.data.cameras.new('CHECK_'+name);o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,2,5))-o.location).to_track_quat('-Z','Y').to_euler();d.lens=28;d.clip_end=200
s.camera=bpy.data.objects['C_4K_CONDITIONAL'];s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.samples=32;s.cycles.use_denoising=False;s['stage_status']='R01D technical repair of declared candidate, SOURCE NOT ACCEPTED';s['render_config']='Cycles CPU 2 threads 32 samples no denoiser, fixed shared lighting across all sources';s['technical_changes']='23 reversed closed objects corrected; two edge trims radial+.012 only; all camera hypotheses unchanged'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ring-remake-R01D-material.blend'));bpy.ops.export_scene.gltf(filepath=str(out/'ring-remake-R01D-material.glb'),export_format='GLB')
# Actual shared-geometry white render original, then actual gray-slot export copy.
m=bpy.data.materials.new('R01D_actual_gray');m.use_nodes=True;m.diffuse_color=(.65,.65,.65,1);b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.65,.65,.65,1);b.inputs['Roughness'].default_value=.7;b.inputs['Metallic'].default_value=0;m.use_fake_user=True;s.view_layers[0].material_override=m;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ring-remake-R01D-white-same-geometry.blend'))
s.view_layers[0].material_override=None
for o in s.objects:
 if o.type=='MESH':
  o.data.materials.clear();o.data.materials.append(m)
  for p in o.data.polygons:p.material_index=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ring-remake-R01D-white-export-slots.blend'));bpy.ops.export_scene.gltf(filepath=str(out/'ring-remake-R01D-white.glb'),export_format='GLB')
(r/'qa/R01D-technical-scope.json').write_text(json.dumps({'changes':changes,'unchanged':'All main structure vertices except two trim offsets; object transforms, source cameras, lights, base counts and unknown supports unchanged','source_status':'Not accepted; geometry/source/whole-contact verification separate','check_cameras':[n for n,p in checks]},indent=2));print('SAVED R01D')
