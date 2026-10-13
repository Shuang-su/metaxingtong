import os
import bpy,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
r=Path(__file__).parent;base=Path(os.environ.get('HOSPITAL_B_BASELINE',str(r.parent/'candidate_b/hospital_endboard_shape_B.blend')));roundbase=Path(os.environ.get('HOSPITAL_C_RECESS',str(r.parent/'candidate_c_outline/hospital_recess_outline_C.blend')))
bpy.ops.wm.open_mainfile(filepath=str(roundbase));s=bpy.context.scene
fit=json.load(open(r/'joint_fit_d2_result.json'));q=np.array(fit['params']);changes=[]
for o in s.objects:
 if o.type!='MESH':continue
 n=o.name;changed=False;inv=o.matrix_world.inverted();p=np.array([o.matrix_world@v.co for v in o.data.vertices])
 if n.startswith('Window_') or n.startswith('Window •') or n.startswith('ROOM_SHELL'):
  if n.startswith('ROOM_SHELL'):p[p[:,1]>.0001,1]*=.12
  else:p[:,1]*=.12
  if '__jamb_with_reveal' in n:
   cx=float(p[:,0].mean());anchors=[-1.60361624,0.,1.5,3.57642221,4.99425650];near=min(anchors,key=lambda a:abs(a-cx));newc=near if abs(near-cx)<.065 else cx;p[:,0]=newc+(p[:,0]-cx)*.34
  if '__closed_glass_solid' in n:
   idx=int(n.split('_')[1]);limits={1:(-1.57861624,-.025),2:(.025,.9906562),3:(1.525,3.5514222),4:(3.6014222,4.9692565)};a,b=limits[idx];vmin=p[:,0].min();vmax=p[:,0].max();p[:,0]=a+(p[:,0]-vmin)/(vmax-vmin)*(b-a)
  changed=True
 if n.startswith('Bed'):
  is_board=any(t in n for t in ['endboard','Bed end']);yy=p[:,1]+1.73290586;xx=p[:,0]-3.8301885;u=np.clip(abs(yy)/1.1375,0,1)
  if is_board:
   t=np.clip((p[:,2]-.15125)/(.82125-.15125),0,1);p[:,2]+=q[27]*4*t*(1-t)
   if 'endboard' in n:p[:,2]-=q[26]*u*u*np.clip((p[:,2]-.61)/(.82125-.61),0,1)
   p[:,2]*=math.exp(q[21])
  else:p[:,2]*=math.exp(q[25])
  yy*=math.exp(q[20])
  if not is_board:yy*=math.exp(q[29]);xx*=math.exp(q[30])
  a=q[28];p[:,0]=3.8301885+xx*math.cos(a)-yy*math.sin(a)+q[18];p[:,1]=-1.73290586+xx*math.sin(a)+yy*math.cos(a)+q[19];changed=True
 if changed:
  for v,pp in zip(o.data.vertices,p):v.co=inv@Vector(pp)
  o.data.update();changes.append(n)
 if n.startswith('Blind bank'):
  for v in o.data.vertices:v.co.z*=.20
  o.rotation_euler.x=.24;changes.append(n)
 if n.startswith('Curtain rail'):
  o.location+=Vector(q[22:25]);changes.append(n)
for k,name in [('F','MATCH_F_Turning_Right'),('G','MATCH_G_Sofa_And_Bed'),('H','MATCH_H')]:
 if k=='H':continue
 x=fit['cameras'][k];c=bpy.data.objects[name];c.rotation_mode='AXIS_ANGLE';ang=math.sqrt(sum(v*v for v in x[:3]));c.rotation_axis_angle=(ang,*[v/ang for v in x[:3]]);c.location=x[3:6];c.data.lens=math.exp(x[6])
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.cycles.samples=8;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False
for vl in s.view_layers:vl.cycles.use_denoising=False
s.camera=bpy.data.objects['MATCH_G_Sofa_And_Bed']
bpy.ops.wm.save_as_mainfile(filepath=str(r/'D2_screening.blend'))
(r/'D2_changes.json').write_text(json.dumps({'fit_hypothesis':fit['name'],'source_fidelity_accepted':False,'B_baseline_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'C_two_target_capsule_topology_only_sha256':hashlib.sha256(roundbase.read_bytes()).hexdigest(),'modified_objects':changes,'shared_window_wall_depth_factor':.12,'black_jamb_width_factor':.34,'black_jamb_alignment':'nearest already-present main mullion within .065 units; otherwise retain centre','glazing':'four true openings remain, thin closed solids span opening loops','slat_local_thickness_factor':.2,'slat_rotation_x':.24,'slat_count_unchanged':True,'fit':fit},ensure_ascii=False,indent=2))
for k,name in [('F','MATCH_F_Turning_Right'),('G','MATCH_G_Sofa_And_Bed'),('H','MATCH_H')]:
 s.camera=bpy.data.objects[name];s.render.filepath=str(r/f'{k}_D2_screening_960_8spp.png');bpy.ops.render.render(write_still=True)
