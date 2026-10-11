import bpy,sys,os,json,hashlib,bmesh
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/01_castle_hall_material.blend'));S=bpy.context.scene
# Bring near buffet in front of its column instead of occluding it behind the shaft.
for o in S.objects:
 if o.type=='MESH' and any(c.name[:2] in ['04','05','06','07'] for c in o.users_collection):
  ys=[v.co.y for v in o.data.vertices]
  if ys and -1.7<sum(ys)/len(ys)<2.3:
   for v in o.data.vertices:v.co.y-=2.1
# Clear unobserved end-window transoms (vertical divisions dominate the source).
for o in list(S.objects):
 if 'Central window horizontal frame' in o.name and o.data.vertices and min(v.co.z for v in o.data.vertices)>1:bpy.data.objects.remove(o,do_unlink=True)
for o in S.objects:
 if o.type=='LIGHT':
  o.data.energy*=.40
  if o.name.startswith('Blue night'):o.data.energy=240
S.view_settings.exposure=.05
m=bpy.data.materials['Night blue glazing'];p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.025,.068,.15,1);p.inputs['Roughness'].default_value=.85;p.inputs['Metallic'].default_value=0;p.inputs['Emission Strength'].default_value=.42
S.camera=bpy.data.objects['MATCH_A_45m15_empty_aisle'];S.camera.data.lens=44;S.camera.data.shift_y=-.045
# Remove zero-area faces at sphere poles; bake real edge/cloth geometry before export.
for o in list(S.objects):
 if o.type!='MESH':continue
 bpy.context.view_layer.objects.active=o
 for mod in list(o.modifiers):
  try:bpy.ops.object.modifier_apply(modifier=mod.name)
  except Exception:pass
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.00000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 o['reconstruction']='Approximate visible reference component; no source screenshot used as geometry texture.'
 if 'Inferred' in o.name:o['evidence']='off-camera extent inferred'
for im in bpy.data.images:
 if im.source=='FILE':im.filepath='//../textures/'+os.path.basename(im.filepath);im.pack()
S.render.resolution_percentage=65;S.cycles.samples=28
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/03_refined.blend'),compress=True)
S.render.filepath=str(R/'renders/refined_MATCH_A.png');bpy.ops.render.render(write_still=True)
print('REFINEMENT_DONE')
