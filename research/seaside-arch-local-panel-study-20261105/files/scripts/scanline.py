import bpy,os,json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));bpy.ops.wm.open_mainfile(filepath='/workspace/scratch/fa58bfcf0425/seaside-arch-candidate-20261105/models/material.blend');s=bpy.context.scene;cam=bpy.data.objects['SOURCE04 conditional'];objs=[bpy.data.objects['W06 panel surround 03'],bpy.data.objects['W07 pink inset 03']];base=[o.location.copy() for o in objs]
def projected(o):
 points=[]
 for v in o.data.vertices:
  q=world_to_camera_view(s,cam,o.matrix_world@v.co);points.append((1192*q.x,671*(1-q.y)))
 return points
def cross(o,y):
 pp=projected(o);x=[]
 for e in o.data.edges:
  a,b=[pp[i] for i in e.vertices]
  if min(a[1],b[1])<=y<=max(a[1],b[1]) and abs(b[1]-a[1])>1e-8:x.append(a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1]))
 return [min(x),max(x)] if x else None
out={'caution':'Source annotation spans y400..435 and is subjective ±5px; per-row model silhouette is exact projective candidate, not source line measurement. Does not prove unoccluded edges.','rows':[]}
for shift in [0,-.235,-.25,-.275]:
 for o,p in zip(objs,base):o.location=p+Vector((shift,0,0))
 bpy.context.view_layer.update();row={'shift_x':shift,'objects':{}}
 for o,src in zip(objs,[[162,220],[173,211]]):
  row['objects'][o.name]={'source_conditional_span':src,'scanlines':[]}
  for y in [400,410,420,430,435]:
   pred=cross(o,y);row['objects'][o.name]['scanlines'].append({'y':y,'model_bounds':pred,'signed_conditional_residual':[pred[i]-src[i] for i in range(2)] if pred else None})
 out['rows'].append(row)
json.dump(out,open(root+'/qa/scanline.json','w'),indent=2)
print(json.dumps(out,indent=2))
