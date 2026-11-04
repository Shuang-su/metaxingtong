import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];scene=bpy.context.scene;src=json.loads((R/'qa/R06_manual_source_landmarks.json').read_text());points={}
for pref,s,y,z,a in [('outer',6.3,4.7,2.55,20),('white',5.35,4.95,2.17,-33)]:
 a=math.radians(a);pts=[Vector((xx*math.cos(a)-hh*math.sin(a),y,(z+xx*math.sin(a)+hh*math.cos(a))*.86)) for xx,hh in [(-s/2,-s/2),(s/2,-s/2),(s/2,s/2),(-s/2,s/2)]]
 points[pref+'_upper']=max(pts,key=lambda p:p.z);points[pref+'_left']=min(pts,key=lambda p:p.x);points[pref+'_right']=max(pts,key=lambda p:p.x)
for side,a in [('left',-33),('right',33)]:
 a=math.radians(a);x=9.9*math.sin(a);y=-4+9.9*math.cos(a);points['pier_'+side+'_base']=Vector((x,y,0));points['pier_'+side+'_top']=Vector((x,y,6.3*.86))
points['disc_center']=bpy.data.objects['tilted crimson circular disc'].parent.matrix_world @ bpy.data.objects['tilted crimson circular disc'].location if False else Vector((3.8,3.3,.8*.86))
# disc is mesh in world coordinates with local adjustment; use full evaluated bounds center, not guessed center.
dg=bpy.context.evaluated_depsgraph_get();ob=bpy.data.objects['tilted crimson circular disc'];ev=ob.evaluated_get(dg);mm=ev.to_mesh();vv=[ev.matrix_world@v.co for v in mm.vertices];points['disc_center']=Vector([(max(v[i] for v in vv)+min(v[i] for v in vv))/2 for i in range(3)]);ev.to_mesh_clear()
points['gift00_center']=Vector((5.35,3.4,.3*.86));result={'manual_definition':src,'world_points':{k:list(v) for k,v in points.items()},'projection':'Blender world_to_camera_view, exact stored camera at320x176; NO image alignment/warping or postfit','views':{}}
for tag,marks in src['views'].items():
 camera=bpy.data.objects['SRC_'+tag];rows=[]
 for key,pixel in marks.items():
  co=world_to_camera_view(scene,camera,points[key]);pred=[co.x*320,(1-co.y)*176];err=math.dist(pixel,pred) if pixel else None
  rows.append(dict(id=key,manual_source_xy=pixel,model_projected_xy=pred,error_px=err,status='manual correspondence hypothesis' if pixel else 'not identifiable / out of crop'))
 errs=[r['error_px'] for r in rows if r['error_px'] is not None];result['views'][tag]={'points':rows,'visible_count':len(errs),'excluded_null_count':len(rows)-len(errs),'rmse_px':math.sqrt(sum(e*e for e in errs)/len(errs)),'mean_error_px':sum(errs)/len(errs),'max_error_px':max(errs),'acceptance':'FAILED; sparse manual features cannot establish full-image fit'}
(R/'qa/R06_landmark_projection_residuals.json').write_text(json.dumps(result,indent=2))
