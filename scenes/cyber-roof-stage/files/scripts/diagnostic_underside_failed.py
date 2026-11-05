import bpy,json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from pathlib import Path
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r03.blend'));s=bpy.context.scene;rows=[]
for name in ['ROOF_MAIN gold ridge','ROOF_MAIN front eave','STAGE_INNER annulus','DJ11 body inferred depth']:
 o=bpy.data.objects[name];pts=[world_to_camera_view(s,s.camera,o.matrix_world@v.co) for v in o.data.vertices]
 rows.append({'object':name,'render_pixel_bbox':[min(p.x for p in pts)*1192,(1-max(p.y for p in pts))*671,max(p.x for p in pts)*1192,(1-min(p.y for p in pts))*671],'method':'project every mesh vertex through shared conditional SOURCE11 camera; bound only, not silhouette/occlusion match'})
(P/'qa/projected-landmark-bounds.json').write_text(json.dumps(rows,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r03-white.blend'));s=bpy.context.scene;s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_percentage=100;s.render.resolution_x=796;s.render.resolution_y=448
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.3,.3,.3,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
for name,loc,tar in [('under-support',(0,-27,-8),(0,2,3)),('low-thickness',(16,-25,2),(0,1,2))]:
 bpy.ops.object.camera_add(location=loc);c=bpy.context.object;c.name='DIAGNOSTIC WHITE '+name;c.data.lens=35;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();s.camera=c
 bpy.ops.object.light_add(type='AREA',location=(0,-10,-10));l=bpy.context.object;l.data.energy=2500;l.data.size=12;l.rotation_euler=(Vector((0,2,2))-l.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(P/'renders'/('diagnostic-white-lit-'+name+'.png'));bpy.ops.render.render(write_still=True)
# Do not save changed diagnostic scene over production.
