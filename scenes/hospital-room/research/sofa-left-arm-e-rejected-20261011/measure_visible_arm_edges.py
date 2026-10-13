import bpy,json,numpy as np
from mathutils import Vector
from pathlib import Path
r=Path(__file__).parent;target='Sofa • broad padded arm';out={'method':'Nearest visible object identity via true Blender scene ray_cast at native pixel centers with frozen camera and all scene meshes present. Scan rows and columns only, no source image warp. This is geometric visibility, not shadow/color thresholding. Results are trained/diagnostic, not independent validation.','variants':{}}
for label,file in [('D',r.parent/'spatial_fit_d/hospital_spatial_D.blend'),('E',r/'hospital_sofa_arm_E_REJECTED.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(file));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();out['variants'][label]={}
 for k,cam in [('G','MATCH_G_Sofa_And_Bed'),('H','MATCH_H')]:
  c=bpy.data.objects[cam];P=np.array(c.calc_matrix_camera(dg,x=1920,y=1080));V=np.array(c.matrix_world.inverted());N=np.linalg.inv(P@V);origin=c.matrix_world.translation;nr={}
  def hit(x,y):
   q=N@np.array([(x+.5)/960-1,1-(y+.5)/540,-1,1]);q=q[:3]/q[3];d=Vector(q)-origin;d.normalize();h=s.ray_cast(dg,origin,d);return h[0] and h[4].original.name==target
  rows=[1061,1068,1079] if k=='G' else [970,978,989,1010,1045,1079]
  for y in rows:
   xx=[x for x in range(0,1450) if hit(x,y)];intervals=[]
   for x in xx:
    if intervals and x==intervals[-1][1]+1:intervals[-1][1]=x
    else:intervals.append([x,x])
   nr[str(y)]={'visible_intervals_x':intervals,'rightmost_x':max(xx) if xx else None}
  if k=='H':
   tops={}
   for x in [879,900,925,950,978,1006,1035,1057]:
    yy=[y for y in range(800,1080) if hit(x,y)];tops[str(x)]=min(yy) if yy else None
   nr['visible_upper_at_source_x']=tops
  out['variants'][label][k]=nr
(r/'actual_visible_edge_scanlines.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,indent=2))
