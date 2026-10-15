"""Create reversible D-derived diagnostic stages. Never overwrites archive or CURRENT.
Run: blender -b path/to/hospital_D_before_J1_cameras.blend -t 4 --python build_candidates.py
"""
import bpy,json,hashlib,time
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).parent;P=json.load(open(R/'C2_selected_parameters.json'));s=bpy.context.scene;models=R/'models';models.mkdir(exist_ok=True);raw=R/'renders_C2';raw.mkdir(exist_ok=True)
basehash=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();changes=[]
def remap(o,fn):
 inv=o.matrix_world.inverted()
 for v in o.data.vertices:v.co=inv@Vector(fn(o.matrix_world@v.co))
 o.data.update()

def fingerprint():
 return hashlib.sha256(json.dumps({o.name:{'hide_render':o.hide_render,'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons]} for o in bpy.data.objects if o.type=='MESH'},sort_keys=True).encode()).hexdigest()
def save(name):
 s['candidate_status']='UNACCEPTED; explicit assumptions; never promoted to CURRENT';s['source_base_SHA256']=basehash;bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(models/name));changes.append({'file':name,'mesh_fingerprint':fingerprint(),'sha256':hashlib.sha256((models/name).read_bytes()).hexdigest()});(R/'stage_manifest.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2))
def box(n,lo,hi,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=tuple((a+b)/2 for a,b in zip(lo,hi)));o=bpy.context.object;o.name=n;o.dimensions=tuple(b-a for a,b in zip(lo,hi));bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if mat:o.data.materials.append(mat)
 o['evidence_status']='INFERRED cross-section/depth; source supports member presence and rail connection, not hidden shape';return o

# Camera carries a source-relative rotation hypothesis, no furniture was used.
c=P['cameras']['N640'];d=bpy.data.cameras.new('C2_N640_static_background_hypothesis');d.lens=c['lens'];d.sensor_width=36;d.sensor_fit='HORIZONTAL';d.clip_start=.015;d.clip_end=500;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.matrix_world=Matrix(c['matrix']);o['status']='CONDITIONAL pure-rotation/focal camera; bed eye position unverified'
# Physical stage: whole drape moved coherently in every view.
o=bpy.data.objects['Curtain • rebuilt uniform eight-fold drape'];remap(o,lambda p:(p.x,p.y-.04011060774326324,p.z));o['C2_edit']='P0 global Y=-0.04011060774326324 to separate from all bank3 slats and lift strings; 0.005 inferred scene-unit clearance';save('hospital_P0_drape_clearance_UNACCEPTED.blend')
# Column stage: preserve the D opening; add explicit conditional beige member and end connector.
mat=bpy.data.materials.get('Warm ivory plaster • observed color');x0=1.521875023841858;x1=1.6446596384048462
box('C2 • inferred beige column right of central black frame',(x0,-.36,0),(x1,0,2.714665412902832),mat)
box('C2 • inferred rail end cross connector',(1.46,-.360307946,2.674999714),(1.70,-.330307946,2.708749771),bpy.data.materials.get('Anodised charcoal window frames'))
for o in bpy.data.objects:
 if o.type!='MESH':continue
 if o.name.startswith('Blind bank 3 • physical slat'):
  oldlo=min((o.matrix_world@v.co).x for v in o.data.vertices);oldhi=max((o.matrix_world@v.co).x for v in o.data.vertices);newlo=x1+.005
  remap(o,lambda p,lo=oldlo,hi=oldhi:(newlo+(p.x-lo)*(hi-newlo)/(hi-lo),p.y,p.z));o['C2_edit']='Shared bank3 left endpoint shortened to clear inferred column; count/right endpoint unchanged'
 elif o.name.startswith('Window_3__sill_or_lintel'):
  oldlo=min((o.matrix_world@v.co).x for v in o.data.vertices);oldhi=max((o.matrix_world@v.co).x for v in o.data.vertices)
  remap(o,lambda p,lo=oldlo,hi=oldhi:(x1+(p.x-lo)*(hi-x1)/(hi-lo),p.y,p.z));o['C2_edit']='Left sill/lintel endpoint meets inferred column; rest unchanged'
save('hospital_P1_column_connection_UNACCEPTED.blend')
# Cushion stage: only left-back low-amplitude top taper adopted. Right-back bound-hitting fit rejected.
for n,delta in P['geometry_parameters'].items():
 if max(abs(t) for t in delta)<1e-10:continue
 o=bpy.data.objects[n];z0=min((o.matrix_world@v.co).z for v in o.data.vertices);z1=max((o.matrix_world@v.co).z for v in o.data.vertices)
 remap(o,lambda p,d=delta:(p.x+(p.z-z0)/(z1-z0)*d[0],p.y+(p.z-z0)/(z1-z0)*d[1],p.z+(p.z-z0)/(z1-z0)*d[2]));o['C2_edit']='Fixed-bottom tapered XYZ correction from same G/H top/side branches; all cameras share mesh'
s.camera=bpy.data.objects['MATCH_G_Sofa_And_Bed'];save('hospital_C2_small_shared_geometry_UNACCEPTED.blend')
# White file: identical mesh/world matrices/visibility; only material substitutions.
mats={o.name:list(o.data.materials) for o in bpy.data.objects if o.type=='MESH'};w=bpy.data.materials.new('C2 white geometry inspection');w.diffuse_color=(.72,.72,.72,1);w.use_nodes=True;bs=w.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.72,.72,.72,1);bs.inputs['Roughness'].default_value=.8
for o in bpy.data.objects:
 if o.type=='MESH' and 'closed_glass' not in o.name and not o.name.startswith('Approximate city'):
  o.data.materials.clear();o.data.materials.append(w)
save('hospital_C2_small_shared_geometry_WHITE_UNACCEPTED.blend')
for o in bpy.data.objects:
 if o.type=='MESH':
  o.data.materials.clear()
  for m in mats[o.name]:o.data.materials.append(m)
# Full scene renders: no visibility/geometry switches, warp, registration, or crop.
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=True; s.view_layers[0].cycles.use_denoising=False; # inherited raw-noise layer state, explicitly retained
s.cycles.seed=0;s.render.threads_mode='FIXED';s.render.threads=4
manifest=[]
for k,n in [('G','MATCH_G_Sofa_And_Bed'),('H','MATCH_H'),('F','MATCH_F_Turning_Right'),('N640','C2_N640_static_background_hypothesis')]:
 s.camera=bpy.data.objects[n];s.render.filepath=str(raw/f'{k}_C2_RAW_1920x1080.png');before=fingerprint();t=time.time();bpy.ops.render.render(write_still=True);after=fingerprint();f=Path(s.render.filepath);manifest.append({'view':k,'camera':n,'camera_matrix':[list(row) for row in s.camera.matrix_world],'lens_mm':s.camera.data.lens,'file':f.name,'size':[1920,1080],'samples':16,'denoising_requested':True,'seconds':time.time()-t,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'mesh_visibility_fingerprint_before':before,'mesh_visibility_fingerprint_after':after,'same_geometry':before==after,'image_transform':'none; raw Blender output'});(raw/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('C2 BUILT',R)
