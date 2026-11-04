import bpy,json
from pathlib import Path
O=Path(__file__).parent;R=O.parent/'keyring-underbridge-r07-20261104/models'
def snap():
 s=bpy.context.scene
 return {'mesh':{o.name:{'v':[list(v.co) for v in o.data.vertices],'f':[list(p.vertices) for p in o.data.polygons],'mat':[m.name for m in o.data.materials],'matrix':[list(r) for r in o.matrix_world],'uv':[[list(x.uv) for x in l.data] for l in o.data.uv_layers],'hide':[o.hide_render,o.hide_viewport]} for o in s.objects if o.type=='MESH'},'cam':{o.name:{'matrix':[list(r) for r in o.matrix_world],'lens':o.data.lens,'sensor':o.data.sensor_width,'frame':[list(v) for v in o.data.view_frame(scene=s)]} for o in s.objects if o.type=='CAMERA'}}
bpy.ops.wm.open_mainfile(filepath=str(R/'r07-material.blend'));a=snap();bpy.ops.wm.open_mainfile(filepath=str(R/'r07b-material.blend'));b=snap();out={'all164_mesh_data_exact':a['mesh']==b['mesh'],'changed_camera_names':[n for n in a['cam'] if a['cam'][n]!=b['cam'][n]],'new_camera':b['cam']['diagnostic-underbridge-fixed']}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'r07b-material.glb'));bpy.context.scene.render.resolution_x=1192;bpy.context.scene.render.resolution_y=671;c=snap();out['all12_glb_camera_matrix_max_error']=max(abs(v-c['cam'][n]['matrix'][i][j]) for n,x in b['cam'].items() for i,row in enumerate(x['matrix']) for j,v in enumerate(row));(O/'diff-b.json').write_text(json.dumps(out,indent=2));print(out)
