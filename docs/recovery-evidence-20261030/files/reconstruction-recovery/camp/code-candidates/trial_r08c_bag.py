import bpy,math,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1];out=r/'qa/R08_trial';bpy.ops.wm.open_mainfile(filepath=str(r/'models/R08b_roof_trial.blend'));s=bpy.context.scene
teal=bpy.data.objects['P02_duffel_lobe_0'].data.materials[0];cloth=bpy.data.objects['P02_strap_0_0.3'].data.materials[0]
for o in list(bpy.data.objects):
 if o.name.startswith('P02_'):bpy.data.objects.remove(o,do_unlink=True)
# One horizontal rounded soft bag is an explicit occlusion hypothesis, not proven count.
cx,cy=-.55,5.99;wx,dy,h=2.5,.72,1.18
v=[];f=[];N=48;M=24
def sp(x,p=.55):return math.copysign(abs(x)**p,x)
for a in range(M+1):
 t=-math.pi/2+math.pi*a/M
 for b in range(N):
  q=2*math.pi*b/N;x=wx/2*sp(math.cos(t))*sp(math.cos(q));y=dy/2*sp(math.cos(t))*sp(math.sin(q));z=max(.025,h/2+h/2*sp(math.sin(t)))-.025;v.append((cx+x,cy+y,z))
for a in range(M):
 for b in range(N):k=a*N+b;n=a*N+(b+1)%N;f.append((k,n,n+N,k+N))
me=bpy.data.meshes.new('R08_conditional_soft_bag');me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new('P02_one_horizontal_bag_HYPOTHESIS',me);s.collection.objects.link(o);me.materials.append(teal)
for p in me.polygons:p.use_smooth=True
# Two visible broad bands around rounded body; hidden rear continuation explicitly inferred.
def curve(name,pts,rad,mat):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=rad;c.bevel_resolution=2;c.use_fill_caps=True;sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 ob=bpy.data.objects.new(name,c);s.collection.objects.link(ob);c.materials.append(mat)
for x in [-.78,.78]:
 pts=[]
 # rounded rectangle cross section; working approximate band, not recovered texture.
 for k in range(65):
  q=math.tau*k/64;pts.append((cx+x,cy+(dy/2+.008)*sp(math.cos(q)),max(.008,(h-.025)/2+(h-.025)/2*sp(math.sin(q)))))
 curve('P02_vertical_band_'+str(x),pts,.022,cloth)
# Visible horizontal seam, no fictitious logo or printed features.
for z in [.43,.91]:
 pts=[]
 for k in range(65):q=math.tau*k/64;pts.append((cx+(wx/2+.003)*sp(math.cos(q)),cy+(dy/2+.003)*sp(math.sin(q)),z))
 curve('P02_horizontal_seam_'+str(z),pts,.006,cloth)
(out/'R08c_bag_report.json').write_text(json.dumps({'hypothesis':'one horizontal soft bag occluded by standing crate; object count/hidden middle and back not established','working_dimensions':[wx,dy,h],'ground_body_min_z':min(p[2] for p in v),'geometry_source_cameras':'all other geometry and cameras unchanged from R08b','source_evidence':'same teal curved ends either side of crate and vertical wrapping bands in both source images; source crops are enlarged review only, never native evidence','not_accepted':True},indent=2));bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(r/'models/R08c_bag_trial.blend'))
s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.use_denoising=False;s.cycles.samples=8;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=50
for role in ['materials','white']:
 if role=='white':
  m=bpy.data.materials.new('R08c_white');m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.65,.65,.65,1)
  for o in s.objects:
   if o.type in {'MESH','CURVE'}:o.data.materials.clear();o.data.materials.append(m)
 for i in [1,2]:s.camera=bpy.data.objects[f'SOURCE_CONDITIONAL_{i}'];s.render.filepath=str(out/f'R08c_source{i}_{role}_960.png');bpy.ops.render.render(write_still=True)
print('R08C_DONE')
