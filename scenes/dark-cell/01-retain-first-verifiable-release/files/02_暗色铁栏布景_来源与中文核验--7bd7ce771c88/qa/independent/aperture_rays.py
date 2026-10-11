import bpy,json
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/dark_cell_v1';bpy.ops.wm.open_mainfile(filepath=R+'/models/dark_cell_textured.blend');s=bpy.context.scene;d=bpy.context.evaluated_depsgraph_get();out={}
n=0;bad=[]
for i in range(241):
 for j in range(151):
  x=-3.199+6.398*i/240;z=.001+4.298*j/150
  # Stay clear of trim strips; intended opening interior excludes the supporting frame.
  opening=1.88<x<2.92 and z<2.47
  h=s.ray_cast(d,Vector((x,-3.07,z)),Vector((0,-1,0)),distance=.5);n+=1
  if bool(h[0])==opening:bad.append({'x':x,'z':z,'hit':h[4].name if h[0] else None,'expected_open':opening})
out['front_wall_and_portal']={'samples':n,'mismatch':len(bad),'examples':bad[:20],'note':'门洞净边界按实际收边扣除；边缘点另由封闭构件几何与接触检查覆盖。'}
n=0;bad=[]
for i in range(13):
 x=(i-6)*.32+.12
 for j in range(201):
  z=.071+3.238*j/200;h=s.ray_cast(d,Vector((x,-.2,z)),Vector((0,1,0)),distance=.4);n+=1
  if not h[0]:bad.append((i,z))
out['all_13_bar_axes_dense']={'samples':n,'misses':len(bad),'examples':bad[:20]}
json.dump(out,open(R+'/qa/independent/aperture_rays.json','w'),ensure_ascii=False,indent=2)
