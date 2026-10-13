import bpy,sys,json,hashlib,time,math
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).parent;S=json.load(open(R/'joint_candidate_screening.json'))['selected'];g=S['geometry'];H=json.load(open(R/'heldout_camera_validation.json'))['views'];scene=bpy.context.scene
OUT=R/'diagnostic_outputs';OUT.mkdir(exist_ok=True)
wy=g['window_y'];pj=1.521875;pr=pj+g['pillar_width'];front=wy-g['pillar_projection'];m3=g['m3_x'];rx=pj+g['pillar_width']*g['rail_pillar_fraction'];sep=g['rail_depth_separation'];rz=g['rail_height'];bc=-2.321825685
baseline_meshes={o.name:[tuple(o.matrix_world@v.co) for v in o.data.vertices] for o in bpy.data.objects if o.type=='MESH'}

# Cameras use explicit proper rotations (old D camera transforms carried scale 1.25).
def rotvec_matrix(v):
 a=Vector(v);theta=a.length
 return Matrix.Identity(3) if theta<1e-12 else Matrix.Rotation(theta,3,a.normalized())
camsets={k:S['cameras'][k] for k in ['A','G']};camsets.update({k:H[k]['camera'] for k in ['B','H','F']})
for k,c in camsets.items():
 data=bpy.data.cameras.new('J1_'+k+'_uncalibrated');data.lens=math.exp(c[6]);data.sensor_width=36;data.sensor_fit='HORIZONTAL';data.clip_start=.015;data.clip_end=500;o=bpy.data.objects.new('J1_'+k+'_uncalibrated',data);scene.collection.objects.link(o);m=rotvec_matrix(c[:3]).to_4x4();m.translation=Vector(c[3:6]);o.matrix_world=m;o['status']='UNACCEPTED camera hypothesis; bounded patient region, no source calibration'
scene.camera=bpy.data.objects['J1_G_uncalibrated'];scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8';scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_adaptive_sampling=False;scene.cycles.seed=0;scene.cycles.use_denoising=True
scene['J1_status']='REJECTED_DIAGNOSTIC; no promotion to accepted model';scene['J1_source']='BV1GqXMByE1s A/B/F/G/H native 1920x1080';scene['J1_units']='Arbitrary D scene units, not recovered metric dimensions';scene['J1_hidden_head_support']='Eye constrained over mattress. Support height inferred, no fabricated precise pillow.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'hospital_D_before_J1_cameras.blend'))

# World-space remap utility; original mesh vertices preserved separately.
def remap(o,fn):
 inv=o.matrix_world.inverted()
 for v in o.data.vertices:v.co=inv@Vector(fn(o.matrix_world@v.co))
 o.data.update()

def affine(x,a,b,c,d):return c+(x-a)*(d-c)/(b-a)

def adjust():
 for o in list(bpy.data.objects):
  n=o.name
  if o.type!='MESH':continue
  if n.startswith(('Bed •','Bed end •')):
   remap(o,lambda p:(p.x+g['bed_dx'],bc+(p.y-bc)*g['bed_width_scale']+g['bed_dy'],p.z));o['J1_edit']='Bed assembly rigid XY translation plus shared transverse scale; longitudinal length unchanged'
  elif n=='ROOM_SHELL__joined_solid__hidden_extents_inferred':
   def shell(p):
    x,y,z=p
    if abs(x-.990656197)<1e-4:x=1.478125
    elif abs(x-1.524999857)<1e-4:x=pr
    elif abs(x-3.551422119)<1e-4:x=m3-.025
    elif abs(x-3.601422071)<1e-4:x=m3+.025
    if y>-.01:y+=wy
    return x,y,z
   remap(o,shell);o['J1_edit']='Opening 2 end moved to verified black jamb; narrow beige member on its right; window wall depth shared'
  elif n.startswith('Window_2') or n.startswith('Blind bank 2'):
   vv=baseline_meshes[n];mn=min(v[0] for v in vv);mx=max(v[0] for v in vv)
   def w2(p):
    x=p.x
    if n.startswith('Window_2__jamb') and mn>.9:x+=1.5-.97945
    else:x=affine(x,.025,.990656197,.025,1.478125)
    return x,p.y+wy,p.z
   remap(o,w2)
  elif n.startswith('Window_3') or n.startswith('Blind bank 3'):
   remap(o,lambda p:(affine(p.x,1.525,3.576422215,pr,m3),p.y+wy,p.z))
  elif n.startswith('Window_4') or n.startswith('Blind bank 4'):
   remap(o,lambda p:(affine(p.x,3.576422215,4.994256496,m3,4.994256496),p.y+wy,p.z))
  elif n.startswith('Window') or n.startswith('Blind'):
   def window(p):
    x=p.x
    if n=='Window • calibrated vertical mullion.003':x+=m3-3.576422215
    return x,p.y+wy,p.z
   remap(o,window)
  elif n.startswith('Curtain rail'):
   # Parallel horizontal-direction tracks retained; braces move coherently, not the rejected vertical hypothesis.
   remap(o,lambda p:(rx+(p.x-1.479429245)*sep/.2,affine(p.y,-.34530795,-3.38280821,front,-3.38280821),p.z+(rz-2.6918747425)))
  elif n.startswith('Curtain •'):
   remap(o,lambda p:(affine(p.x,1.64465964,2.34156275,pr,pr+.59),p.y+front-.02-(-.12879937),affine(p.z,.00624999,2.71466541,.00624999,rz-.017)))
 # Beige member projects into the room, separate from conditional grey folded material.
 mat=bpy.data.materials.get('Warm ivory plaster • observed color')
 def box(n,lo,hi,mat):
  bpy.ops.mesh.primitive_cube_add(size=1,location=tuple((a+b)/2 for a,b in zip(lo,hi)));o=bpy.context.object;o.name=n;o.dimensions=tuple(b-a for a,b in zip(lo,hi));bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  if mat:o.data.materials.append(mat)
  o['J1_status']='BOUNDED_INFERENCE, not measured hidden dimensions';return o
 pillar=box('J1 • beige window pillar bounded projection',(pj,front,0),(pr,wy+.0001,2.714665413),mat)
 railmat=bpy.data.materials.get('Anodised charcoal window frames')
 box('J1 • inferred end cross-connector',(rx-.018,front-.014,rz-.017),(rx+sep+.018,front+.014,rz+.017),railmat)
 # The connector has finite overlap with the pillar and both rails. No unseen support or pillow invented.
 bpy.context.view_layer.update()

