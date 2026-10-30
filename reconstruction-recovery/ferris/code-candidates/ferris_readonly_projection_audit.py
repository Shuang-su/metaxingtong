import bpy,json,numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R='/workspace/shared/ferris-cabin-build-20261030/scenes/ferris-wheel-cabin/'
bpy.ops.wm.open_mainfile(filepath=R+'models/ferris_cabin_material.blend');s=bpy.context.scene
j=json.load(open(R+'qa/r05/source-to-3d-landmarks.json'));o=bpy.data.objects['door_window_bezel_4'];vs=np.array([list(o.matrix_world@v.co) for v in o.data.vertices]);print('RING_Y',sorted(set(vs[:,1].round(6))))
pts=np.array([p['model_world'] for p in j['points']]);print('SVD',np.linalg.svd(pts-pts.mean(0),compute_uv=False))
for n in ['SRC_front','SRC_bench','SRC_corner','SRC_high_bitrate']:
 c=bpy.data.objects[n];print('CAM',n,'loc',list(c.location),'lens',c.data.lens,'fit',c.data.sensor_fit,'sensor',c.data.sensor_width,c.data.sensor_height,'shift',c.data.shift_x,c.data.shift_y,'aspect',s.render.pixel_aspect_x,s.render.pixel_aspect_y,'dims',s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage)
 if n!='SRC_front':continue
 C=np.array(c.matrix_world);rr=np.diag([1,-1,-1])@C[:3,:3].T
 for p in j['points']:
  w=np.array(p['model_world']);q=rr@(w-C[:3,3]);f=c.data.lens/c.data.sensor_width*1920;px=np.array([960+f*q[0]/q[2]-c.data.shift_x*1920,540+f*q[1]/q[2]+c.data.shift_y*1920]);v=world_to_camera_view(s,c,Vector(w));bb=np.array([v.x*1920,(1-v.y)*1080]);nearest=vs[np.argmin(np.linalg.norm(vs-w,axis=1))];print('POINT',p['id'],'blender',bb.tolist(),'math_delta',(px-bb).tolist(),'src_resid',float(np.linalg.norm(bb-p['source_px'])),'nearest_vertex',nearest.tolist(),'dist',float(np.linalg.norm(nearest-w)))
for o in bpy.data.objects:
 if o.name in ['bench_1_seat','bench_1_back','cream_bezel_1_0','cream_bezel_2_0','cream_bezel_2_1','pillar_2']:
  vs=[o.matrix_world@Vector(v) for v in o.bound_box];print('OBJ',o.name,[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)])
