import bpy,json,time,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
r=Path(__file__).resolve().parents[1];out=r/'versions/R01D';bpy.ops.wm.open_mainfile(filepath=str(out/'ring-remake-R01D-material.blend'));s=bpy.context.scene
cameras=[('source4k','C_4K_CONDITIONAL',3840,2160),('front','C_FRONT_CONDITIONAL',1920,1080),('oblique','C_OBLIQUE_UNCALIBRATED',1920,1080)]
rows=[]
for o in sorted(s.objects,key=lambda x:x.name):
 if o.type!='MESH':continue
 cat='inferred repeated fixture/count'
 if o.name.startswith('P_'):cat='source platform layer, dimensions/camera conditional'
 elif o.name.startswith('ARCH_'):cat='broad arch source group, circle/depth/lower closure conditional'
 elif o.name.startswith('SIDE_MAIN'):cat='main coarse arc distinct from small loop, endpoints/foundations unknown'
 elif o.name.startswith('SIDE_SMALL'):cat='small marked arc separate group, exact tilt/closure unknown'
 elif o.name.startswith('STAR'):cat='multi-chain graphic/rod identity and static state uncertain; NOT camera anchor'
 elif o.name.startswith('LED_'):cat='source segmented background, count/backside/radius and authored texture inferred'
 elif o.name.startswith('DARK_WEDGE'):cat='two dark wedge group visible in new60s, dimensions/placement conditional'
 rows.append({'id':o.name,'type':cat,'source_frames':'three reacquired Nov2 training frames, original time/hash in sources manifests','model_bounds':[[min((o.matrix_world@Vector(v))[j] for v in o.bound_box) for j in range(3)],[max((o.matrix_world@Vector(v))[j] for v in o.bound_box) for j in range(3)]],'source_acceptance':'NOT VERIFIED','unknown':'actual dimensions, material equality, contacts/occlusions/instances not independently accepted'})
(r/'qa/R01D-object-evidence-inventory.json').write_text(json.dumps({'objects':rows,'count':len(rows),'missing_or_unresolved':['ring side outer foundations and hidden continuation','middle and largest arc full silhouette','star chain state/identity','individual accent/fixture count','floor source texture/reflections and stage text waist','background exact layout and rear faces','later independent replay confirmation','oblique camera calibration'],'no_hidden_geometry_certificate':True},indent=2))
progress=[]
def render(name,camera,w,h):
 s.camera=bpy.data.objects[camera];s.render.resolution_x=w;s.render.resolution_y=h;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.samples=32;s.cycles.use_denoising=False;s.render.filepath=str(out/(name+'.png'));t=time.time();bpy.ops.render.render(write_still=True);p=out/(name+'.png');progress.append({'file':p.name,'size':[w,h],'seconds':time.time()-t,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'camera':camera,'threads':2,'samples':32});(r/'qa/R01D-render-progress.json').write_text(json.dumps(progress,indent=2));print('STAGE_FILE_DONE',name,flush=True)
for i in range(1,9):render('check_%02d'%i,'CHECK_%02d'%i,1280,720)
for n,c,w,h in cameras:render(n+'-material-native',c,w,h)
bpy.ops.wm.open_mainfile(filepath=str(out/'ring-remake-R01D-white-same-geometry.blend'));s=bpy.context.scene
for n,c,w,h in cameras:render(n+'-white-native',c,w,h)
print('R01D_SUITE_COMPLETE',flush=True)
