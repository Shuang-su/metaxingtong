"""Resume-safe renders; source PNGs always full native grid, no image warp/resize."""
import bpy,json,time,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'stages/r03b-mounted-review';O.mkdir(exist_ok=True)
cfgs=json.loads((O/'source-cameras.json').read_text());manifest_path=O/'render-manifest.json';manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else []
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def render(state,camera,size,path,engine,samples,role):
    global loaded
    inp=O/('harbor-r03b-'+state+'.blend');finger=sha(inp);key=str(path.relative_to(O));previous=[r for r in manifest if r['output']==key and r['input_sha256']==finger and r['engine']==engine and r['samples']==samples]
    if path.exists() and previous and sha(path)==previous[-1]['sha256']:
        print('RESUME_SKIP',key,flush=True);return
    if loaded!=state:
        bpy.ops.wm.open_mainfile(filepath=str(inp));loaded=state
    sc=bpy.context.scene;sc.render.engine=engine;sc.render.resolution_x=size[0];sc.render.resolution_y=size[1];sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.camera=bpy.data.objects[camera]
    if engine=='CYCLES':
        sc.cycles.samples=samples;sc.cycles.use_denoising=False;sc.cycles.device='CPU';sc.cycles.max_bounces=6;sc.cycles.diffuse_bounces=3;sc.cycles.glossy_bounces=3;sc.cycles.transmission_bounces=4
    elif hasattr(sc.eevee,'taa_render_samples'):sc.eevee.taa_render_samples=samples
    path.parent.mkdir(parents=True,exist_ok=True);sc.render.filepath=str(path);t=time.perf_counter();bpy.ops.render.render(write_still=True)
    rec={'output':key,'input':str(inp.relative_to(R)),'input_sha256':finger,'camera':camera,'dimensions':size,'engine':engine,'samples':samples,'role':role,'seconds':time.perf_counter()-t,'bytes':path.stat().st_size,'sha256':sha(path),'geometry_state':'r03b; shared all cameras','lighting_material_state':'canonical teal; same state for every material source camera; white is diagnostic shader replacement','camera_matrix_world':[list(row) for row in sc.camera.matrix_world],'lens':sc.camera.data.lens,'shift':[sc.camera.data.shift_x,sc.camera.data.shift_y]}
    manifest[:]=[r for r in manifest if r['output']!=key];manifest.append(rec);temp=manifest_path.with_suffix('.tmp');temp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2));temp.replace(manifest_path);print('RENDER_VERIFIED',key,rec['seconds'],flush=True)
loaded=None
# Deliver main native image first; it remains a conditional candidate, not source acceptance.
front=next(c for c in cfgs if c['id']=='preview-front')
render('material',front['camera'],front['size'],O/'source-renders/preview-front/material.png','CYCLES',96,'main source-camera native render; all-input fit, no holdout')
# Clear white inspection angles. Different engine is explicit: geometry diagnostics, not photometric proof.
for i in range(8):render('white','CHECK_%02d_%03d'%(i+1,i*45),[960,600],O/('checks/white/check-%02d.png'%(i+1)),'BLENDER_EEVEE_NEXT',32,'arbitrary azimuth white geometry inspection; not a source camera')
for name in ['CHECK_LOW_CONTACT','CHECK_ENVIRONMENT_OVERVIEW']:
    render('white',name,[960,600],O/('checks/white/'+name+'.png'),'BLENDER_EEVEE_NEXT',32,'extra low/contact or environment diagnostic')
for cfg in cfgs:
    render('white',cfg['camera'],cfg['size'],O/('source-renders/'+cfg['id']+'/white.png'),'BLENDER_EEVEE_NEXT',32,'native-grid white geometry source comparison; conditional camera')
# Canonical material rendered with one unchanged state for all views.
for i in range(8):render('material','CHECK_%02d_%03d'%(i+1,i*45),[960,600],O/('checks/material/check-%02d.png'%(i+1)),'CYCLES',48,'arbitrary azimuth material inspection; not a source camera')
for cfg in cfgs:
    if cfg['id']=='preview-front':continue
    render('material',cfg['camera'],cfg['size'],O/('source-renders/'+cfg['id']+'/material.png'),'CYCLES',24 if cfg['size'][0]==3840 else 32,'native-grid source comparison; other light states deliberately not retuned by camera')
print('SUITE_RENDER_COMPLETE',len(manifest),flush=True)
