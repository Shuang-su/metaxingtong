import bpy,json,os
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath='/workspace/shared/arcade-prop-local-20261030/models/arcade_prop_detail_R08_material.blend');s=bpy.context.scene

def signature(o):
 return {'matrix':[list(r) for r in o.matrix_world],'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons]}
before={o.name:signature(o) for o in s.objects if o.type=='MESH'}
fixed={o.name:{'matrix':[list(r)for r in o.matrix_world],'type':o.type,'lens':o.data.lens if o.type=='CAMERA' else None,'energy':o.data.energy if o.type=='LIGHT' else None} for o in s.objects if o.type in ['CAMERA','LIGHT']}
allowed=[];removed=[];added=[]
m=bpy.data.materials.new('R09 incomplete graphic placeholder NOT source texture');m.diffuse_color=(.035,.045,.06,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.035,.045,.06,1)
for i in range(1,4):
 p=f'M{i:02d}'
 for suffix in ['header','header_blue']:
  o=bpy.data.objects[p+'_'+suffix];allowed.append(o.name)
  bottom=o.location.z-o.dimensions.z/2;o.dimensions.z=1.02 if suffix=='header' else .98;o.location.z=bottom+o.dimensions.z/2
  o['certainty']='Observed taller graphic board region; height and clipped top/back closure are inferred working dimensions, NOT complete silhouette'
  if suffix=='header_blue':o.data.materials.clear();o.data.materials.append(m);o['graphic_status']='UNFINISHED: no clean complete source graphic; no fabricated lettering or live foreground figure baked'
 o=bpy.data.objects[p+'_header_logo'];removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
 for side,suf in [('L',''),('R','.002')]:
  for part in ['outer','cone','dome']:
   old=bpy.data.objects[p+'_speaker_'+part+suf];assert old.location.z>3
   new=old.copy();new.data=old.data.copy();new.name=p+'_HEADER_upper_'+side+'_'+part;s.collection.objects.link(new);new.location.z+=.46;new['evidence']='Second circular unit on each side directly visible in 2026 low-angle source; physical separation/radius ratio inferred';added.append(new.name)
bpy.context.view_layer.update()
changed=[n for n in before if n not in removed and before[n]!=signature(bpy.data.objects[n])];assert set(changed)==set(allowed),(changed,allowed)
for n,v in fixed.items():
 o=bpy.data.objects[n];assert v=={'matrix':[list(r)for r in o.matrix_world],'type':o.type,'lens':o.data.lens if o.type=='CAMERA' else None,'energy':o.data.energy if o.type=='LIGHT' else None}
for name,loc,target in [('HEADER_FRONT',(0,-4.4,3.48),(0,0,3.35)),('HEADER_OBLIQUE',(-2.6,-4.4,3.6),(0,0,3.35))]:
 d=bpy.data.cameras.new(name);d.lens=55;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o['scope']='Unregistered inspection camera, NOT source camera'
s.render.engine='CYCLES';s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=960;s.render.resolution_y=720;s.render.resolution_percentage=100;s.cycles.samples=24;s.camera=bpy.data.objects['HEADER_FRONT'];s['R09_scope']='Header circular-unit count and taller unfinished board only. Whole scene NOT accepted. Top/back/dimensions inferred.'
(D/'qa/scope.json').write_text(json.dumps({'baseline':'R08 46107bfa360dbbbbf3ecafff8ec305fdc5bfee75','changed_meshes':changed,'removed':removed,'added':added,'unchanged_mesh_count':len(before)-len(removed)-len(changed),'original_cameras_lights_unchanged':True,'source_texture':'none; visible design remains UNFINISHED','height_working':1.02,'upper_row_separation_working':.46},indent=2))
a={o.name:signature(o)for o in s.objects if o.type=='MESH'}
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/arcade_header_R09_material.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'models/arcade_header_R09_material.glb'),export_format='GLB',export_cameras=True,export_lights=True)
w=bpy.data.materials.new('R09 same geometry white');w.use_nodes=True;w.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.62,.62,.62,1)
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(w)
assert a=={o.name:signature(o)for o in s.objects if o.type=='MESH'}
(D/'qa/shared_geometry.json').write_text(json.dumps({'exact_world_vertices_topology':True,'mesh_count':len(a)}))
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/arcade_header_R09_white.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'models/arcade_header_R09_white.glb'),export_format='GLB',export_cameras=True,export_lights=True)
