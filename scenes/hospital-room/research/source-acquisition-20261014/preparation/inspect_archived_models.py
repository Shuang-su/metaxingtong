"""Read-only Blender inspection. Never changes/saves/renders the loaded model."""
import bpy,json,sys,hashlib
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];dest=Path(args[0]);scene=bpy.context.scene
file=Path(bpy.data.filepath)
names=['Window • calibrated vertical mullion.002','Window • calibrated vertical mullion.003','Curtain rail • forward overhead beam','Curtain rail • forward overhead beam.001','Curtain • rebuilt uniform eight-fold drape','J1 • beige window pillar bounded projection','J1 • inferred end cross-connector','Bed • mattress and sheet','Bed • observed endboard, consistent width','Bed • inferred low foot bumper','Bed • integrated side rail','Bed • integrated side rail.001','TV • rectangular black frame','ROOM_SHELL__joined_solid__hidden_extents_inferred']
out={'status':'READ_ONLY_ARCHIVE_INSPECTION_NOT_SOURCE_VALIDATION','blend':file.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'world_units':'arbitrary inherited D units','meshes':{},'cameras':{}}
for cam in (o for o in bpy.data.objects if o.type=='CAMERA'):
 out['cameras'][cam.name]={'matrix_world':[list(r) for r in cam.matrix_world],'lens_mm':cam.data.lens,'sensor_width':cam.data.sensor_width,'type':cam.data.type,'status':'unaccepted inherited hypothesis'}
for name in names:
 o=bpy.data.objects.get(name)
 if not o:continue
 vs=[o.matrix_world@v.co for v in o.data.vertices];mn=[min(v[i] for v in vs) for i in range(3)];mx=[max(v[i] for v in vs) for i in range(3)]
 q={'vertex_count':len(vs),'bounds_min':mn,'bounds_max':mx,'hide_render':o.hide_render,'source_vertex_identity':'UNVERIFIED; mesh extrema are synthetic construction choices','projections':{}}
 for camname in ['MATCH_G_Sofa_And_Bed','MATCH_H','J1_G_uncalibrated','J1_H_uncalibrated','J1_A_uncalibrated','J1_B_uncalibrated','J1_F_uncalibrated']:
  cam=bpy.data.objects.get(camname)
  if not cam:continue
  pts=[world_to_camera_view(scene,cam,v) for v in vs];pts=[(p.x*1920,(1-p.y)*1080,p.z) for p in pts]
  q['projections'][camname]={'positive_depth_vertices':sum(p[2]>0 for p in pts),'screen_bounds':[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)],'first_projected_vertex':list(pts[0]),'no_visibility_test':True}
 if 'mullion.002' in name:
  # Explicit finite front-face bounds. Used for side ordering, not source vertex correspondence.
  corners={'xmin_zlow':Vector((mn[0],mn[1],mn[2])),'xmax_zlow':Vector((mx[0],mn[1],mn[2])),'xmin_zhigh':Vector((mn[0],mn[1],mx[2])),'xmax_zhigh':Vector((mx[0],mn[1],mx[2]))}
  q['projected_front_bounds']={}
  for camname in ['MATCH_G_Sofa_And_Bed','MATCH_H','J1_G_uncalibrated','J1_H_uncalibrated']:
   cam=bpy.data.objects.get(camname)
   if cam:
    q['projected_front_bounds'][camname]={}
    for key,v in corners.items():
     p=world_to_camera_view(scene,cam,v);q['projected_front_bounds'][camname][key]=[p.x*1920,(1-p.y)*1080,p.z]
 out['meshes'][name]=q
out['blend_hash_after']=hashlib.sha256(file.read_bytes()).hexdigest();out['blend_unchanged']=out['sha256']==out['blend_hash_after'];dest.write_text(json.dumps(out,ensure_ascii=False,indent=2));print('INSPECTED',dest,'UNCHANGED',out['blend_unchanged'])
