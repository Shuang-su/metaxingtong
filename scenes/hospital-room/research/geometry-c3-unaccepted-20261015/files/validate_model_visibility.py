import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).parent;label=sys.argv[sys.argv.index('--')+1];s=bpy.context.scene;P=json.load(open(R/'C2_selected_parameters.json'));tests=[]
# Whole-scene ray checks inset into expected object's projected silhouette; no hiding/isolating meshes.
for br in P['branches']:
 for t in br['before' if label=='D' else 'after']:
  if t['projection']:
   tests.append({'branch_id':br['branch_id'],'view':br['frame'],'expected_object':br['mesh'],'branch':br['branch'],'source':t['source'],'projected_boundary':t['projection']})
# Curtain long outer-right samples used for candidate screen.
Q=json.load(open(R/'drape_width_screen.json'))
for k,z in Q['views'].items():
 for t in z['D' if label=='D' else ('P0' if label=='C2' else 'width_candidate')]:
  tests.append({'branch_id':k+':gray_outer_right:long_unoccluded','view':k,'expected_object':'Curtain • rebuilt uniform eight-fold drape','branch':'right','source':t['source'],'projected_boundary':t['projection']})
for view in ['G','H','F','N640']:
 n={'G':'MATCH_G_Sofa_And_Bed','H':'MATCH_H','F':'MATCH_F_Turning_Right','N640':'C2_N640_static_background_hypothesis'}[view]
 if n not in bpy.data.objects:
  c=P['cameras']['N640'];data=bpy.data.cameras.new(n);data.lens=c['lens'];data.sensor_width=36;data.sensor_fit='HORIZONTAL';cam=bpy.data.objects.new(n,data);s.collection.objects.link(cam);cam.matrix_world=Matrix(c['matrix'])
 cam=bpy.data.objects[n];rot=cam.matrix_world.to_3x3().normalized();origin=cam.matrix_world.translation;f=1920*cam.data.lens/36
 for t in (q for q in tests if q['view']==view):
  uv=list(t['projected_boundary']);branch=t['branch']
  if branch=='upper':uv[1]+=2
  elif branch=='left':uv[0]+=2
  elif branch=='right':uv[0]-=2
  elif branch=='lower':uv[1]-=2
  direction=(rot@Vector(((uv[0]-960)/f,(540-uv[1])/f,-1))).normalized();hit,loc,norm,index,obj,matrix=s.ray_cast(bpy.context.evaluated_depsgraph_get(),origin,direction,distance=100)
  t['inset_pixel']=uv;t['ray_hit_object']=obj.name if hit else None;t['expected_visible']=bool(hit and obj.name==t['expected_object']);t['ray_distance']=float((loc-origin).length) if hit else None
out={'status':'ACTUAL_SCENE_RAY_VISIBILITY_NOT_OVERALL_ACCEPTANCE','model':bpy.data.filepath,'stage':label,'method':'2px inward ray from actual scene camera through projected named boundary; whole scene, no visibility changes','tests':tests,'visible_count':sum(t['expected_visible'] for t in tests),'failed_count':sum(not t['expected_visible'] for t in tests)};(R/f'{label}_branch_visibility.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(label,'visible',out['visible_count'],'failed',out['failed_count']);print([(t['branch_id'],t['source'],t['ray_hit_object']) for t in tests if not t['expected_visible']])
