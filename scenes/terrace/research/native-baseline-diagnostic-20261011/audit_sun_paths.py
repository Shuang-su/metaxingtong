import bpy,json,pathlib,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=pathlib.Path(__file__).resolve().parent;sc=bpy.context.scene;cam=bpy.data.objects['SOURCE_5586__01h33m06s'];dg=bpy.context.evaluated_depsgraph_get();sun=bpy.data.objects['Sun'];to_sun=(sun.matrix_world.to_quaternion()@Vector((0,0,1))).normalized()
grid=bpy.data.objects['CentralGrid_VisibleAndCasting'];gt=BVHTree.FromPolygons([grid.matrix_world@v.co for v in grid.data.vertices],[list(p.vertices) for p in grid.data.polygons])
# Ten frozen native image-space probes. Roles corrected after independent visual review; no probe moved or added.
# These are image-space test probes, not asserted 3D surveyed landmarks.
samples=[('diagonal_left_near',110,1012),('diagonal_left_mid',215,938),('diagonal_centre_near',464,1036),('diagonal_centre_mid',530,948),('diagonal_right_near',785,1038),('diagonal_right_mid',825,970),('horizontal_band_left',250,951),('horizontal_band_mid',600,951),('horizontal_band_right',1130,951),('adjacent_sunlit_control',350,1015)]
def ray_pixel(u,v):
 # Horizontal sensor fit, zero shift, square pixels, 1920x1080.
 local=Vector(((u/1920-.5)*cam.data.sensor_width/cam.data.lens,(.5-v/1080)*cam.data.sensor_width*(1080/1920)/cam.data.lens,-1)).normalized()
 return cam.matrix_world.translation,cam.matrix_world.to_quaternion()@local
records=[]
for probe_id,(original_label,u,v) in enumerate(samples,1):
 role='shadow_band_candidate' if probe_id in [1,2,4,7,8,9] else 'sunlit_control'
 label=f'point_{probe_id:02d}'
 origin,ray=ray_pixel(u,v);hit,pos,norm,index,obj,mat=sc.ray_cast(dg,origin,ray,distance=1000)
 r={'label':label,'probe_id':probe_id,'role':role,'original_test_label':original_label,'role_correction':'Originally mislabelled as a diagonal-shadow point; independently checked to be sunlit; position retained unchanged.' if probe_id in [3,5,6] else ('Shadow-band candidate only; transverse versus longitudinal caster identity is not assumed.' if probe_id in [1,2,4,7,8,9] else 'Original sunlit control.'),'source_pixel':[u,v],'camera_ray_hits':obj.name if hit else None,'hit_world':list(pos) if hit else None,'hit_normal':list(norm) if hit else None}
 if hit:
  start=pos+to_sun*.002;gh=gt.ray_cast(start,to_sun,100)
  allhit,p2,n2,idx2,o2,m2=sc.ray_cast(dg,start,to_sun,distance=1000)
  t=(4.769845962524414-pos.z)/to_sun.z;at=pos+to_sun*t
  r.update({'existing_grid_sun_occlusion':gh[0] is not None,'grid_hit_world':list(gh[0]) if gh[0] else None,'any_scene_occluder_toward_sun':o2.name if allhit else None,'other_hit_world':list(p2) if allhit else None,'other_hit_hidden_render':o2.hide_render if allhit else None,'ray_at_grid_bottom_height':list(at),'at_grid_height_within_current_grid_xy_bbox':(-4.0875<=at.x<=1.375 and -.489<=at.y<=3.749)})
 records.append(r)
lights=[]
for o in sc.objects:
 if o.type=='LIGHT':lights.append({'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'rotation':list(o.rotation_euler),'location':list(o.location),'hide_render':o.hide_render,'angle':o.data.angle if o.data.type=='SUN' else None})
world=[]
if sc.world and sc.world.use_nodes:
 for n in sc.world.node_tree.nodes:
  if n.type=='BACKGROUND':world.append({'node':n.name,'color':list(n.inputs['Color'].default_value),'strength':n.inputs['Strength'].default_value})
report={'sample_roles':{'shadow_band_candidates':[1,2,4,7,8,9],'sunlit_controls':[3,5,6,10],'positions_changed':False,'new_points_added':False},'scope':'Read-only frozen green main scene. Pixel samples map into existing model with fixed legacy camera. Not a source-camera calibration or proof that source geometry and current model coincide.','ray_direction_to_sun':list(to_sun),'probes':records,'lights':lights,'world_background':world,'conclusion':'All conclusions must distinguish absence of direct-sun geometric occlusion from the contrast effect of area/world fill. No lights, geometry, materials or per-camera visibility were changed.'}
(P/'sun_path_audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
