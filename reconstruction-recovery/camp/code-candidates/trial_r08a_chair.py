import bpy,json,math,hashlib
from mathutils import Vector
from pathlib import Path
r=Path(__file__).resolve().parents[1];out=r/'qa/R08_trial';out.mkdir(exist_ok=True)
p=r/'models/R07_camp_materials.blend';before=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene
s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.use_denoising=False;s.cycles.samples=8;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=50;s.render.use_border=False;s.render.use_crop_to_border=False
cams={n:[list(row) for row in bpy.data.objects[n].matrix_world] for n in ['SOURCE_CONDITIONAL_1','SOURCE_CONDITIONAL_2']}
o=bpy.data.objects['C01_sling_fabric'];old=[v.co.copy() for v in o.data.vertices];top=sum(old[:19],Vector())/19;end=sum(old[-19:],Vector())/19;axis=(old[18]-old[0]).normalized();front=end-top;front.z=0;front.normalize()
# Piecewise smooth sag profile: shape hypothesis, not recovered cloth physics.
knots=[(0,0,1.12),(.48,.18,.57),(.78,.53,.405),(1,.69,.48)]
for a in range(19):
 t=a/18
 for k in range(len(knots)-1):
  if knots[k][0]<=t<=knots[k+1][0]:break
 A,B=knots[k],knots[k+1];u=(t-A[0])/(B[0]-A[0]);u=u*u*(3-2*u);offset=A[1]*(1-u)+B[1]*u;z=A[2]*(1-u)+B[2]*u
 for b in range(19):
  v=b/18;P=top+axis*((v-.5)*.9)+front*offset;P.z=z-.045*math.sin(math.pi*v)*math.sin(math.pi*t);o.data.vertices[a*19+b].co=P
for b in [0,18]:
 c=bpy.data.curves.new('R08_cloth_side_hem','CURVE');c.dimensions='3D';c.bevel_depth=.012;c.bevel_resolution=2;c.use_fill_caps=True;sp=c.splines.new('POLY');sp.points.add(18)
 for a in range(19):P=o.data.vertices[a*19+b].co;sp.points[a].co=(*P,1)
 h=bpy.data.objects.new('C01_R08_side_hem_'+str(b),c);s.collection.objects.link(h);c.materials.append(o.data.materials[0])
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(r/'models/R08a_chair_trial.blend'))
report={'stage':'R08a only chair trial, roof/bag still R07','not_accepted':True,'profile':knots,'source_cameras_unchanged':all(cams[n]==[list(row) for row in bpy.data.objects[n].matrix_world] for n in cams),'R07_original_bytes_unchanged':before==hashlib.sha256(p.read_bytes()).hexdigest(),'top_corners_displacement':[(o.data.vertices[i].co-old[i]).length for i in [0,18]],'front_cloth_z':.48,'crossed_supports':'unchanged','minimum_cloth_z':min(v.co.z for v in o.data.vertices),'third':'seen, not used to fit this trial; not fresh holdout'}
(out/'R08a_geometry_report.json').write_text(json.dumps(report,indent=2))
for role in ['materials','white']:
 if role=='white':
  m=bpy.data.materials.new('R08_trial_white');m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.65,.65,.65,1)
  for ob in s.objects:
   if ob.type in {'MESH','CURVE'}:ob.data.materials.clear();ob.data.materials.append(m)
 for i in [1,2]:
  s.camera=bpy.data.objects[f'SOURCE_CONDITIONAL_{i}'];s.render.filepath=str(out/f'R08a_source{i}_{role}_960.png');bpy.ops.render.render(write_still=True)
print('R08A_DONE')
