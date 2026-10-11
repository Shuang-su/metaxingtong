import bpy,json
from bpy_extras.object_utils import world_to_camera_view
R='/workspace/scratch/fa58bfcf0425';bpy.ops.wm.open_mainfile(filepath=R+'/ktv_fullroom/delivery/models/KTV_Complete_Open_Stage.blend');sc=bpy.context.scene
sc.render.resolution_x=1188;sc.render.resolution_y=668;sc.render.resolution_percentage=100
out={}
for cname in ['MATCH_D_01h58m39s_empty','DETAIL_Telescope_Lamp']:
 cam=bpy.data.objects[cname];sc.camera=cam;bpy.context.view_layer.update();out[cname]={}
 for collname in ['02_Inflated_Armchairs','08_Optional_Star_Companion']:
  c=bpy.data.collections[collname];ps=[world_to_camera_view(sc,cam,o.matrix_world@v.co) for o in c.objects if o.type=='MESH' for v in o.data.vertices]
  out[cname][collname]={'hide_render':c.hide_render,'projected_min':[min(p[i] for p in ps) for i in range(3)],'projected_max':[max(p[i] for p in ps) for i in range(3)],'all_vertices_right_of_frame':all(p.x>1 for p in ps),'all_vertices_left_of_frame':all(p.x<0 for p in ps),'notes':'Normalized camera coordinates x/y in 0..1 are inside frame, z is depth. No occlusion test.'}
json.dump(out,open(R+'/ktv_fixed_visibility_20261010/qa/furniture_camera_projection.json','w'),indent=2);print(out)
