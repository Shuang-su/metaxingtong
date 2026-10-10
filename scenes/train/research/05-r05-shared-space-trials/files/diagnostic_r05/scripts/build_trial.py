import bpy,json,hashlib,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];src=R.parent/'frozen_r03/train_hd_r03_material_f0cd84d2a8ab.blend';assert hashlib.sha256(src.read_bytes()).hexdigest()=='f0cd84d2a8abff5e2597fc986b01279889e239c7c589a63991ba68632b0b3a7c'
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
fit=json.loads((R/'analysis/rack_cross_section_fit.json').read_text())['shared_head_and_rack_height'];jfit=json.loads((R/'analysis/J_empty_plane_fit.json').read_text())['compressed_window']
# Conservative rounded working-unit candidate from the fits, not physical surveyed dimensions.
bot,top=1.08,1.725;head=1.787;rackx,rackz=1.068,1.925
oldbot,oldtop=.9625,2.0975
# Continuous, strictly increasing vertical map. Sidewall outer floor/roof boundaries fixed.
def wallz(z):
 if z<0:return z
 if z<=oldbot:return z*bot/oldbot
 if z<=oldtop:return bot+(z-oldbot)*(top-bot)/(oldtop-oldbot)
 if z<=2.42:return top+(z-oldtop)*(2.42-top)/(2.42-oldtop)
 return z
wallprefix=('Lower walnut wainscot','Window sill wooden rail','Upper walnut header','Lower dado cap brass','Walnut wall pier','Corner wall infill','Window ','Coat hook ','Red gathered curtain','Curtain ','Left full sidewall','Right full sidewall')
changed=[];rigid=[]
for o in s.objects:
 if o.type=='MESH' and o.name.startswith(wallprefix):
  m=o.matrix_world.copy();iv=m.inverted();o.data=o.data.copy()
  for v in o.data.vertices:
   p=m@v.co
   if o.name.startswith('Window head warm strip'):
    p.z+=head-2.107
   elif o.name.startswith('Window mid sash'):
    # Same global vertical map as the wall; sash fraction intentionally reserved for independent check.
    p.z=wallz(p.z)
   else:p.z=wallz(p.z)
   v.co=iv@p
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free();o.data.update();changed.append(o.name)
 if o.type=='MESH' and o.name.startswith(('Rack ','Luggage ')):
  m=o.matrix_world.copy();iv=m.inverted();o.data=o.data.copy()
  for v in o.data.vertices:
   p=m@v.co;sign=1 if p.x>0 else -1;p.x=sign*(rackx+(abs(p.x)-.88)*(1.43-rackx)/(1.43-.88));p.z+=rackz-2.19;v.co=iv@p
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free();o.data.update();changed.append(o.name)
 if o.type=='LIGHT' and o.name.startswith('Window header soft lamp'):
  o.location.z+=head-2.107;changed.append(o.name)
# All original cameras stay byte-equivalent in transforms. New fitted views separate from r03.
for k in ['A','B','D']:
 c=fit['cameras'][k]['camera'];old=bpy.data.objects['HD_'+k];o=old.copy();o.data=old.data.copy();s.collection.objects.link(o);o.name='R05_HD_'+k;o.location=c[:3];o.rotation_euler=c[3:6];o.data.lens=c[6]
old=bpy.data.objects['HD_J'];o=old.copy();o.data=old.data.copy();s.collection.objects.link(o);o.name='R05_J_LOCAL_UNRESOLVED_BAY';c=jfit['camera_24mm_gauge'];o.location=c[:3];o.rotation_euler=c[3:6];o.data.lens=24;o['Scope']='Local window metric test only; physical side and absolute bay not solved.'
s['Candidate_status']='r05 shared sidewall/window/rack proportion trial; NOT source accepted; r03 preserved.'
s['Shared_change']='Window vertical band shortened 0.9625..2.0975 -> 1.08..1.725; all sidewall layers mapped continuously; head fixtures lowered to1.787; rack inner rail x1.068/z1.925, outer rail x1.43 fixed; no Y, furniture, ceiling, door, material changes.'
s.camera=bpy.data.objects['R05_HD_A'];s.render.threads_mode='FIXED';s.render.threads=2
out=R/'trial_r05_shared.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out));h=hashlib.sha256(out.read_bytes()).hexdigest();dest=R/f'trial_r05_shared_{h[:12]}.blend';out.rename(dest);dest.chmod(0o444)
meta={'input_r03_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'file':str(dest),'sha256':h,'changed_objects':changed,'window_bounds':[bot,top],'head_fixture_z':head,'rack_inner_x':rackx,'rack_z':rackz,'unchanged':'floor/roof/end walls/door; all furniture transforms; longitudinal positions/pitch; materials; r03 historical cameras; no per-camera hide/swap','caveat':'continuous sidewall map changes wall trim/curtain proportions too; check support/apertures before any handoff; sash remains heldout'}
(R/'analysis/trial_manifest.json').write_text(json.dumps(meta,indent=2));print('FROZEN TRIAL',dest,h,len(changed))
