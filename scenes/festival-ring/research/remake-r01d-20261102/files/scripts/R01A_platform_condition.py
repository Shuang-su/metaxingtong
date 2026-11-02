import bpy,json,math
from pathlib import Path
from mathutils import Vector,Quaternion
r=Path(__file__).resolve().parents[1];out=r/'versions/R01A';out.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(r/'versions/R00/ring-remake-R00-platforms.blend'))
fit=json.loads((r/'qa/platform-camera-conditional-fit.json').read_text());p=fit['distance_branches'][0]['params'];el,f,cx,cy,rt,zt,zb,roll=p
# Rewrite mesh vertices from existing known local range, keeping single solid per tier.
def remap(n,rad,z0,z1):
 o=bpy.data.objects[n];vs=o.data.vertices;zmin=min(v.co.z for v in vs);zmax=max(v.co.z for v in vs);maxr=max(math.hypot(v.co.x,v.co.y) for v in vs)
 for v in vs:v.co.x*=rad/maxr;v.co.y*=rad/maxr;v.co.z=z0+(v.co.z-zmin)/(zmax-zmin)*(z1-z0)
 o.location.z=0;o.data.update()
remap('P_IN_lower_base',4.95,0,zb);remap('P_IN_text_waist_placeholder',rt+.12,zb,zt-.1);remap('P_IN_performance_disc',rt,zt-.1,zt)
# Existing annular lip preserves proportion of width as explicitly conditional refinement.
remap('P_BASE_edge_lip',4.95,zb,zb+.03);remap('P_TOP_edge_lip',rt,zt,zt+.03)
s=bpy.context.scene;cam=s.camera;az=math.radians(-40);D=30;cam.location=(D*math.cos(el)*math.sin(az),-D*math.cos(el)*math.cos(az),D*math.sin(el));q=(-cam.location).to_track_quat('-Z','Y');cam.rotation_mode='QUATERNION';cam.rotation_quaternion=q@Quaternion((0,0,1),roll);cam.data.lens=f*36/3840;cam.data.sensor_width=36;cam.data.sensor_fit='HORIZONTAL';cam.data.shift_x=(1920-cx)/3840;cam.data.shift_y=(cy-1080)/3840;cam.name='C01_4K_CONDITIONAL_AZIMUTH_MINUS40_UNRESOLVED';s['stage_status']='R01A platform-contour conditional candidate ONLY, azimuth arbitrary, superstructure absent';s.render.resolution_x=960;s.render.resolution_y=540
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ring-remake-R01A-platform-fit.blend'));bpy.ops.export_scene.gltf(filepath=str(out/'ring-remake-R01A-platform-fit.glb'),export_format='GLB');s.render.filepath=str(out/'platform-fit-material-960.png');bpy.ops.render.render(write_still=True)
