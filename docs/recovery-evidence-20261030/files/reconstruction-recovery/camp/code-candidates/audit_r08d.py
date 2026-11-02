import bpy,bmesh,json,hashlib
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
r=Path(__file__).resolve().parents[1];out=r/'qa/R08_trial'
def camera_state():return {o.name:{'matrix':[list(row) for row in o.matrix_world],'lens':o.data.lens} for o in bpy.data.objects if o.type=='CAMERA'}
def object_state():
 data={}
 for o in bpy.data.objects:
  if o.type=='MESH':data[o.name]=hashlib.sha256(json.dumps({'mat':[list(row) for row in o.matrix_world],'vertices':[list(v.co) for v in o.data.vertices]},sort_keys=True).encode()).hexdigest()
 return data
bpy.ops.wm.open_mainfile(filepath=str(r/'models/R07_camp_materials.blend'));oldcams=camera_state();oldobjs=object_state();bpy.ops.wm.open_mainfile(filepath=str(r/'models/R08d_contacts_cloth_trial.blend'));newobjs=object_state();changed=[n for n in oldobjs if oldobjs[n]!=newobjs.get(n)];new=[n for n in newobjs if n not in oldobjs]
items=[];dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
 if o.name.startswith(('P02_','C01_sling','C01_R08','T01_roof_panel_04','T01_roof_panel_05','T01_skirt_panel_04','T01_skirt_panel_05')):
  ev=o.evaluated_get(dg);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me);pts=[o.matrix_world@v.co for v in me.vertices];items.append({'name':o.name,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'min_z':min(p.z for p in pts),'bounds':[list(map(min,zip(*pts))),list(map(max,zip(*pts)))]});bm.free();ev.to_mesh_clear()
rep={'source_cameras_unchanged':all(camera_state().get(n)==v for n,v in oldcams.items() if n.startswith('SOURCE_')),'all_original_camera_parameters_unchanged':all(camera_state().get(n)==v for n,v in oldcams.items()),'changed_or_removed_meshes':changed,'new_meshes':new,'evaluated_local_topology':items,'limits':'not collision proof; duplicated capped curve rings may be non-welded; no source acceptance','third':'fixed previously seen H01 f2500 camera reused only, not optimized, failed old calibration remains'}
(out/'R08d_actual_audit.json').write_text(json.dumps(rep,indent=2));s=bpy.context.scene;s.camera=bpy.data.objects['REUSED_H01_F2500_NOT_FRESH_HOLDOUT'];s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=50;s.cycles.samples=8;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(out/'R08d_source3_reused_failed_camera_960.png');bpy.ops.render.render(write_still=True)
print('R08D_AUDIT_DONE')
