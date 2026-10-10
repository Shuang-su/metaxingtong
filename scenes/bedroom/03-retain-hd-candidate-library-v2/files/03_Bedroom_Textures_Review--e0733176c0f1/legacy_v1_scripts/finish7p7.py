import bpy,json,hashlib,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;D=R/'final7p7';bpy.ops.wm.open_mainfile(filepath=str(D/'models/01_bedroom_material.blend'));s=bpy.context.scene;s.cycles.use_denoising=False
for key in ['BED_ASSUMPTIONS','SOURCE','EVIDENCE_LIMIT']:
 if key in s:del s[key]
t=bpy.data.texts.new('README_中文');t.write((R/'README_中文.txt').read_text())
def digest():
 h=hashlib.sha256()
 for o in sorted([o for o in s.objects if o.type=='MESH'],key=lambda o:o.name):
  h.update(o.name.encode());h.update(str(tuple(tuple(r) for r in o.matrix_world)).encode())
  for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
  for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 return h.hexdigest()
def export(name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in s.objects:
  if o.type in ['MESH','CAMERA']:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(D/'models'/name),export_format='GLB',use_selection=True,export_apply=True,export_cameras=True,export_extras=True)
a=digest();s.camera=bpy.data.objects['01_入口看床'];bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/01_bedroom_material.blend'),compress=True);export('03_bedroom_material.glb')
w=bpy.data.materials.new('统一中性白模');w.use_nodes=True;b=w.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.68,.68,.68,1);b.inputs['Roughness'].default_value=.8
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(w)
 if o.type=='LIGHT':o.data.color=(1,1,1)
for m in list(bpy.data.materials):
 if m.users==0:bpy.data.materials.remove(m)
for im in list(bpy.data.images):
 if im.users==0:bpy.data.images.remove(im)
b=digest();assert a==b
(D/'analysis/geometry_identity.json').write_text(json.dumps({'material_sha256':a,'white_sha256':b,'identical':a==b},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/02_bedroom_white.blend'),compress=True);export('04_bedroom_white.glb')
s.cycles.samples=12
for n,stem in [('01_入口看床','normal_white'),('MATCH_front_50m07_same_axis','source_front_white'),('MATCH_close_50m10_same_axis','source_close_white')]:
 s.camera=bpy.data.objects[n];s.render.resolution_x=1188 if 'source' in stem else 960;s.render.resolution_y=668 if 'source' in stem else 540;s.render.filepath=str(D/'renders'/(stem+'.png'));bpy.ops.render.render(write_still=True)
# Explicitly separate cutaway asset, NEVER used for ordinary or reference render.
bpy.ops.wm.open_mainfile(filepath=str(D/'models/01_bedroom_material.blend'));s=bpy.context.scene
for o in list(s.objects):
 if o.name=='实体天花_厚0.16' or '推定窗' in o.name or '推定门洞' in o.name or o.name.startswith('门墙踢脚线') or o.name.startswith('侧墙踢脚线'):
  bpy.data.objects.remove(o,do_unlink=True)
sh=bpy.data.objects['完整四墙_厚0.18_真实门窗洞']
for loc,dim in [((.2,-7.95,1.6),(9,1,4)),((-3.7,-3.8,1.6),(.6,9,4))]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);cut=bpy.context.object;cut.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);mod=sh.modifiers.new('独立剖切真实切除','BOOLEAN');mod.object=cut;mod.operation='DIFFERENCE';bpy.context.view_layer.objects.active=sh;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
s['VERSION']='独立剖切示意，仅审阅内部；不是完整房间模型';s.camera=bpy.data.objects['12_外壳完整'];s.camera.data.lens=40;s.render.filepath=str(D/'renders/13_独立剖切_不用于普通视角.png');s.cycles.samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/05_bedroom_CUTAWAY_INFERRED.blend'),compress=True);bpy.ops.render.render(write_still=True)
