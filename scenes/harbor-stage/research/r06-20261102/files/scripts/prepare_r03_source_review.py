"""Camera/evidence stage only: keep r03 geometry identity explicit."""
import bpy,json,hashlib,struct,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];BASE=R/'stages/r03-shared-scene';O=R/'stages/r03-source-review';O.mkdir(exist_ok=True)
def geometry_manifest():
    rows=[]
    for ob in sorted([o for o in bpy.context.scene.objects if o.type=='MESH'],key=lambda o:o.name):
        h=hashlib.sha256()
        for v in ob.data.vertices:h.update(struct.pack('<3d',*(ob.matrix_world@v.co)))
        for p in ob.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
        rows.append({'id':ob.name,'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons),'world_geometry_sha256':h.hexdigest()})
    return rows
configs=[
 {'id':'aug24-front','file':'sources/preliminary/BV1iteRzHEsK_1.093550_4k_preliminary.png','camera':'SOURCE_AUG24_FRONT_CONDITIONAL','size':[3840,2160],'loc':[0,-6,1.5],'target':[0,1,1.35],'lens':40,'role':'same-event performance close/cropped; known dark display state differs from canonical teal'},
 {'id':'preview-front','file':'sources/official-preview/BV1uqYvzDEZK_5.051975_1080p60.png','camera':'SOURCE_PREVIEW_FRONT_CONDITIONAL','size':[1920,1080],'loc':[0,-22,3.2],'target':[0,1,3.0],'lens':37,'shift':[-.015625,-.012],'role':'official CG front establishing frame; canonical teal state approximation'},
 {'id':'preview-high','file':'sources/official-preview/BV1uqYvzDEZK_10.106498_1080p60.png','camera':'SOURCE_PREVIEW_HIGH_CONDITIONAL','size':[1920,1080],'loc':[0,-8.5,8.2],'target':[0,1,2.0],'lens':35,'role':'official CG high front; pink light state differs, crown top cropped'},
 {'id':'preview-wide','file':'sources/official-preview/BV1uqYvzDEZK_13.767175_1080p60.png','camera':'SOURCE_PREVIEW_WIDE_CONDITIONAL','size':[1920,1080],'loc':[-14,-22.4,15.4],'target':[0,0,3.0],'lens':34,'shift':[-.035,0],'role':'official CG oblique establishing frame; gold light state differs'},
 {'id':'preview-low','file':'sources/official-preview/BV1uqYvzDEZK_16.085747_1080p60.png','camera':'SOURCE_PREVIEW_LOW_CONDITIONAL','size':[1920,1080],'loc':[0,-5.2,.95],'target':[0,1,2.8],'lens':28,'role':'official CG underside; mint light state differs, top and feet cropped'},
 {'id':'companion-120','file':'sources/live-companion/BV1gseHzLEuf_120.140741_actual1080.png','camera':'SOURCE_COMPANION_120_CONDITIONAL','size':[1920,1080],'loc':[4.5,-4,1.3],'target':[4.2,2,1.6],'lens':54,'role':'same-event other performance; actual1080; dynamic person/pink lights excluded from geometry'},
 {'id':'companion-126','file':'sources/live-companion/BV1gseHzLEuf_126.768777_4k.png','camera':'SOURCE_COMPANION_126_CONDITIONAL','size':[3840,2160],'loc':[2.7,-4,1.3],'target':[6.2,4.8,1.65],'lens':55,'role':'same-event other performance actual4K; side foot/chevrons, no roof; not exact120 frame'},
]
all_states={}
for state in ['white','material']:
    bpy.ops.wm.open_mainfile(filepath=str(BASE/('harbor-scene-r03-'+state+'.blend')));sc=bpy.context.scene;before=geometry_manifest()
    for cfg in configs:
        name=cfg['camera'];ob=bpy.data.objects.get(name)
        if ob is None:
            da=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,da);sc.collection.objects.link(ob)
        ob.location=cfg['loc'];ob.rotation_euler=(Vector(cfg['target'])-ob.location).to_track_quat('-Z','Y').to_euler();ob.data.lens=cfg['lens'];ob.data.shift_x,ob.data.shift_y=cfg.get('shift',[0,0]);ob['source_file']=cfg['file'];ob['alignment_status']='CONDITIONAL; all sources used for training, no independent held-out validation'
    sc['geometry_baseline_commit']='121c415fe96f003f0930f02d84fecdaeba72fec2'
    sc['source_validation_status']='Unaccepted candidate; all7 source frames used in construction/review; no holdout, later independent replay unverified'
    sc.camera=bpy.data.objects['SOURCE_PREVIEW_FRONT_CONDITIONAL'];sc.render.resolution_x=1920;sc.render.resolution_y=1080;sc.cycles.use_denoising=False;sc.cycles.samples=48
    after=geometry_manifest();assert before==after,'Camera preparation must not mutate frozen geometry'
    bpy.ops.wm.save_as_mainfile(filepath=str(O/('harbor-r03-review-'+state+'.blend')))
    bpy.ops.export_scene.gltf(filepath=str(O/('harbor-r03-review-'+state+'.glb')),export_format='GLB',export_cameras=True,export_lights=False,export_extras=True)
    all_states[state]=after
assert all_states['white']==all_states['material'],'White/material shared geometry mismatch'
(O/'geometry-identity.json').write_text(json.dumps({'origin_commit':'121c415fe96f003f0930f02d84fecdaeba72fec2','camera_only_stage':True,'white_material_world_geometry_exact_match':True,'objects':all_states['white']},indent=2))
for cfg in configs:
    p=R/cfg['file'];cfg['source_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();cfg['source_bytes']=p.stat().st_size;cfg['fit_status']='conditional, source pixels may have large residuals; not a passed calibration';cfg['split']='TRAINING / RECONSTRUCTION INPUT; NOT HOLDOUT'
(O/'source-cameras.json').write_text(json.dumps(configs,ensure_ascii=False,indent=2))
print('CAMERA_ONLY_SHARED_GEOMETRY_READY',len(all_states['white']))
