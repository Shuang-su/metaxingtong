import bpy,json
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/phone-material.blend'));s=bpy.context.scene
points={}
for name,obs in [('P07_lens1_glass',[826,505]),('P07_lens2_glass',[822,546]),('P08_small_spot_identity_uncertain',[831,462])]:
 o=bpy.data.objects[name];p=world_to_camera_view(s,s.camera,o.matrix_world.translation);xy=[1080*p.x,603*(1-p.y)];points[name]={'source_manual_approximate':obs,'projected':xy,'residual_px':[xy[i]-obs[i] for i in range(2)],'status':'diagnostic only, uncertain visible centers; not independent blind validation'}
json.dump(points,open(R/'qa/feature-projections.json','w'),indent=2)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(R/'models/phone-white.glb'));json.dump({'mesh_count':len([o for o in bpy.context.scene.objects if o.type=='MESH']),'material_names':list(bpy.data.materials.keys()),'result':'Actual white GLB import completed'},open(R/'qa/white-reimport.json','w'),indent=2)
