import bpy,json,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/workspace/scratch/fa58bfcf0425/ktv_fullroom/delivery/models/KTV_Complete_Open_Stage.blend')
sc=bpy.context.scene;out=[]
for l in sc.objects:
 if l.type!='LIGHT' or l.data.type!='AREA':continue
 inv=l.matrix_world.inverted();r=l.data.size/2;hits=[]
 for o in sc.objects:
  if o.type!='MESH' or o.hide_render or any(c.hide_render for c in o.users_collection):continue
  mat=inv@o.matrix_world;vs=[mat@v.co for v in o.data.vertices]
  if min(v.z for v in vs)>0 or max(v.z for v in vs)<0:continue
  o.data.calc_loop_triangles();count=0
  for tr in o.data.loop_triangles:
   p=[vs[i] for i in tr.vertices];cross=[]
   for a,b in zip(p,p[1:]+p[:1]):
    if a.z*b.z<0:cross.append(a+(b-a)*(-a.z/(b.z-a.z)))
   if len(cross)==2:
    a,b=cross;ab=b-a;t=max(0,min(1,-a.dot(ab)/ab.length_squared)) if ab.length_squared else 0
    if (a+ab*t).length<=r:count+=1
  if count:hits.append([o.name,count])
 ps=[l.matrix_world@Vector((r*math.cos(t*math.pi/180),r*math.sin(t*math.pi/180),0)) for t in range(360)]
 out.append({'light':l.name,'shape':l.data.shape,'size':l.data.size,'position':list(l.location),'disk_bounds':[[min(v[i] for v in ps) for i in range(3)],[max(v[i] for v in ps) for i in range(3)]],'intersections':hits})
json.dump(out,open('/workspace/scratch/fa58bfcf0425/ktv_fullroom/independent_qa/light_disk_intersections.json','w'),indent=2)
