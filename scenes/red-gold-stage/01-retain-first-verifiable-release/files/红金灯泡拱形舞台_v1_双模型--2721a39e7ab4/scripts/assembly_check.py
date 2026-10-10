import bpy,json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R='/workspace/scratch/fa58bfcf0425/red_gold_stage_v1';bpy.ops.wm.open_mainfile(filepath=R+'/models/red_gold_stage_textured.blend');S=bpy.context.scene;bpy.context.view_layer.update()
objs=[o for o in S.objects if o.type=='MESH'];bounds={o.name:([min((o.matrix_world@Vector(c))[i] for c in o.bound_box) for i in range(3)],[max((o.matrix_world@Vector(c))[i] for c in o.bound_box) for i in range(3)]) for o in objs}
adj={o.name:set() for o in objs}
for i,a in enumerate(objs):
 for b in objs[i+1:]:
  aa,ab=bounds[a.name];ba,bb=bounds[b.name]
  if all(min(ab[k],bb[k])-max(aa[k],ba[k])>=-1e-5 for k in range(3)):adj[a.name].add(b.name);adj[b.name].add(a.name)
seen=set();components=[]
for name in adj:
 if name in seen:continue
 todo=[name];group=[]
 while todo:
  n=todo.pop()
  if n in seen:continue
  seen.add(n);group.append(n);todo.extend(adj[n]-seen)
 components.append(group)
anchors=[]
for name,p,source in [('左内翼顶角',(-1.98,-.37,1.52),(325,344)),('右内翼顶角',(1.98,-.37,1.52),(828,344)),('左内翼底角',(-1.98,-.37,.80),(325,420)),('右内翼底角',(1.98,-.37,.80),(828,420))]:
 q=world_to_camera_view(S,S.camera,Vector(p));pred=(q.x*1180,(1-q.y)*664);anchors.append({'name':name,'predicted_pixel':pred,'approx_source_pixel':source,'distance_pixels':((pred[0]-source[0])**2+(pred[1]-source[1])**2)**.5})
out={'broad_phase_AABB_component_count':len(components),'component_sizes':[len(x) for x in components],'component_names':components,'isolated_nodes':[x for x in components if len(x)==1],'scope':'AABB连接图是宽相筛查而非实体布尔或全接触认证。倾斜/曲面接触须结合明确端点及独立审查。','explicit_contacts':[{'pair':'左右星饰—安装座—侧景板','star_y':[0,.25],'mount_y':[.20,.42],'board_y':[.35,.63],'overlap_depths':[.05,.07]},{'pair':'悬挂柱顶—横梁','post_top_z':5.56,'beam_bottom_z':5.42,'overlap_z':.14},{'pair':'帘顶—横梁','curtain_top_z':5.5,'beam_bottom_z':5.42,'overlap_z':.08},{'pair':'后台支柱/脚—台面','post_bottom_z':.6,'foot_bottom_z':.6,'platform_top_z':.6},{'pair':'拱环脚—台面','arch_bottom_z':.6,'platform_top_z':.6}], 'projected_landmarks':anchors,'landmark_caveat':'源坐标为低清图人工近似，人物及边框遮挡影响，不作为多视标定精度证明。'}
json.dump(out,open(R+'/qa/assembly_contacts.json','w'),ensure_ascii=False,indent=2)
