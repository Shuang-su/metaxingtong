import bpy,math,pathlib,json
from mathutils import Vector
from math import sin,cos,pi
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/lakeleaf-r04-material.blend'));s=bpy.context.scene

def point(u,v):
 width=1.58*max(0,1-u*u)**.72*(1+.06*sin(3*pi*u));x=4.65*u;y=width*v;end=(2.30 if u<0 else 1.65)*abs(u)**3
 z=.20+end+.75*v*v*(1-abs(u)**1.1)+.045*sin(8*pi*u+v*.8)*abs(v)**3*max(0,1-u*u)
 return (x,y,z)
rows=[]
for sign in [-1,1]:
 name='LEAF_003_Branch_00_'+('L' if sign<0 else 'R');o=bpy.data.objects[name];pts=[];r=[]
 for j in range(31):
  t=j/30;u0=-.70;travel=min(.32,u0+.96);u=u0-travel*(.78*t+.22*t*t);v=sign*.90*sin(t*pi/2);p=list(point(u,v));p[2]+=.018;pts.append(p);r.append(.003+.019*(1-t)**1.2)
 vs=[];fs=[];sides=6
 for i,p in enumerate(pts):
  p=Vector(p);a=(Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)])).normalized();b=a.cross(Vector((0,0,1)))
  if b.length<.01:b=a.cross(Vector((0,1,0)))
  b.normalize();c=a.cross(b).normalized()
  for j in range(sides):vs.append(tuple(p+r[i]*(b*cos(j*2*pi/sides)+c*sin(j*2*pi/sides))))
 for i in range(len(pts)-1):
  for j in range(sides):fs.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
 fs += [tuple(reversed(tuple(range(sides)))),tuple((len(pts)-1)*sides+j for j in range(sides))]
 old=o.data;m=bpy.data.meshes.new(name+'_r05_repaired_mesh');m.from_pydata(vs,[],fs);m.materials.append(old.materials[0]);m.update();o.data=m
 for p in m.polygons:p.use_smooth=True
 o['repair']='R05 first branch pair limited to u>=-0.96; R04 exceeded shell parameter u=-1.02 and made an erroneous external spike.'
 rows.append({'id':name,'old_u_end':-1.02,'new_u_end':-.96,'centerline_model_coordinates':pts,'object_transform':[list(row) for row in o.matrix_world]})
s['R05_changes']='Only first leaf secondary-vein pair shortened within shell domain; no shell/shore/material/lighting/camera change. R04 source images retained as failed-stage evidence.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/lakeleaf-r05-material.blend'));bpy.ops.export_scene.gltf(filepath=str(R/'models/lakeleaf-r05.glb'),export_format='GLB',export_cameras=True,export_lights=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT')
w=bpy.data.materials.new('WHITE_R05_DiagnosticOnly');w.use_nodes=True;p=w.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.66,.67,.64,1);p.inputs['Roughness'].default_value=.75
for o in s.objects:
 if o.type=='MESH':
  for k in range(len(o.data.materials)):o.data.materials[k]=w
s['white_model_note']='Same R05 geometry/transforms/cameras; material-only diagnostic replacement.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/lakeleaf-r05-white.blend'))
(R/'qa/r05').mkdir(exist_ok=True,parents=True);(R/'qa/r05/vein-repair.json').write_text(json.dumps({'cause':'Actual R04 native-size oblique render exposed parametrically overlong first branch pair. Failed images and models preserved.','rows':rows},indent=2)+'\n')
