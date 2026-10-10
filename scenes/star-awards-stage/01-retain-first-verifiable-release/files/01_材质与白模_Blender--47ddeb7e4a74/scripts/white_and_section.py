import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Star_Awards_Candidate.blend'))
sc=bpy.context.scene

def geomhash():
 h=hashlib.sha256()
 for o in sorted((o for o in sc.objects if o.type=='MESH'),key=lambda o:o.name):
  h.update(o.name.encode());h.update(str([tuple(round(float(t),7)for t in v.co)for v in o.data.vertices]).encode());h.update(str([tuple(p.vertices)for p in o.data.polygons]).encode());h.update(str([list(r)for r in o.matrix_world]).encode())
 return h.hexdigest()
before=geomhash();m=bpy.data.materials.new('统一中性白模');m.diffuse_color=(.7,.7,.7,1);m.use_nodes=True;pr=m.node_tree.nodes.get('Principled BSDF');pr.inputs['Base Color'].default_value=(.7,.7,.7,1);pr.inputs['Roughness'].default_value=.8
for o in sc.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(m)
for o in sc.objects:
 if o.type=='LIGHT':o.data.color=(1,1,1)
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.4,.4,.4,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Star_Awards_White.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'Star_Awards_White.glb'),export_format='GLB',export_apply=True,export_cameras=True,export_lights=False)
(P/'qa/white_geometry_identity.json').write_text(json.dumps({'main_geometry_hash':before,'white_geometry_hash':geomhash(),'equal':before==geomhash(),'main_source_sha256':hashlib.sha256((P/'Star_Awards_Candidate.blend').read_bytes()).hexdigest()},indent=2))
# Explicit derived section only. Main delivered geometry and visibility are untouched.
cutmat=bpy.data.materials.new('剖切截面暖橙');cutmat.diffuse_color=(.65,.22,.07,1);cutmat.use_nodes=True;cutmat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.65,.22,.07,1)
removed=[]
for o in list(sc.objects):
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world)
 res=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=Vector((.10,0,0)),plane_no=Vector((1,0,0)),clear_outer=True,clear_inner=False)
 cutedges=[e for e in bm.edges if e.is_boundary and abs(e.verts[0].co.x-.1)<1e-5 and abs(e.verts[1].co.x-.1)<1e-5]
 o.data.materials.append(cutmat)
 if cutedges:
  r=bmesh.ops.holes_fill(bm,edges=cutedges,sides=0)
  for f in r.get('faces',[]):f.material_index=1
 bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.transform(o.matrix_world.inverted());bm.to_mesh(o.data);bm.free()
 if not len(o.data.polygons):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
cam=bpy.data.cameras.new('显式剖切相机');co=bpy.data.objects.new('显式剖切相机',cam);sc.collection.objects.link(co);co.location=(10,-12,8);co.rotation_euler=(Vector((0,-.7,2.5))-co.location).to_track_quat('-Z','Y').to_euler();cam.lens=32;sc.camera=co
sc['section_note']='显式几何剖切 x=0.10，仅用于查看连接；不属于完整原模型。原模型没有按相机隐藏对象。'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'qa/Cutaway_Inspection.blend'))
sc.cycles.samples=16;sc.cycles.use_denoising=False;sc.render.resolution_x=1000;sc.render.resolution_y=700;sc.render.resolution_percentage=100;sc.render.threads=2;sc.render.filepath=str(P/'renders/显式剖切_检查.png');bpy.ops.render.render(write_still=True)