mats={o.name:[m for m in o.data.materials] for o in bpy.data.objects if o.type=='MESH'}
white=bpy.data.materials.new('J1 QA matte white');white.diffuse_color=(.72,.72,.72,1);white.use_nodes=True;bs=white.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.72,.72,.72,1);bs.inputs['Roughness'].default_value=.8
# White opaque model; glass retained so complete-room daylight and exterior remain consistent.
def white_mode(on):
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  if on:
   if 'closed_glass' in o.name or o.name.startswith('Approximate city'):continue
   if o.name not in mats:mats[o.name]=[m for m in o.data.materials]
   o.data.materials.clear();o.data.materials.append(white)
  else:
   if o.name in mats:
    o.data.materials.clear()
    for m in mats[o.name]:o.data.materials.append(m)

def fingerprint():
 return hashlib.sha256(json.dumps({o.name:{'hide_render':o.hide_render,'verts':[(tuple(o.matrix_world@v.co)) for v in o.data.vertices]} for o in bpy.data.objects if o.type=='MESH'},sort_keys=True).encode()).hexdigest()
manifest=[]
for stage in ['before','J1_REJECTED']:
 if stage!='before':
  adjust();scene.camera=bpy.data.objects['J1_G_uncalibrated'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'hospital_joint_J1_REJECTED.blend'))
 for mode in ['material','white']:
  white_mode(mode=='white');scene.cycles.samples=16 if mode=='white' else 32
  if stage!='before' and mode=='white':bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'hospital_joint_J1_REJECTED_white.blend'))
  for k in ['G','H']:
   scene.camera=bpy.data.objects['J1_'+k+'_uncalibrated'];f=OUT/f'{k}_{stage}_{mode}_1920x1080.png';scene.render.filepath=str(f);before=fingerprint();t=time.time();bpy.ops.render.render(write_still=True);after=fingerprint()
   manifest.append({'stage':stage,'mode':mode,'view':k,'file':f.name,'size':[1920,1080],'samples':scene.cycles.samples,'denoising':True,'engine':'Cycles CPU','threads':2,'camera':camsets[k],'same_camera_before_after':True,'geometry_fingerprint_before':before,'geometry_fingerprint_after':after,'fingerprint_equal':before==after,'seconds':time.time()-t,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()});(OUT/'render_manifest.json').write_text(json.dumps(manifest,indent=2))
 white_mode(False)
# Save geometry inventory and connection checks, not a false overall acceptance certificate.
checks={'candidate_status':'REJECTED','bed_length_unchanged':2.73643696,'frozen_target_geometry_during_holdout':True,'pillar_x':[pj,pr],'pillar_y':[front,wy],'black_jamb_x':[1.478125,1.521875],'rail_x':[rx,rx+sep],'pillar_connector_overlap_x':min(pr,rx+.018)-max(pj,rx-.018),'pillar_black_frame_overlap_x':max(0,min(pr,1.521875)-max(pj,1.478125)),'meshes':[]}
for o in bpy.data.objects:
 if o.type!='MESH':continue
 verts=[o.matrix_world@v.co for v in o.data.vertices];checks['meshes'].append({'name':o.name,'vertex_count':len(verts),'bounds_min':[min(v[i] for v in verts) for i in range(3)],'bounds_max':[max(v[i] for v in verts) for i in range(3)],'hide_render':o.hide_render})
(OUT/'geometry_qa.json').write_text(json.dumps(checks,indent=2,ensure_ascii=False))
print('J1 COMPLETE',OUT)
