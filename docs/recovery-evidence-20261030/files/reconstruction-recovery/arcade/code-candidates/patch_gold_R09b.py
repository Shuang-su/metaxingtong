import bpy,json,math
from mathutils import Vector
from pathlib import Path
D=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(D/'models/arcade_header_R09_material.blend'));s=bpy.context.scene

def sig(o):return {'matrix':[list(r)for r in o.matrix_world],'verts':[list(v.co)for v in o.data.vertices],'polys':[list(p.vertices)for p in o.data.polygons]}
a={o.name:sig(o)for o in s.objects if o.type=='MESH'};allowed=[];new=[]
gold=bpy.data.materials.new('Observed printed gold circles NOT raised balls');gold.use_nodes=True;bs=gold.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.68,.28,.055,1);bs.inputs['Roughness'].default_value=.48
points=json.load(open(D/'qa/gold_layout_conditional.json'))['points']
for i,cx in enumerate([-3.35,0,3.35],1):
 p=f'M{i:02d}'
 for suffix in ['header','header_blue']:
  o=bpy.data.objects[p+'_'+suffix];bottom=o.location.z-o.dimensions.z/2;top=4.47 if suffix=='header' else 4.45;height=top-bottom;o.dimensions.z=height;o.location.z=bottom+height/2;allowed.append(o.name);o['certainty']='Extended only to contain observed gold dots; actual top above image remains unknown. Flat top/back technical closure inferred.'
 for q in points:
  # Planar disk at the observed red front face, 0.0005 working units offset to avoid z fighting. No spherical relief.
  r=q['radius_working'];verts=[(cx+q['x']+r*math.cos(k*2*math.pi/64),-.1055,q['z']+r*math.sin(k*2*math.pi/64))for k in range(64)];me=bpy.data.meshes.new(p+'_gold_dot_'+q['id']);me.from_pydata(verts,[],[list(range(64))]);me.update();o=bpy.data.objects.new(p+'_HEADER_printed_gold_'+q['id'],me);s.collection.objects.link(o);o.data.materials.append(gold);o['evidence']='Only directly visible source dots: left five right two. Unknown off-frame continuation omitted.';o['mapping']='Conditional local homography via speaker centers, not calibrated source camera or measured physical metric.';new.append(o.name)
bpy.context.view_layer.update();changed=[n for n in a if a[n]!=sig(bpy.data.objects[n])];assert set(changed)==set(allowed)
# Add new inspection cameras; all existing source/inspection cameras remain unchanged.
for name,loc in [('HEADER_B_FRONT',(0,-5.0,3.74)),('HEADER_B_OBLIQUE',(-2.8,-5.0,3.95))]:
 d=bpy.data.cameras.new(name);d.lens=55;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,3.65))-o.location).to_track_quat('-Z','Y').to_euler();o['scope']='New inspection camera only; not registered'
s.camera=bpy.data.objects['HEADER_B_FRONT'];s['R09b_scope']='Same header phase supplement: seven visible printed gold dots, no guessed continuation, plate height covering these observations, central graphic unfinished'
(D/'qa/gold_patch_scope.json').write_text(json.dumps({'modified':changed,'added':new,'unchanged_previous_mesh_count':len(a)-len(changed),'dot_geometry':'flat polygon y=-.1055, no thickness or bulge','red_front_y':-.105,'top_inferred':4.47,'source_off_frame_dots':'not filled or mirrored'},indent=2))
b={o.name:sig(o)for o in s.objects if o.type=='MESH'}
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/arcade_header_R09b_material.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'models/arcade_header_R09b_material.glb'),export_format='GLB',export_cameras=True,export_lights=True)
w=bpy.data.materials.new('R09b shared white');w.use_nodes=True;w.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.62,.62,.62,1)
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(w)
assert b=={o.name:sig(o)for o in s.objects if o.type=='MESH'}
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/arcade_header_R09b_white.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'models/arcade_header_R09b_white.glb'),export_format='GLB',export_cameras=True,export_lights=True)
