import bpy,json,hashlib,struct,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=Path('/workspace/scratch/fa58bfcf0425/classroom_hd_alignment_20261010');s=bpy.context.scene
# Fixed content hash excludes camera and renderer settings; covers all mesh data/transforms/material graphs and collection visibility.
def state():
 h=hashlib.sha256()
 for o in sorted(bpy.data.objects,key=lambda a:a.name):
  if o.type=='CAMERA':continue
  h.update(str((o.name,o.type,tuple(v for row in o.matrix_world for v in row),o.hide_render)).encode())
  if o.type=='MESH':
   for v in o.data.vertices:h.update(struct.pack('fff',*v.co))
   for f in o.data.polygons:h.update(str((tuple(f.vertices),f.material_index)).encode())
   h.update(str([m.name if m else None for m in o.data.materials]).encode())
 for c in sorted(bpy.data.collections,key=lambda a:a.name):h.update(str((c.name,c.hide_render)).encode())
 for m in sorted(bpy.data.materials,key=lambda a:a.name):
  h.update(str((m.name,tuple(m.diffuse_color),m.use_nodes)).encode())
  if m.use_nodes:
   for n in sorted(m.node_tree.nodes,key=lambda a:a.name):
    h.update(str((n.name,n.bl_idname,[(i.name,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')])).encode())
   h.update(str([(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]).encode())
 return h.hexdigest()
before=state();f=json.loads((p/'qa/motion_camera_fit.json').read_text());mapping=[('classroom_0919_front','SOURCE_A'),('classroom_2123_key','SOURCE_B'),('classroom_4284_wide','SOURCE_C'),('classroom_5447_key','SOURCE_D')];manifest=[]
for name,old in mapping:
 o=bpy.data.objects[old].copy();o.data=o.data.copy();o.name='HD_'+name;s.collection.objects.link(o);manifest.append({'source':name,'camera':o.name,'inherited_camera':old,'matrix_world':[list(x) for x in o.matrix_world],'lens_mm':o.data.lens,'shift':[o.data.shift_x,o.data.shift_y]})
o=bpy.data.objects.new('HD_classroom_motion_4282',bpy.data.cameras.new('HD motion camera'));s.collection.objects.link(o);o.location=f['camera_location'];o.rotation_euler=f['camera_rotation_xyz'];o.data.lens=f['lens_mm'];o.data.sensor_width=36;bpy.context.view_layer.update();manifest.append({'source':'classroom_motion_4282','camera':o.name,'camera_only_fit':'qa/motion_camera_fit.json','matrix_world':[list(x) for x in o.matrix_world],'lens_mm':o.data.lens,'shift':[0,0]})
s.camera=o;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=1180;s.render.resolution_y=664;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
bpy.ops.wm.save_as_mainfile(filepath=str(p/'Classroom_HD_Evidence_REVIEW.blend'),compress=True)
(p/'qa/camera_reference_manifest.json').write_text(json.dumps(manifest,indent=2));(p/'qa/shared_state_hash.json').write_text(json.dumps({'before':before,'after':state(),'equal':before==state(),'scope':'All noncamera geometry, transforms, render visibility, material slots and node input/link graph. No geometry or material edits.'},indent=2))
s.render.filepath=str(p/'renders/classroom_motion_4282.png');bpy.ops.render.render(write_still=True)
# Desktop visibility: primary-ray technical test on unchanged opaque meshes, pixel centers, no ID material changes. \n
visible=set()
def walk(col,hidden=False):
 hidden=hidden or col.hide_render
 if not hidden:
  for x in col.objects:
   if not x.hide_render:visible.add(x.name)
 for c in col.children:walk(c,hidden)
walk(s.collection);deps=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];owners=[]
for ob in s.objects:
 if ob.type!='MESH' or ob.name not in visible:continue
 ev=ob.evaluated_get(deps);mesh=ev.to_mesh();offset=len(verts);verts.extend([ob.matrix_world@v.co for v in mesh.vertices]);faces.extend([tuple(offset+i for i in f.vertices) for f in mesh.polygons]);owners.extend([ob.name]*len(mesh.polygons));ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=False);cam=bpy.data.objects['SOURCE_D'];origin=cam.matrix_world.translation;rot=cam.matrix_world.to_3x3();W,H=1180,664;fl=cam.data.lens/cam.data.sensor_width*W;desks=sorted(n for n in visible if 'rounded oak desktop' in n and not n.startswith('Observed_front'));counts={n:0 for n in desks};ids={n:i+1 for i,n in enumerate(desks)};pixels=[0.0]*(W*H*4)
for y in range(H):
 for x in range(W):
  ray=rot@Vector(((x+.5-W/2)/fl,(H/2-y-.5)/fl,-1));hit=bvh.ray_cast(origin,ray.normalized())
  if hit[2] is not None:
   n=owners[hit[2]]
   if n in counts:
    counts[n]+=1;i=ids[n];color=((i*.618033)%1,(i*.381967+.2)%1,(i*.27321+.4)%1);base=((H-1-y)*W+x)*4;pixels[base:base+4]=[*color,1]
img=bpy.data.images.new('D desktop technical primary rays',width=W,height=H);img.pixels=pixels;img.filepath_raw=str(p/'qa/D_desktop_ids.png');img.file_format='PNG';img.save()
(p/'qa/D_desktop_visibility.json').write_text(json.dumps({'method':'Native1180x664 pixel-center primary rays against evaluated, render-visible shared meshes; glass treated as opaque, but student tabletop region contains no interposed glass. Not a beauty render.','total_student_desktops':len(desks),'visible_over_20px':sum(v>20 for v in counts.values()),'pixel_counts':counts,'ids':ids},indent=2));print('AUDIT FINISHED')
