import bpy,json,sys,hashlib,time
from pathlib import Path
from mathutils import Matrix
P=Path('/workspace/scratch/fa58bfcf0425/observatory-exterior-fit-20261105');g=json.load(open(P/'geometry.json'));data=json.load(open(P/'trials.json'))
bpy.ops.wm.open_mainfile(filepath=g['model_path']);s=bpy.context.scene;c=bpy.data.objects['SOURCE_15_exterior'];s.camera=c;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=6;s.render.resolution_percentage=100;s.render.resolution_x=1192;s.render.resolution_y=671
records=[]
for t in data['trials']:
 if t['lens'] not in [12,35]:continue
 r=t['camera_rotation'];pos=t['camera_position'];m=Matrix.Identity(4)
 for i in range(3):
  for j in range(3):m[i][j]=r[i][j]
  m[i][3]=pos[i]
 c.matrix_world=m;c.data.lens=t['lens'];s.render.filepath=str(P/f"trial_{t['lens']}mm.png");bpy.ops.render.render(write_still=True)
 records.append({'path':s.render.filepath,'sha256':hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest(),'model_sha256':g['model_sha256'],'memory_only_camera':t,'samples':16,'denoise':False})
 json.dump(records,open(P/'render-records.json','w'),indent=2)
