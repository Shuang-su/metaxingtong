"""Render frozen validated models; resume skips completed full PNG files.
No material/geometry/lighting changes, no visibility switches; only camera and sampling.
"""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'models/r03';QA=ROOT/'qa/r03'
jobs=[]
for role in ['material','white']:
    bpy.ops.wm.open_mainfile(filepath=str(OUT/f'interview-room-{role}.blend'))
    s=bpy.context.scene;s.cycles.use_denoising=False
    cams=sorted([o for o in s.objects if o.type=='CAMERA'],key=lambda o:o.name)
    for o in cams:
        if o.name.startswith('CHECK'):
            if role=='white':continue
            name='check-'+o.name[5:7]+'.png';res=(1280,720);samples=48
        elif 'front' in o.name:
            name='source-front-'+('render' if role=='material' else 'white')+'.png';res=(1920,1080);samples=128 if role=='material' else 64
        else:
            name='source-oblique-'+('render' if role=='material' else 'white')+'.png';res=(1920,1080);samples=96 if role=='material' else 64
        jobs.append({'name':name,'model':role,'camera':o.name,'resolution':res,'samples':samples,'no_denoise_build_support':True})
    # Main view first for review; then oblique and diagnostic views.
    rolejobs=sorted([j for j in jobs if j['model']==role],key=lambda j: ('0' if j['name'].startswith('source-front') else '1' if j['name'].startswith('source-oblique') else '2')+j['name'])
    for j in rolejobs:
        path=QA/j['name']
        if path.exists():continue
        s.camera=bpy.data.objects[j['camera']];s.render.resolution_x,s.render.resolution_y=j['resolution'];s.render.resolution_percentage=100
        s.cycles.samples=j['samples'];s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
(QA/'render-jobs.json').write_text(json.dumps(jobs,indent=2))
print('ALL_DELIVERABLE_RENDERS_COMPLETE',len(jobs))
