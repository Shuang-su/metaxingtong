import bpy,json,numpy as np
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/C02_repaired_materials.blend'));s=bpy.context.scene
old=Vector((2.7,9.4,3.89));new=Vector((2.004594411262765,8.358255145554718,3.893922449190922));delta=new-old;ap=Vector((.20156395,10.3,6.14944935));u2=Vector((1.4614,6.9885,3.8774));u4=Vector((1.3,12.2,3.89))
for i,a,b in [(2,u2,old),(3,old,u4)]:
 M=np.array([[a.x-ap.x,b.x-ap.x],[a.y-ap.y,b.y-ap.y]])
 for v in bpy.data.objects[f'T01_roof_{i}'].data.vertices:
  coeff=np.linalg.solve(M,np.array([v.co.x-ap.x,v.co.y-ap.y]));w=coeff[1] if i==2 else coeff[0];v.co+=delta*float(w)
 for v in bpy.data.objects[f'T01_skirt_{i}'].data.vertices:
  row,col=divmod(v.index,17);t=row/16;q=col/16;v.co+=delta*t*(q if i==2 else 1-q)
for i,a,b in [(2,u2,new),(3,new,u4)]:
 o=bpy.data.objects[f'T01_roof_hem_{i}'];zs=[v.co.z for v in o.data.vertices];o.location=(a+b)/2;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.scale.z=(b-a).length/(max(zs)-min(zs))
# CHECK cameras only: lower focal and larger orbit so near chair/front box aren't cropped.
for i in range(1,9):
 import math
 a=math.tau*(i-1)/8-math.pi/2;o=bpy.data.objects[f'CHECK_{i:02}'];o.location=(23*math.cos(a),7+23*math.sin(a),10);o.rotation_euler=(Vector((0,7,2))-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=1550*36/1920
report={'stage':'C03 shared right eave conditional improvement','semantic':'T2 right OUTER roof eave, not front curtain corner','training_pixels':[[650,244],[1038,129]],'manual_uncertainty_px':[8,8],'fixed_source_cameras':'unchanged historical working solution, not calibrated truth','new_control_world_working_units':list(new),'ray_separation_working_units':.021894954057468698,'nominal_pixel_residuals':[1.004012499,.904021814],'limits':'Two soft correspondences do not validate full roof or unique camera. Left eave retains failed 15/13px joint test, third not used to fit this control. Back roof unverified.','CHECK_change':'only non-source orbit widened, native source cameras unchanged'};(R/'qa/C03_changes.json').write_text(json.dumps(report,indent=2));bpy.context.preferences.filepaths.save_version=0;s.render.threads=2;s.cycles.samples=8;s.camera=bpy.data.objects['CHECK_MAIN'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/C03_right_eave_materials.blend'));white=bpy.data.materials.get('WHITE_GEOMETRY_PERSISTENT');white.use_fake_user=True
for o in s.objects:
 if o.type in {'MESH','CURVE'}:o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/C03_right_eave_white.blend'))
for cam in ['SOURCE_CONDITIONAL_1','SOURCE_CONDITIONAL_2']+[f'CHECK_{i:02}' for i in range(1,9)]:
 s.camera=bpy.data.objects[cam];s.render.resolution_x=960;s.render.resolution_y=540 if cam.startswith('SOURCE') else 720;s.render.filepath=str(R/f'renders/C03_{cam}_white.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'models/C03_right_eave_materials.blend'));s=bpy.context.scene
for cam in ['SOURCE_CONDITIONAL_1','SOURCE_CONDITIONAL_2','CHECK_MAIN']:
 s.camera=bpy.data.objects[cam];s.render.resolution_x=960;s.render.resolution_y=540 if cam.startswith('SOURCE') else 720;s.render.filepath=str(R/f'renders/C03_{cam}_materials.png');bpy.ops.render.render(write_still=True)
print('C03_DONE')
