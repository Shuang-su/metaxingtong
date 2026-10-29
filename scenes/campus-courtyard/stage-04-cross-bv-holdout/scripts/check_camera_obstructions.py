"""Read-only diagnostic of camera placement and projected fixed-object points."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
D=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(D/'frozen_model_diagnostic_cameras.blend'))
s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();rows={}
landmarks={
 'HOOP03_base_center':[17,-5.1,.07],
 'HOOP02_base_center':[6.6,14.9,.11],
 'HOOP01_base_center':[4.7,24.9,0],
 'LAMP01_ground':[3.3,13.5,.11],
 'LAMP02_ground':[.2,20,0],
 'LAMP03_ground':[-.65,24,0],
 'LAMP04_ground':[13.5,5,0],
 'TRACK_center_near_blue':[-2.5,16,.05],
 'GREEN_centre':[13.5,-7.5,.07],
 'BLUE_centre':[10.5,16,.11],
}
for cam in s.objects:
 if cam.type!='CAMERA' or not cam.name.startswith('HOLDOUT_'):continue
 result={'location':list(cam.location),'landmarks':{}}
 for name,xyz in landmarks.items():
    q=world_to_camera_view(s,cam,Vector(xyz));result['landmarks'][name]={'xy':[q.x*1920,(1-q.y)*1080],'depth':q.z,'correspondence':'not uniquely identified in source; center is not the visible fragment center'}
 direction=cam.rotation_euler.to_matrix()@Vector((0,0,-1));hit,loc,nor,idx,obj,mat=s.ray_cast(deps,cam.location,direction,distance=200)
 result['central_view_ray']={'first_mesh':obj.name if hit else None,'distance':(loc-cam.location).length if hit else None,'world':list(loc) if hit else None}
 o=bpy.data.objects['ENTRY-STEPS'];p=o.matrix_world.inverted()@cam.location;probes=[]
 for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
    hit,loc,nor,idx=o.ray_cast(p,Vector(d),distance=200)
    probes.append({'direction':d,'hit':bool(hit),'distance':(loc-p).length if hit else None,'outward_normal_dot_ray':nor.dot(Vector(d)) if hit else None})
 result['entry_step_six_axis_exit_probes']=probes
 result['inside_entry_closed_solid_by_all_six_exit_normals']=all(p['hit'] and p['outward_normal_dot_ray']>.99 for p in probes)
 rows[cam.name]=result
(D/'qa/camera_obstructions.json').write_text(json.dumps({'render_engine':s.render.engine,'samples_in_actual_saved_blend':s.cycles.samples,'denoise':s.cycles.use_denoising,'cameras':rows,'warning':'Model base centers are projection diagnostics only, not source fragment centers or established instance matches. No model state saved or modified.'},indent=2))
print('READONLY_OBSTRUCTION_CHECK_DONE',flush=True)
