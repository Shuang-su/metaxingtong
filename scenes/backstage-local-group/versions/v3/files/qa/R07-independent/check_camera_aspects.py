import bpy,pathlib,json
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-mannequin-qa-20261104');R={}
for ver in ['R05','R06']:
 D={}
 for typ in ['blend','glb']:
  f=P/'models'/f'{ver}_material.{typ}'
  if typ=='blend':bpy.ops.wm.open_mainfile(filepath=str(f))
  else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(f))
  s=bpy.context.scene;ob=bpy.data.objects['MANNEQUIN_local'];c=ob.data;d={'loaded_resolution':[s.render.resolution_x,s.render.resolution_y],'lens':c.lens,'sensor_fit':c.sensor_fit,'sensor_width':c.sensor_width,'sensor_height':c.sensor_height,'angle_x':c.angle_x,'angle_y':c.angle_y,'frames':{}}
  for w,h in [(960,640),(1192,671)]:
   s.render.resolution_x=w;s.render.resolution_y=h;s.render.resolution_percentage=100;d['frames'][f'{w}x{h}']=[list(v.normalized()) for v in c.view_frame(scene=s)]
  D[typ]=d
 D['equal_aspect_errors']={res:max(abs(x-y)for a,b in zip(D['blend']['frames'][res],D['glb']['frames'][res])for x,y in zip(a,b))for res in D['blend']['frames']};R[ver]=D
(Q/'camera-aspect-diagnosis.json').write_text(json.dumps(R,indent=2));print(R)
