import bpy,math,json,bmesh
from mathutils import Vector
from pathlib import Path
r=Path(__file__).resolve().parents[1];out=r/'qa/R08_trial';bpy.ops.wm.open_mainfile(filepath=str(r/'models/R08c_bag_trial.blend'));s=bpy.context.scene
# R08c failed occlusion: bag front crossed standing crate. Shift entire hypothetical bag behind it.
for o in s.objects:
 if o.name.startswith('P02_'):o.location.y+=.66
# Replace provisional band profiles by true superellipsoid cross-sections, avoiding floating seams.
cx,cy=-.55,6.65;wx,dy,h=2.5,.72,1.18;p=.55
sp=lambda x:math.copysign(abs(x)**p,x)
for o in s.objects:
 if o.name.startswith('P02_vertical_band_'):
  x=float(o.name.split('_')[-1]);factor=(1-(abs(x)/(wx/2))**(2/p))**(p/2)
  for k,pt in enumerate(o.data.splines[0].points):
   q=math.tau*k/64;pt.co=(cx+x,5.99+(dy/2*factor+.006)*sp(math.cos(q)),max(.008,h/2-.025+h/2*factor*sp(math.sin(q))),1)
 if o.name.startswith('P02_horizontal_seam_'):
  z=float(o.name.split('_')[-1]);factor=(1-abs((z+.025-h/2)/(h/2))**(2/p))**(p/2)
  for k,pt in enumerate(o.data.splines[0].points):
   q=math.tau*k/64;pt.co=(cx+(wx/2*factor+.004)*sp(math.cos(q)),5.99+(dy/2*factor+.004)*sp(math.sin(q)),z,1)
o=bpy.data.objects['P02_one_horizontal_bag_HYPOTHESIS'];bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
# Same cloth topology and support corners, centre top and front lip now sag.
o=bpy.data.objects['C01_sling_fabric']
for v in o.data.vertices:
 a,b=divmod(v.index,19);t=a/18;u=b/18;v.co.z-=math.sin(math.pi*u)*(.075*(1-t)**3+.09*t**3)
# Side seams unchanged because sin(pi*u)=0 on both side attachment curves.
(out/'R08d_report.json').write_text(json.dumps({'R08c_failure':'bag crossed foreground standing crate; not accepted. Entire bag moved +.66Y behind crate, source camera unchanged.','bag_body_front_y':cy-dy/2,'bag_ground_z':0,'bands':'cross-section surface profiles, thin offset for visibility; hidden rear inferred','chair':'same topology, top-middle -.075 and front-middle -.09, both side support corners unchanged','unaccepted':True},indent=2));bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(r/'models/R08d_contacts_cloth_trial.blend'))
s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.use_denoising=False;s.cycles.samples=8;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=50
for role in ['materials','white']:
 if role=='white':
  m=bpy.data.materials.new('R08d_white');m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.65,.65,.65,1)
  for o in s.objects:
   if o.type in {'MESH','CURVE'}:o.data.materials.clear();o.data.materials.append(m)
 for i in [1,2]:s.camera=bpy.data.objects[f'SOURCE_CONDITIONAL_{i}'];s.render.filepath=str(out/f'R08d_source{i}_{role}_960.png');bpy.ops.render.render(write_still=True)
print('R08D_DONE')
