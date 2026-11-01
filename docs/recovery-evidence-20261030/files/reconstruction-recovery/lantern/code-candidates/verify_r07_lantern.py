import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[1];Q=D/'qa/R07_lantern'
def snap():
 out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  p=[o.matrix_world@v.co for v in o.data.vertices];out[o.name]={'bounds':[[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]],'geo':hashlib.sha256(str(([list(v.co) for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons],[list(r) for r in o.matrix_world])).encode()).hexdigest()}
 return out
result={};original={}
for typ in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R07_lantern_trial_{typ}.blend'));original[typ]=a=snap();top={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or not o.name.startswith(('LANTERN_round_R0','LANTERN_string0_10')):continue
  uses={}
  for f in o.data.polygons:
   for e in f.edge_keys:uses[e]=uses.get(e,0)+1
  top[o.name]={'boundary_edges':sum(x==1 for x in uses.values()),'nonmanifold_edges':sum(x!=2 for x in uses.values())}
 result[typ+'_detail_topology']=top
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(D/f'models/R07_lantern_trial_{typ}.glb'));b=snap();common=set(a)&set(b);result[typ+'_roundtrip']={'source_count':len(a),'reimport_count':len(b),'missing':sorted(set(a)-set(b)),'extra':sorted(set(b)-set(a)),'max_bbox_error':max(abs(a[n]['bounds'][j][k]-b[n]['bounds'][j][k]) for n in common for j in range(2) for k in range(3))}
result['same_white_material_geometry']=original['material']==original['white'];result['scope']='transport and edge closure only; collars/ribs intentionally overlap body; no exhaustive source acceptance or intersection certification'
(Q/'roundtrip.json').write_text(json.dumps(result,indent=2))
# Separate native-pixel source-camera crop of small representative; no camera transform or lens changes.
for label,model in [('before','R06b_column_trial_material'),('after','R07_lantern_trial_material'),('white','R07_lantern_trial_white')]:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/{model}.blend'));s=bpy.context.scene;s.render.threads=2;s.cycles.samples=24;s.camera=bpy.data.objects['SOURCE1'];s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=850/1920;s.render.border_max_x=1020/1920;s.render.border_min_y=1-345/1080;s.render.border_max_y=1-190/1080;s.render.filepath=str(D/f'renders/R07_{label}_long_SOURCE1_nativecrop.png');bpy.ops.render.render(write_still=True)
# Object inspection only: remove occluding scene for visibility, not source-camera evidence. No saved model edits.
for typ in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R07_lantern_trial_{typ}.blend'));s=bpy.context.scene;s.render.threads=2;s.cycles.samples=24;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=512;s.render.resolution_y=512
 selected=[o for o in s.objects if o.type=='MESH' and o.name.startswith('LANTERN_round_R0')]
 for o in s.objects:
  if o.type=='MESH':o.hide_render=o not in selected
 p=[o.matrix_world@v.co for o in selected for v in o.data.vertices];center=Vector([(min(v[i] for v in p)+max(v[i] for v in p))/2 for i in range(3)]);cam=bpy.data.cameras.new('R07_INSPECTION_ONLY');ob=bpy.data.objects.new(cam.name,cam);s.collection.objects.link(ob);ob.location=center+Vector((2,-4,1));ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler();cam.type='ORTHO';cam.ortho_scale=2;s.camera=ob;s.render.filepath=str(D/f'renders/R07_round_INSPECTION_ONLY_{typ}.png');bpy.ops.render.render(write_still=True)
