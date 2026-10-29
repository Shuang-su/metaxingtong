"""Read actual B1/D1 meshes: topology, visible correspondences, sampled vent opening.
Projection proxies are not automatically visible features. Glass is separately labeled.
"""
import bpy,bmesh,json,math,sys
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import fit_shared_profile as F
fit=json.loads((R/'fit_result.json').read_text());reports={}
def trees():
 return {o.name:BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons]) for o in bpy.context.scene.objects if o.type=='MESH'}
def ray(ts,origin,direction,distance):
 out=[]
 for name,t in ts.items():
  v,n,i,d=t.ray_cast(Vector(origin),Vector(direction).normalized(),distance)
  if v is not None:out.append((float(d),name,list(v)))
 return sorted(out)
def pix(s,c,v):
 p=world_to_camera_view(s,c,Vector(v));return [1920*p.x,1080*(1-p.y)]
for stage,filename,params in [('B1','B1_frozen_camera_baseline.blend',F.P0),('D1','D1_shared_dashboard_material.blend',fit['dashboard_parameters'])]:
 bpy.ops.wm.open_mainfile(filepath=str(R/'models'/filename));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();mesh=[]
 for o in s.objects:
  if o.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(o.data);mesh.append({'object':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True),'hide_render':o.hide_render});bm.free()
 views=[]
 for id in F.IDS:
  frame=fit['results'][id]['state'];s.frame_set(frame);bpy.context.view_layer.update();ts=trees();c=bpy.data.objects['SRC_'+id+('_open' if id=='S02' else '_closed')];points=F.profile_points(params);points.update(F.a_points([0,0]));checks=[]
  targets=[('dash_top_corner','D01_dashboard_top',points['dash_top_corner']),('dash_bottom_corner','D01_dashboard_top',points['dash_bottom_corner']),('a_foot','A01_fixed_A_pillar',points['a_foot'])]
  targets += [('vent_rim_'+str(i),'D03_vent_round_rim',v) for i,v in enumerate(points['vent_rim'][::8])]
  base=F.G['states'][str(frame)]
  for name,ob in [('mirror_center','P17_mirror_glass'),('roof_lower_line','A02_side_roof_rail'),('door_belt_line','P02_upper_belt')]:
   if F.A[id].get(name) is None:continue
   q=np.asarray(base[name]);q=q[None,:] if q.ndim==1 else q
   for i,v in enumerate(q):targets.append((name+('_'+str(i) if len(q)>1 else ''),ob,v))
  for name,expected,proxy in targets:
   proxy=Vector(proxy);o=bpy.data.objects[expected]
   # Real nearest mesh vertex confirms the modeled bevel vs nominal proxy.
   actual=min((o.matrix_world@v.co for v in o.data.vertices),key=lambda v:(v-proxy).length)
   if name in ['a_foot','mirror_center']:actual=proxy # interface/shape center is not a mesh endpoint
   dist=(actual-c.location).length;hits=ray(ts,c.location,actual-c.location,dist+.01);first=hits[0] if hits else None;opaque=next((x for x in hits if x[1]!='P12_side_window_glass'),None)
   allowed=[expected,'D01_dashboard_top'] if name=='a_foot' else [expected]
   visible=bool(opaque and opaque[1] in allowed and (abs(opaque[0]-dist)<.005 or name=='mirror_center'))
   # A mathematically exact bevel vertex can miss both adjacent triangles. Record
   # subpixel neighboring rays instead of calling a numerical grazing miss an occluder.
   cam_right=c.matrix_world.to_3x3()@Vector((1,0,0));cam_up=c.matrix_world.to_3x3()@Vector((0,1,0));offset=dist/(1920*c.data.lens/36)*.3;jitter=[]
   for u,v in [(-1,0),(1,0),(0,-1),(0,1)]:
    target=actual+offset*(u*cam_right+v*cam_up);hh=ray(ts,c.location,target-c.location,dist+.01);op=next((x for x in hh if x[1]!='P12_side_window_glass'),None);jitter.append(op)
   nearvisible=any(x and x[1] in allowed and abs(x[0]-dist)<.005 for x in jitter)
   classification='visible_shape_center' if visible and name=='mirror_center' else 'visible_surface' if visible else 'grazing_vertex_neighborhood_visible' if opaque is None and nearvisible else 'blocked_by_other_object' if opaque and opaque[1] not in allowed else 'same_object_different_depth' if opaque else 'unresolved_grazing_or_missing_surface'
   row={'feature':name,'role':'held_out' if name.startswith(('mirror','roof','door')) else 'fit_dashboard' if name.startswith(('dash','vent')) else 'A_diagnostic_not_applied','proxy_xyz':list(proxy),'actual_xyz':list(actual),'proxy_to_vertex_model_units':(actual-proxy).length,'proxy_pixel':pix(s,c,proxy),'actual_pixel':pix(s,c,actual),'expected_object':expected,'target_distance':dist,'first_hit':first,'first_opaque_hit':opaque,'surface_visible_within_0_005':visible,'subpixel_neighbor_hits':jitter,'classification':classification,'notes':'A foot is a nominal fixed-pillar/dashboard intersection. Rim nearest vertices incorporate bevel. Transparent pane hit is recorded but skipped for opaque occlusion. Mirror center is a shape-axis proxy; visible if its ray first reaches mirror glass. Held-out line endpoint probes do not establish the full observed segment is visible.'}
   if name in F.A[id] and F.A[id][name] is not None and np.asarray(F.A[id][name]).ndim==1:row['actual_point_error_px']=float(np.linalg.norm(np.asarray(row['actual_pixel'])-F.A[id][name]))
   checks.append(row)
  # Aperture center is not a solid feature: separate depth test instead of visibility-to-center.
  center=Vector(points['vent_center']);rr=ray(ts,c.location,center-c.location,4)
  views.append({'id':id,'state':frame,'checks':checks,'vent_axis_first_opaque_hit':next((x for x in rr if x[1]!='P12_side_window_glass'),None)})
 s.frame_set(1);bpy.context.view_layer.update();ts=trees();dy,tilt,thick,scale,h=params;rot=Matrix.Rotation(float(tilt),3,'X');anchor=Vector((0,.637,.94));new=Vector((0,.637+dy,1.0325-thick+.0025))
 def tr(v):return rot@(Vector(v)-anchor)+new
 vent=[]
 for i in range(21):
  for j in range(21):
   xx=(i-10)*.008;zz=(j-10)*.008
   if xx*xx+zz*zz<.089**2 and all(abs(zz-z)>.014 for z in [-.055,0,.055]):
    hits=ray(ts,tr((.8+xx*scale,.59,.77+h+zz*scale)),rot@Vector((0,1,0)),.35);vent.append(hits[0] if hits else None)
 reports[stage]={'mesh_count':len(mesh),'meshes':mesh,'all_closed_positive':all(x['nonmanifold_edges']==0 and x['signed_volume']>0 for x in mesh),'zero_area_faces_total':sum(x['zero_area_faces'] for x in mesh),'views':views,'vent_gap_rays':{'count':len(vent),'recess_end_hits':sum(x is not None and x[1]=='D05_vent_recess_end' for x in vent),'fascia_blockers':sum(x is not None and x[1]=='D02_dashboard_end_fascia' for x in vent),'samples':vent},'limits':'Local mesh and sampled aperture only. No full car, collision sweep, support, true camera, or source acceptance.'}
(R/'qa/actual_geometry_and_visibility.json').write_text(json.dumps(reports,indent=2)+'\n')
for stage,r in reports.items():print(stage,r['all_closed_positive'],r['zero_area_faces_total'],{k:v for k,v in r['vent_gap_rays'].items() if k!='samples'})
