import bpy,json,time,hashlib
from pathlib import Path
R=Path(__file__).parent;OUT=R/'diagnostic_outputs';s=bpy.context.scene
S=json.load(open(R/'joint_candidate_screening.json'))['selected']; H=json.load(open(R/'heldout_camera_validation.json'))['views'];cams={**S['cameras'],**{k:v['camera'] for k,v in H.items()}}
manifest=json.load(open(OUT/'render_manifest.json'))
for e in manifest:e['denoising_requested_global']=e.pop('denoising',True);e['view_layer_denoising']=False;e['actual_output']='RAW; per-view-layer denoising disabled'
(OUT/'render_manifest.json').write_text(json.dumps(manifest,indent=2))
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.seed=0;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=True
for v in s.view_layers:v.cycles.use_denoising=False
mats={o.name:list(o.data.materials) for o in bpy.data.objects if o.type=='MESH'};white=bpy.data.materials.get('J1 QA matte white')
if not white:
 white=bpy.data.materials.new('J1 QA matte white');white.use_nodes=True;bs=white.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.72,.72,.72,1);bs.inputs['Roughness'].default_value=.8

def fingerprint():return hashlib.sha256(json.dumps({o.name:{'hide_render':o.hide_render,'verts':[tuple(o.matrix_world@v.co) for v in o.data.vertices]} for o in bpy.data.objects if o.type=='MESH'},sort_keys=True).encode()).hexdigest()
for mode in ['material','white']:
 s.cycles.samples=32 if mode=='material' else 16
 if mode=='white':
  for o in bpy.data.objects:
   if o.type=='MESH' and 'closed_glass' not in o.name and not o.name.startswith('Approximate city'):o.data.materials.clear();o.data.materials.append(white)
  s.camera=bpy.data.objects['J1_G_uncalibrated'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'hospital_joint_J1_REJECTED_white.blend'))
 for k in ['G','H']:
  f=OUT/f'{k}_J1_REJECTED_{mode}_1920x1080.png'
  if any(e['file']==f.name and f.exists() for e in manifest):continue
  s.camera=bpy.data.objects['J1_'+k+'_uncalibrated'];s.render.filepath=str(f);a=fingerprint();t=time.time();bpy.ops.render.render(write_still=True);b=fingerprint()
  manifest.append({'stage':'J1_REJECTED','mode':mode,'view':k,'file':f.name,'size':[1920,1080],'samples':s.cycles.samples,'denoising_requested_global':True,'view_layer_denoising':False,'actual_output':'RAW; per-view-layer denoising disabled','engine':'Cycles CPU','threads':2,'camera':cams[k],'same_camera_before_after':True,'geometry_fingerprint_before':a,'geometry_fingerprint_after':b,'fingerprint_equal':a==b,'seconds':time.time()-t,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()});(OUT/'render_manifest.json').write_text(json.dumps(manifest,indent=2))
# Geometry inventory, full scene retained.
g=S['geometry'];pj=1.521875;pr=pj+g['pillar_width'];rx=pj+g['pillar_width']*g['rail_pillar_fraction'];wy=g['window_y'];front=wy-g['pillar_projection']
qa={'status':'REJECTED_DIAGNOSTIC','coordinate_units':'D units, not measured meters','unchanged_bed_length':2.73643696,'pillar_x':[pj,pr],'pillar_y':[front,wy],'black_jamb_x':[1.478125,1.521875],'pillar_black_x_overlap':max(0,min(pr,1.521875)-max(pj,1.478125)),'rail_connector_pillar_x_overlap':min(pr,rx+.018)-max(pj,rx-.018),'source_fidelity_passed':False,'meshes':[]}
for o in bpy.data.objects:
 if o.type!='MESH':continue
 vv=[o.matrix_world@v.co for v in o.data.vertices];qa['meshes'].append({'name':o.name,'vertices':len(vv),'min':[min(v[i] for v in vv) for i in range(3)],'max':[max(v[i] for v in vv) for i in range(3)],'hide_render':o.hide_render})
(OUT/'geometry_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));print('RESUME COMPLETE: 8/8 rendered; all raw')
