import bpy,json,math
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/dark_cell_v1';bpy.ops.wm.open_mainfile(filepath=R+'/models/dark_cell_textured.blend');S=bpy.context.scene;D=bpy.context.evaluated_depsgraph_get();out={}
lights=[]
for o in S.objects:
 if o.type!='LIGHT' or o.data.type!='AREA':continue
 bad=[]
 for i in range(17):
  for j in range(17):
   a=o.matrix_world@Vector(((i/16-.5)*o.data.size,(j/16-.5)*o.data.size_y,0));hit,loc,n,idx,obj,m=S.ray_cast(D,a,Vector((0,0,1)),distance=.03)
   if not hit or not obj.name.startswith('推定_实体灯罩'):bad.append([i,j,obj.name if hit else '无'])
 lights.append({'name':o.name,'full_rectangle_samples':289,'outside_diffuser_or_blocked':bad})
out['area_light_complete_boundary_tests']=lights
# Dense entrance border rays deliberately avoid the open rectangle.
miss=[];count=0
for i in range(201):
 x=-3.199+i*6.398/200
 for j in range(111):
  z=.001+j*4.298/110
  if 1.85<x<2.95 and z<2.5:continue
  count+=1;hit,*_=S.ray_cast(D,Vector((x,-3.09,z)),Vector((0,-1,0)),distance=.5)
  if not hit:miss.append((x,z))
out['front_wall_opening_dense']={'samples':count,'misses':len(miss),'examples':miss[:15]}
# Small offsets around floor/top/perimeter joins target accidental cracks.
checks=[]
for x in [-3.199,-3.195,3.195,3.199]:
 for y in [-3.099,-3.095,2.295,2.299]:
  for z,d in [(.001,(0,0,-1)),(4.299,(0,0,1))]:
   h,*_=S.ray_cast(D,Vector((x,y,z)),Vector(d),distance=.3);checks.append(h)
out['corner_near_seams']={'samples':len(checks),'misses':checks.count(False)}
# Geometry-world support samples at both ends of every principal bar.
bar=[]
for o in S.objects:
 if not o.name.startswith('可见竖栏_'):continue
 for z,rail in [(.10,'栏杆底轨'),(3.285,'栏杆顶轨')]:
  a=Vector((o.location.x,0,z));target=bpy.data.objects[rail];p=target.matrix_world.inverted()@a;inside=all(-.5-1e-6<=p[k]<=.5+1e-6 for k in range(3))
  # Applied scale means local cube bounds are actual dimensions.
  bb=[Vector(v) for v in target.bound_box];inside=all(min(v[k] for v in bb)-1e-6<=p[k]<=max(v[k] for v in bb)+1e-6 for k in range(3))
  bar.append({'bar':o.name,'support':rail,'inside':inside})
out['bar_end_supports']=bar
json.dump(out,open(R+'/qa/assembly_checks.json','w'),ensure_ascii=False,indent=2)
