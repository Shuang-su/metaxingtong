import bpy,bmesh,math,json,numpy as np
from mathutils import Vector
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
r=Path(__file__).resolve().parents[1];out=r/'qa/R08_trial';bpy.ops.wm.open_mainfile(filepath=str(r/'models/R08d_contacts_cloth_trial.blend'));s=bpy.context.scene
# Both observed left-eave soft correspondences, not an inferred hidden corner.
cs=[];ds=[]
for i,(u,v) in enumerate([(154,270),(674,150)],1):
 cam=bpy.data.objects[f'SOURCE_CONDITIONAL_{i}'];f=cam.data.lens*1920/cam.data.sensor_width;cs.append(np.array(cam.location));ds.append(np.array((cam.matrix_world.to_3x3()@Vector(((u-960)/f,(540-v)/f,-1))).normalized()))
A=np.column_stack((ds[0],-ds[1]));l=np.linalg.lstsq(A,cs[1]-cs[0],rcond=None)[0];points=[cs[i]+l[i]*ds[i] for i in [0,1]];new=Vector((points[0]+points[1])/2);old=Vector((-3.3,9.5,3.89));delta=new-old
for i in [0,5]:
 for prefix,N,M in [('T01_roof_panel_',14,12),('T01_skirt_panel_',16,16)]:
  o=bpy.data.objects[f'{prefix}{i:02}']
  for v in o.data.vertices:
   a,b=divmod(v.index,N+1);t=a/M;u=b/N;v.co+=delta*t*((1-u) if i==0 else u)
for i in [4,5]:
 o=bpy.data.objects[f'T01_roof_panel_{i:02}']
 for v in o.data.vertices:
  a,b=divmod(v.index,15);t=a/12;u=b/14;v.co.z-=.10*math.sin(math.pi*t)*(u if i==4 else 1-u)
upper=[new,Vector((-.5396,8.1541,3.8916)),None,None,None,Vector((-1.99651054,10.,5.49581436))]
for i,a,b in [(0,upper[0],upper[1]),(5,upper[5],upper[0])]:
 o=bpy.data.objects[f'T01_roof_hem_{i}'];o.location=(a+b)/2;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.dimensions.z=(b-a).length
# Right-only soft bag contraction: no claim about left hidden instance count.
def contract(x):return x-.45*max(0,min(1,(x+.55)/1.25))**1.2
for o in list(s.objects):
 if o.name.startswith('P02_'):
  if o.type=='MESH':
   for v in o.data.vertices:v.co.x=contract(v.co.x)
  elif o.type=='CURVE':
   for sp in o.data.splines:
    for pt in sp.points:
     pt.co.x=contract(pt.co.x)
     if o.name.startswith('P02_vertical_band'):pt.co.z=max(.022,pt.co.z)
 # Convert only added solid cords with existing caps, weld coincident cap/loop endpoint vertices; no fake closure.
 if o.type=='CURVE' and o.name.startswith(('P02_','C01_R08_')):
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
proj={}
for i in [1,2]:
 p=world_to_camera_view(s,bpy.data.objects[f'SOURCE_CONDITIONAL_{i}'],new);proj[str(i)]=[p.x*1920,(1-p.y)*1080]
(out/'R08e_report.json').write_text(json.dumps({'left_eave_working_xyz':list(new),'two_ray_separation':float(np.linalg.norm(points[0]-points[1])),'left_eave_native_projection':proj,'roof_arc':'shared edge inward Z sag amplitude .10 working units; conditional, not physical measured drape','bag':'right-only contraction max .45X preserves hidden left half; two-source visible right contour constraint, not unique full bag geometry','straps':'min centre .022 for radius .022; actual mesh check follows','unaccepted':True},indent=2));bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(r/'models/R08e_shared_edges_trial.blend'))
s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.use_denoising=False;s.cycles.samples=12;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=50
for role in ['materials','white']:
 if role=='white':
  m=bpy.data.materials.new('R08e_white');m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.65,.65,.65,1)
  for o in s.objects:
   if o.type in {'MESH','CURVE'}:o.data.materials.clear();o.data.materials.append(m)
 for i in [1,2]:s.camera=bpy.data.objects[f'SOURCE_CONDITIONAL_{i}'];s.render.filepath=str(out/f'R08e_source{i}_{role}_960.png');bpy.ops.render.render(write_still=True)
print('R08E_DONE')
