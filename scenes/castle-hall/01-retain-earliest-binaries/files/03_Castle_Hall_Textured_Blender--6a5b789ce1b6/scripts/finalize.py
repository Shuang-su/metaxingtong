import bpy,json,hashlib,os
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/04_refined_v2.blend'));S=bpy.context.scene
# Keep exported PBR simple: bake mauve tint into authored base-color image.
m=bpy.data.materials['RoseStone | original UV PBR'];p=m.node_tree.nodes.get('Principled BSDF')
for n in list(m.node_tree.nodes):
 if n.type=='MIX_RGB':m.node_tree.nodes.remove(n)
for n in m.node_tree.nodes:
 if n.type=='TEX_IMAGE' and n.image and 'BaseColor' in n.image.name:m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
for im in bpy.data.images:
 if im.name.startswith('RoseStone_BaseColor'):
  im.filepath=str(R/'textures/RoseStone_BaseColor.png');im.reload();im.pack()
# Source balustrade is visible on the near side of the nighttime glazing.
for o in S.objects:
 if o.type=='MESH' and o.name.startswith('Balcony'):
  for v in o.data.vertices:v.co.y-=.55
 if o.type=='MESH' and o.name.startswith('Outside dim light'):
  for v in o.data.vertices:v.co.y-=.18
# Near dessert tiers and gifts are smaller in the source than the first blocking pass.
for o in S.objects:
 if o.type!='MESH' or not o.data.vertices:continue
 cx=sum(v.co.x for v in o.data.vertices)/len(o.data.vertices);cy=sum(v.co.y for v in o.data.vertices)/len(o.data.vertices)
 if abs(cx)>2 and cy<1.3 and any(t in o.name.lower() for t in ['cake','icing','candle flame']):
  for v in o.data.vertices:
   v.co.z=1.028+(v.co.z-1.028)*.39
   anchor=2.88 if cx>0 else -2.88
   v.co.x=anchor+(v.co.x-anchor)*.55
   v.co.y=-1.2+(v.co.y+1.2)*.55
 if cy<1 and any(t in o.name.lower() for t in ['gift','wrapped']):
  for v in o.data.vertices:v.co.y+=2.1
 if abs(cx)>2 and cy<1 and any(t in o.name.lower() for t in ['pink balloon','balloon knot','balloon hanging']):
  for v in o.data.vertices:
   anchor=3.1 if cx>0 else -3.1
   shift=.9 if cx>0 else -.9
   v.co.x=anchor+(v.co.x-shift-anchor)*.5
   v.co.y=-.88+(v.co.y+.88)*.5
   v.co.z=1.028+(v.co.z-1.028)*.38
for name in ['Octagonal polished ivory floor tiles','Dark marble diamond inlay']:
 for uv in bpy.data.objects[name].data.uv_layers.active.data:uv.uv*=.42
S.render.resolution_percentage=100;S.cycles.samples=48;S.render.threads=5
# Match B is a source-constrained oblique camera; manually aligned, not calibrated.
c=bpy.data.objects['MATCH_B_75m07_oblique'];c.data.lens=38;c.data.shift_y=-.02;c.rotation_euler=(Vector((3.0,18,1.45))-c.location).to_track_quat('-Z','Y').to_euler()
S['Evidence']='2023-11-10 BV1aw411T7ws; primary 00:45:15 and 01:15:07; arch/detail cross-check 01:13:44. Manual approximation, not recovered original assets.'
S['Excluded']='Characters, player UI, garden, unknown rear wall and ceiling omitted.'
def stats():
 obs=[o for o in S.objects if o.type=='MESH'];tri=[];vs=0;bad=0
 for o in obs:
  o.data.calc_loop_triangles();vs+=len(o.data.vertices)
  for t in o.data.loop_triangles:
   p=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
   if (p[1]-p[0]).cross(p[2]-p[0]).length<1e-12:bad+=1
   tri.append(sorted(tuple(round(x,4) for x in v) for v in p))
 return {'mesh_objects':len(obs),'vertices':vs,'triangles':len(tri),'degenerate_triangles':bad,'world_triangle_coordinate_sha256':hashlib.sha256(repr(sorted(tri)).encode()).hexdigest(),'all_meshes_have_uv':all(bool(o.data.uv_layers) for o in obs)}
def export(v):
 bpy.ops.object.select_all(action='DESELECT')
 for o in S.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(R/'models'/f'Xingtong_Castle_Hall_{v}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_extras=True,export_cameras=False,export_lights=False)
 bpy.ops.object.select_all(action='DESELECT')
def save(v):
 S.camera=bpy.data.objects['QA_WIDE_LEVEL_FRONT'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'models'/f'Xingtong_Castle_Hall_{v}.blend'),compress=True);json.dump(stats(),open(R/'qa'/f'blender_{v.lower()}_geometry.json','w'),indent=2);export(v)
def render(v):
 for label,cam in [('Match_A','MATCH_A_45m15_empty_aisle'),('Panorama','QA_WIDE_LEVEL_FRONT'),('Match_B','MATCH_B_75m07_oblique'),('Side','QA_SIDE_LEVEL')]:
  S.camera=bpy.data.objects[cam];S.render.filepath=str(R/'renders'/f'Final_{v}_{label}.png');bpy.ops.render.render(write_still=True)
save('Textured');render('Textured')
w=bpy.data.materials.new('Neutral white clay');w.use_nodes=True;p=w.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.72,.72,.72,1);p.inputs['Roughness'].default_value=.75
for o in S.objects:
 if o.type=='MESH':
  o.data.materials.clear();o.data.materials.append(w)
  for p in o.data.polygons:p.material_index=0
 elif o.type=='LIGHT':o.data.color=(1,1,1)
S.world.node_tree.nodes['Background'].inputs[0].default_value=(.4,.4,.4,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.5
save('White');render('White');print('FINAL_DONE')
