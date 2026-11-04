import bpy,json,pathlib,hashlib
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=pathlib.Path(__file__).resolve().parents[1];f=P/'models/R06_material.blend';bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene;D={'model_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'units':'arbitrary working units, not measured metres','source_status':'all source FAILED; per-instance identities unresolved except broad component type','objects':[],'lamp_diagnostics':{}}
for o in sorted(bpy.data.objects,key=lambda x:x.name):
 if o.type!='MESH':continue
 world=[o.matrix_world@v.co for v in o.data.vertices];mn=[min(v[i] for v in world) for i in range(3)];mx=[max(v[i] for v in world) for i in range(3)];group=o.name.split('_')[0];D['objects'].append({'id':o.name,'group':group,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'world_bounds':[mn,mx],'materials':[m.name for m in o.data.materials],'inspection_context_images_not_instance_proof':[8,23,26] if group in ['WALL','BASEBOARD','LANTERN','FLOOR'] else [8,23],'classification':'current geometry dimensions/count/location inferred; source per-instance match unconfirmed','hidden':o.hide_render})
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
for name in ['SOURCE_08_wide','SOURCE_23_oblique','SOURCE_26_side']:
 cam=bpy.data.objects[name];arr=[]
 for side in [-1,1]:
  for j in range(4):
   o=bpy.data.objects[f'LANTERN_{side}_{j}_diffuser'];p=o.matrix_world.translation;v=world_to_camera_view(s,cam,p);d=p-cam.location;hit,loc,n,idx,obj,mat=s.ray_cast(deps,cam.location,d.normalized(),distance=d.length+.001);arr.append({'model_fixture_id':f'LANTERN_{side}_{j}','hypothesis_point':'diffuser object origin, not physically measured bright housing centroid','world_point':list(p),'projected_px':[v.x*1192,(1-v.y)*671],'forward_depth':v.z,'inside_image':bool(v.z>0 and 0<=v.x<=1 and 0<=v.y<=1),'first_hit_object':obj.name if hit else None,'hit_distance':float((loc-cam.location).length) if hit else None,'target_distance':d.length,'source_fixture_id':None,'reason':'Visible-source centers known but identity/state/camera not verified; no nearest-point assignment or deletion'})
 D['lamp_diagnostics'][name]=arr
for rec in D['objects']:
 if rec['id'].startswith(('DOOR_leaf_-1','DOOR_trim_-1','DOOR_handle_-1','WALL_end_-1','BASEBOARD_end_-1')):
  rec['inspection_context_images_not_instance_proof']=[];rec['classification']='unseen camera-back end inferred closure; no source-specific observation'
(P/'qa/R06-object-inventory.json').write_text(json.dumps(D,indent=2))
