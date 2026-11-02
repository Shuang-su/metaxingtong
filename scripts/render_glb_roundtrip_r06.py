"""Actual imported GLB appearance diagnostic under the identical native light rig."""
import bpy,json,hashlib,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'stages/r06-review-candidate';Q=O/'qa/glb-render';Q.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(O/'harbor-r06-material.blend'));sc=bpy.context.scene;cam=bpy.data.objects['SOURCE_PREVIEW_FRONT_CONDITIONAL'];sc.camera=cam;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=False;sc.cycles.device='CPU';sc.render.resolution_x=768;sc.render.resolution_y=432;sc.render.resolution_percentage=100
before_cam=[list(r) for r in cam.matrix_world];before_lights={o.name:{'matrix':[list(r) for r in o.matrix_world],'type':o.data.type,'energy':o.data.energy} for o in sc.objects if o.type=='LIGHT'}
sc.render.filepath=str(Q/'native-same-rig.png');bpy.ops.render.render(write_still=True)
removed=[]
for ob in list(sc.objects):
 if ob.type=='MESH':removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
for mat in list(bpy.data.materials):bpy.data.materials.remove(mat)
for im in list(bpy.data.images):
 if im.type=='IMAGE':bpy.data.images.remove(im)
assert len([o for o in sc.objects if o.type=='MESH'])==0
bpy.ops.import_scene.gltf(filepath=str(O/'harbor-r06-material.glb'));sc.camera=cam
after_lights={o.name:{'matrix':[list(r) for r in o.matrix_world],'type':o.data.type,'energy':o.data.energy} for o in sc.objects if o.type=='LIGHT'};assert before_lights==after_lights;assert before_cam==[list(r) for r in cam.matrix_world]
sc.render.filepath=str(Q/'actual-glb-import-same-rig.png');bpy.ops.render.render(write_still=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'native_source':{'file':'harbor-r06-material.blend','sha256':sha(O/'harbor-r06-material.blend')},'glb_source':{'file':'harbor-r06-material.glb','sha256':sha(O/'harbor-r06-material.glb')},'removed_native_meshes':len(removed),'native_materials_and_images_cleared_before_import':True,'actual_imported_meshes':len([o for o in sc.objects if o.type=='MESH']),'native_camera_and_lights_preserved_exactly':True,'dimensions':[768,432],'engine':'CYCLES','samples':32,'blender_threads':1,'outputs':[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in Q.glob('*.png')],'scope':'geometry/material appearance round trip under supplied native light rig; GLB itself does not embed area lights/world; not source acceptance'}
(Q/'report.json').write_text(json.dumps(report,indent=2));print('ACTUAL_GLB_RENDER_READY')
