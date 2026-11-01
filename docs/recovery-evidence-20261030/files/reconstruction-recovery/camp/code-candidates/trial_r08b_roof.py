import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
r=Path(__file__).resolve().parents[1];out=r/'qa/R08_trial';bpy.ops.wm.open_mainfile(filepath=str(r/'models/R08a_chair_trial.blend'));s=bpy.context.scene
# Conditional visible boundary control, NOT evidence for a second physical apex.
old=Vector((-2.4,12.4,3.89));new=Vector((-1.99651054,10.,5.49581436));delta=new-old
for i in [4,5]:
 o=bpy.data.objects[f'T01_roof_panel_{i:02}']
 for v in o.data.vertices:
  a,b=divmod(v.index,15);t=a/12;u=b/14;weight=u if i==4 else 1-u;v.co+=delta*t*weight
 o=bpy.data.objects[f'T01_skirt_panel_{i:02}']
 for v in o.data.vertices:
  a,b=divmod(v.index,17);t=a/16;u=b/16;weight=u if i==4 else 1-u;v.co+=delta*t*weight
# Cylinders generated local Z; keep radius and material, update shared endpoints.
upper=[Vector(x) for x in [(-3.3,9.5,3.89),(-.5396,8.1541,3.8916),(1.4614,6.9885,3.8774),(2.7,9.4,3.89),(1.3,12.2,3.89),tuple(new)]]
for i in [4,5]:
 o=bpy.data.objects[f'T01_roof_hem_{i}'];a=upper[i];b=upper[(i+1)%6];o.location=(a+b)/2;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.dimensions.z=(b-a).length
proj={}
for i in [1,2]:
 v=world_to_camera_view(s,bpy.data.objects[f'SOURCE_CONDITIONAL_{i}'],new);proj[str(i)]=[v.x*1920,(1-v.y)*1080,v.z]
report={'stage':'R08b conditional roof boundary trial + chair, bags still R07','roof_control_world_working_units':list(new),'old_control':list(old),'native_projections':proj,'control_evidence':'source1 observed contour around 294,104; source2 top cropped. Assumed y=10, not measured depth or second apex. Shared roof/skirt/hem joins follow one control.','geometry_not_accepted':True,'source_cameras':'unchanged','third':'not used to fit; left cropped; previously seen'}
(out/'R08b_roof_report.json').write_text(json.dumps(report,indent=2));bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(r/'models/R08b_roof_trial.blend'))
s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.use_denoising=False;s.cycles.samples=8;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=50
for role in ['materials','white']:
 if role=='white':
  m=bpy.data.materials.new('R08b_white');m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.65,.65,.65,1)
  for o in s.objects:
   if o.type in {'MESH','CURVE'}:o.data.materials.clear();o.data.materials.append(m)
 for i in [1,2]:
  s.camera=bpy.data.objects[f'SOURCE_CONDITIONAL_{i}'];s.render.filepath=str(out/f'R08b_source{i}_{role}_960.png');bpy.ops.render.render(write_still=True)
print('R08B_DONE')
