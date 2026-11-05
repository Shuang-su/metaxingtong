import bpy,math,pathlib,json,hashlib
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parents[1];audit={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R04_{mode}.blend'));before=set(bpy.data.objects.keys());gold=bpy.data.materials['BRASS_proxy' if mode=='material' else 'WHITE_clay'];red=bpy.data.materials['GARMENT_red_proxy' if mode=='material' else 'WHITE_clay'];dark=bpy.data.materials['DARK_metal' if mode=='material' else 'WHITE_clay'];C=Vector((3.85,2.78,0))
 def finish(o,n,m):
  o.name='MANNEQUIN_'+n;o.data.materials.append(m);o['evidence']='Source011/012 visible gold head/neck/arm fragments, red clothing and dark belt. Relative scale/depth/back/pose inferred. No hidden feet/base invented; not source calibrated.'
  return o
 def sphere(n,loc,scale,m):
  bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=1,location=C+Vector(loc));o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  for f in o.data.polygons:f.use_smooth=True
  return finish(o,n,m)
 def rod(n,a,b,r,m):
  a=C+Vector(a);b=C+Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,n,m)
 def rings(n,profiles,m):
  vs=[];N=24
  for z,cx,rx,ry in profiles:
   for j in range(N):
    t=2*math.pi*j/N;vs.append(tuple(C+Vector((cx+rx*math.cos(t),ry*math.sin(t),z))))
  fs=[tuple(reversed(range(N)))];L=len(profiles)
  for k in range(L-1):
   for j in range(N):a=k*N+j;b=k*N+(j+1)%N;fs.append((a,b,b+N,a+N))
  fs.append(tuple((L-1)*N+j for j in range(N)));me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o)
  for f in me.polygons:f.use_smooth=len(f.vertices)==4
  return finish(o,n,m)
 rings('red_upper_clothing_proxy',[(1.13,0,.20,.105),(1.26,0,.15,.10),(1.49,0,.20,.12),(1.73,0,.23,.115),(1.81,0,.12,.09)],red)
 rings('dark_belt_proxy',[(1.245,0,.158,.108),(1.30,0,.17,.112)],dark)
 # Separate finite bifurcated lower garment: source does not establish dress pattern or hidden legs.
 for side in [-1,1]:
  rings(f'red_bifurcated_lower_proxy_{side}',[(.25,side*.115,.105,.115),(.42,side*.112,.105,.11),(.87,side*.105,.092,.10),(1.18,side*.103,.095,.10)],red)
 rod('neck_visible_proxy',(0,0,1.77),(0,0,1.98),.049,gold);sphere('head_without_facial_claim',(0,-.008,2.05),(.10,.085,.135),gold)
 for side in [-1,1]:
  shoulder=(side*.20,0,1.72);elbow=(side*.285,-.018,1.46);wrist=(side*.29,-.04,1.15)
  rod(f'red_short_sleeve_proxy_{side}',shoulder,(side*.26,-.012,1.53),.078,red)
  rod(f'upper_arm_pose_inferred_{side}',shoulder,elbow,.044,gold);sphere(f'elbow_join_inferred_{side}',elbow,(.046,.046,.046),gold);rod(f'forearm_visible_proxy_{side}',elbow,wrist,.033,gold);sphere(f'hand_fragment_proxy_{side}',(side*.29,-.045,1.115),(.039,.029,.067),gold)
 # One new diagnostic camera; existing four cameras, lights and background unchanged.
 d=bpy.data.cameras.new('MANNEQUIN_local');d.lens=50;o=bpy.data.objects.new('MANNEQUIN_local',d);bpy.context.collection.objects.link(o);o.location=(5.5,-1.8,2.5);o.rotation_euler=(Vector((3.3,2.75,1.2))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R05_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R05_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True)
 audit[mode]={'new_objects':sorted(set(bpy.data.objects.keys())-before),'model_sha256':hashlib.sha256((P/'models'/f'R05_{mode}.blend').read_bytes()).hexdigest(),'scope':'finite local prop proxy only; no floor/walls/ceiling, no mannequin feet/hidden stand, no source-camera calibration'}
(P/'qa/R05-added-proxy.json').write_text(json.dumps(audit,indent=2))
