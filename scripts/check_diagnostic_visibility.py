import bpy,json,math
from pathlib import Path
from mathutils import Vector,Quaternion
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/r07-material.blend'));s=bpy.context.scene;c=s.objects['diagnostic-underbridge-fixed']
configs=[{'label':'saved-a','location':list(c.location),'target':[5.5,0,-.35],'lens':22,'roll_degrees':0},{'label':'under-gap-b','location':[5.01,0,-1.2],'target':[5.46,0,-.3],'lens':28,'roll_degrees':90}]
out=[]
for cfg in configs:
 c.location=cfg['location'];c.data.lens=cfg['lens'];c.rotation_mode='QUATERNION';c.rotation_quaternion=(Vector(cfg['target'])-c.location).to_track_quat('-Z','Y')@Quaternion((0,0,1),math.radians(cfg['roll_degrees']));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();vis={}
 for n in ['inferred-low-bridge-central-step','inferred-low-bridge-step-outer']:
  o=s.objects[n];me=o.data;me.calc_loop_triangles();rows=[];bottom=0;inside=0
  for t in me.loop_triangles:
   if t.normal.z>-.5:continue
   bottom+=1;p=o.matrix_world@sum((me.vertices[i].co for i in t.vertices),Vector())/3;q=world_to_camera_view(s,c,p)
   if q.z<=0 or not(0<q.x<1 and 0<q.y<1):continue
   inside+=1;direction=p-c.location;hit=s.ray_cast(dg,c.location,direction.normalized(),distance=direction.length+.001)
   if hit[0] and hit[4].name==n and (hit[1]-p).length<.001:rows.append({'triangle':t.index,'point':list(p),'pixel':[q.x*1192,(1-q.y)*671],'hit_object':hit[4].name,'target_distance_error':(hit[1]-p).length})
  vis[n]={'bottom_triangles':bottom,'in_frame_centroids':inside,'actually_visible_centroids':len(rows),'witnesses':rows}
 out.append({'config':cfg,'visibility':vis})
assert all(x['actually_visible_centroids']>0 for x in out[-1]['visibility'].values())
(R/'results/diagnostic-visibility.json').write_text(json.dumps(out,indent=2));d=json.loads((R/'docs/diagnostic-configuration.json').read_text());d['camera'].update(configs[-1]);d['camera']['name']='diagnostic-underbridge-fixed';(R/'docs/diagnostic-configuration-b.json').write_text(json.dumps(d,indent=2));print([(x['config']['label'],{n:a['actually_visible_centroids'] for n,a in x['visibility'].items()}) for x in out])
