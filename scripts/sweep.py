import bpy,os,json,math,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));p='/workspace/scratch/fa58bfcf0425/seaside-arch-candidate-20261105/models/material.blend'
bpy.ops.wm.open_mainfile(filepath=p);s=bpy.context.scene;cam=bpy.data.objects['SOURCE04 conditional'];circle=bpy.data.objects['W08 lower circle 0'];moving=[bpy.data.objects['W06 panel surround 03'],bpy.data.objects['W07 pink inset 03']];mesh=[o for o in s.objects if o.type=='MESH'];orig=[o.location.copy() for o in moving]
def bounds(o):
 vs=[o.matrix_world@v.co for v in o.data.vertices];return [[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]
def bvh(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices) for t in o.data.loop_triangles],all_triangles=True)
def overlap(a,b):return all(a[i][1]>=b[i][0] and b[i][1]>=a[i][0] for i in range(3))
fixed={o.name:(bounds(o),bvh(o)) for o in mesh if o not in moving};deps=bpy.context.evaluated_depsgraph_get();c=circle.location.copy();bb=bounds(circle);front=bb[1][0];radius=(bb[0][1]-bb[0][0])/2
samples=[]
for rr in [0,.25,.5,.75,.9,.98,.995]:
 for j in range(720 if rr else 1):
  a=2*math.pi*j/720;samples.append((rr,j,Vector((c.x+radius*rr*math.cos(a),front,c.z+radius*rr*math.sin(a)))))
def pixel(pt):q=world_to_camera_view(s,cam,pt);return [1192*q.x,671*(1-q.y)]
report={'source_model_sha256':hashlib.sha256(open(p,'rb').read()).hexdigest(),'saved_model':False,'only_moving':[o.name for o in moving],'source_disc_center':[262,420],'source_frame03_outer_x_at_y400_435':[162,220],'source_frame03_luminous_x':[173,211],'circle_projected_center':pixel(c),'circle_center_residual':math.dist(pixel(c),(262,420)),'samples_per_shift':len(samples),'sample_radii':[0,.25,.5,.75,.9,.98,.995],'perimeter_step_degrees':.5,'tests':[]}
for shift in [0,-.20,-.23,-.235,-.24,-.245,-.25,-.255,-.26,-.265,-.27,-.275,-.28,-.285,-.30]:
 for o,q in zip(moving,orig):o.location=q+Vector((shift,0,0))
 bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();pairs=[]
 for o in moving:
  a=bounds(o);tree=bvh(o)
  for other in mesh:
   if other==o:continue
   ob,ot=fixed[other.name] if other not in moving else (bounds(other),bvh(other))
   if overlap(a,ob):pairs.append({'moving':o.name,'other':other.name,'aabb':True,'surface_triangle_pairs':len(tree.overlap(ot))})
 hits={};perimeter_bad=[]
 for rr,j,pt in samples:
  v=pt-cam.location;hit,loc,normal,index,obj,matrix=s.ray_cast(deps,cam.location,v.normalized(),distance=v.length+.001);name=obj.name if hit else 'NO_HIT';hits[name]=hits.get(name,0)+1
  if rr==.995 and name!=circle.name:perimeter_bad.append([j,name])
 projected={o.name:{'vertex_bounds_pixels':[[min(pixel(o.matrix_world@v.co)[i] for v in o.data.vertices),max(pixel(o.matrix_world@v.co)[i] for v in o.data.vertices)] for i in range(2)],'world_bounds':bounds(o)} for o in moving}
 report['tests'].append({'shift_x':shift,'pairs':pairs,'circle_sample_first_hits':hits,'perimeter_wrong_hits':perimeter_bad,'projected':projected})
json.dump(report,open(root+'/qa/sweep.json','w'),indent=2)
print('DONE',[(t['shift_x'],t['circle_sample_first_hits'],len(t['perimeter_wrong_hits'])) for t in report['tests']])
