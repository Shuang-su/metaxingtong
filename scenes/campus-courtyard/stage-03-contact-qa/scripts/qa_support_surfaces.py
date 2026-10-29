import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];D=R/'stage-03-contact-qa';Q=D/'qa'
ground_names=['SITE-PAVERS','LAWN-L','COURT-NE','COURT-E','COURT-E-IN','ENTRY-STEPS']
def surface(x,y):
    hits=[]
    for name in ground_names:
        o=bpy.data.objects[name];inv=o.matrix_world.inverted();hit,p,n,i=o.ray_cast(inv@Vector((x,y,2)),inv.to_3x3()@Vector((0,0,-1)),distance=4)
        if hit:hits.append(((o.matrix_world@p).z,name))
    return max(hits) if hits else (None,None)
def near_min(o,x,y,radius):
    v=[o.matrix_world@v.co for v in o.data.vertices];v=[v for v in v if abs(v.x-x)<=radius and abs(v.y-y)<=radius]
    return min(p.z for p in v) if v else None
rows={}
for phase in ['stage-02-material-candidate','stage-03-contact-qa']:
 bpy.ops.wm.open_mainfile(filepath=str(R/phase/'campus-courtyard_material.blend'));bpy.context.view_layer.update();support=[]
 benches={'BENCH-01':(3.6,8.8),'BENCH-02':(-7.8,18),'BENCH-03':(-13,21),'BENCH-04':(13 if phase.startswith('stage-02') else 10.6,23.4)}
 for name,(x,y) in benches.items():
  for u in [-.88,.88]:
   for v in [-.36,.38]:
    xx=x+u;yy=y+v;z,under=surface(xx,yy);bottom=near_min(bpy.data.objects[name],xx,yy,.12)
    support.append({'object':name,'xy':[xx,yy],'support':under,'support_top_z':z,'lowest_foot_vertex_z':bottom,'gap_model_units':bottom-z,'contact_within_1e-5':abs(bottom-z)<1e-5})
 for name,x,y,r in [('LAMP-01',3.3,13.5,.14),('LAMP-02',.2,20,.14),('LAMP-03',-.65,24,.14),('LAMP-04',13.5,5,.14),('HOOP-01',4.7,24.9,.34),('HOOP-02',6.6,14.9,.34),('HOOP-03',17,-5.1,.34),('TREEBED-01',3.9,-3.1,2.25),('TREEBED-05',17.8,-8.5,.91)]:
  z,under=surface(x,y);bottom=near_min(bpy.data.objects[name],x,y,r);support.append({'object':name,'xy':[x,y],'support':under,'support_top_z':z,'lowest_foot_vertex_z':bottom,'gap_model_units':bottom-z,'contact_within_1e-5':abs(bottom-z)<1e-5})
 if phase.startswith('stage-03'):
  for x in [16.3,19.25]:
   for y in [-17,-10.5]:
    z,under=surface(x,y);bottom=near_min(bpy.data.objects['STAIR-BASE-PLATES'],x,y,.16);support.append({'object':'STAIR-BASE-PLATES','xy':[x,y],'support':under,'support_top_z':z,'lowest_foot_vertex_z':bottom,'gap_model_units':bottom-z,'contact_within_1e-5':abs(bottom-z)<1e-5,'column_foundation':'original columns continue below surface; hidden footing inferred, not certified'})
 def bounds(name):
    o=bpy.data.objects[name];v=[o.matrix_world@Vector(p) for p in o.bound_box];return [[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]]
 collision=[]
 for a,b in [('FLOWERBED-02','ENTRY-STEPS'),('FLOWERBED-03','COURT-NE')]:
    aa,bb=bounds(a),bounds(b);over=[min(aa[1][i],bb[1][i])-max(aa[0][i],bb[0][i]) for i in range(3)]
    collision.append({'a':a,'b':b,'bounds_a':aa,'bounds_b':bb,'axis_overlap':over,'positive_aabb_intersection':all(v>0 for v in over),'xy_intersection':all(v>0 for v in over[:2]),'method':'AABB diagnostic, not a general mesh collision certificate'})
 cam=bpy.data.objects['SRC04'];floor=bpy.data.objects['SITE-PAVERS'];miss=[];tested=0;f=cam.data.lens/36*1920
 for u in range(1500,1920,8):
  for v in range(850,1080,8):
    local=Vector(((u-960)/f,(540-v)/f,-1)).normalized();direction=cam.matrix_world.to_3x3()@local
    hit,p,n,i=floor.ray_cast(cam.location,direction,distance=300);tested+=1
    if not hit:miss.append([u,v])
 rows[phase]={'supports':support,'flower_step_court_tests':collision,'source04_lower_right_floor_roi':[1500,850,1920,1080],'floor_roi_ray_count':tested,'floor_roi_misses':len(miss),'missing_pixels_samples':miss,'scope':'specified support samples and explicit source floor ROI only; court/tree/stair plan layout still unconfirmed'}
(Q/'support_surface_before_after.json').write_text(json.dumps(rows,indent=2))
print(json.dumps({k:{'support_count':len(v['supports']),'contact_pass':sum(x['contact_within_1e-5'] for x in v['supports']),'floor_roi_misses':v['floor_roi_misses'],'flower_xy_overlap':[x['xy_intersection'] for x in v['flower_step_court_tests']]} for k,v in rows.items()},indent=2))
