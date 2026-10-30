"""Render immutable B1/D1 with same frozen cameras. No hiding, clipping or warps."""
import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'low'
rows=[]
def signature():
 return hashlib.sha256(repr([(o.name,[tuple(v.co) for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons],tuple(tuple(r) for r in o.matrix_world),o.hide_render) for o in sorted((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:o.name)]).encode()).hexdigest()
for stage,filename in [('B1','B1_frozen_camera_baseline.blend'),('D1','D1_shared_dashboard_material.blend')]:
 if mode=='review' and stage!='D1':continue
 bpy.ops.wm.open_mainfile(filepath=str(R/'models'/filename));s=bpy.context.scene
 s.render.engine='CYCLES';s.cycles.use_denoising=False;s.render.image_settings.file_format='PNG';s.render.resolution_percentage=100
 if mode=='review':
  tasks=[('MAIN','MAIN_passenger_local',1,1920,1080,64)]+[(f'CHECK_{i:02}',f'CHECK_{i:02}',1 if i%2 else 2,800,450,16) for i in range(1,9)]
 else:
  w,h,n=(960,540,12) if mode=='low' else (1920,1080,32)
  tasks=[(id,'SRC_'+id+('_open' if id=='S02' else '_closed'),2 if id=='S02' else 1,w,h,n) for id in ['S01','S02','S03']]
 state_signatures={}
 for frame in [1,2]:s.frame_set(frame);bpy.context.view_layer.update();state_signatures[frame]=signature()
 for id,camera,frame,w,h,n in tasks:
  s.frame_set(frame);s.camera=bpy.data.objects[camera];bpy.context.view_layer.update();before=signature();assert before==state_signatures[frame]
  s.render.resolution_x=w;s.render.resolution_y=h;s.cycles.samples=n
  path=R/'renders'/mode/f'{stage}_{id}.png';path.parent.mkdir(parents=True,exist_ok=True)
  s.render.filepath=str(path)
  if not path.exists():bpy.ops.render.render(write_still=True)
  assert signature()==before
  rows.append({'stage':stage,'id':id,'camera':camera,'frame':frame,'dimensions':[w,h],'samples':n,'path':str(path.relative_to(R)),'state_mesh_signature':before,'geometry_unchanged_after_render':True,'all_meshes_visible':all(not o.hide_render for o in s.objects if o.type=='MESH'),'existing_complete_output_preserved':True})
(R/'qa'/f'render_{mode}.json').write_text(json.dumps(rows,indent=2)+'\n')
print('RENDER_COMPLETE',mode,len(rows))
