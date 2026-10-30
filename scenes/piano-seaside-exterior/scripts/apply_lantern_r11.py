"""Save the bounded shared-lantern update; reopen and verify frozen state."""
import bpy,json,hashlib,array,ast,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from lantern_material_r11 import apply_lanterns,LAMP_IDS
Q=R/'qa/r11';O=R/'models/r11';O.mkdir(parents=True,exist_ok=True)
module=ast.parse((R/'scripts/apply_n6766_camera.py').read_text());exec(compile(ast.Module(body=[n for n in module.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'read_only_snapshot_functions','exec'),globals())
def frozen():
 s=bpy.context.scene;ss=snapshot();lampm={m.name for o in s.objects if o.type=='MESH' and o.get('evidence_id') in LAMP_IDS for m in o.data.materials if m}
 nonlamp={m.name:nodes(m.node_tree) for m in bpy.data.materials if m.users and m.name not in lampm}
 worlds={w.name:{'nodes':nodes(w.node_tree),'env':[{'image':n.image.name,'sha':hashlib.sha256(n.image.packed_file.data).hexdigest(),'interpolation':n.interpolation} for n in w.node_tree.nodes if n.type=='TEX_ENVIRONMENT' and n.image and n.image.packed_file]} for w in bpy.data.worlds if w.node_tree}
 lights={o.name:{'matrix':[list(v) for v in o.matrix_world],'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'shadow':o.data.use_shadow,'size':getattr(o.data,'size',None),'radius':getattr(o.data,'shadow_soft_size',None)} for o in s.objects if o.type=='LIGHT' and o.get('evidence_id') not in LAMP_IDS}
 uvs={o.name:{u.name:sha([list(p.uv) for p in u.data]) for u in o.data.uv_layers} for o in s.objects if o.type=='MESH'}
 return {'geometry_hash':ss['geometry_hash'],'mesh_count':ss['mesh_count'],'uv_hash':sha(uvs),'camera_hash':sha({o.name:camera(o) for o in s.objects if o.type=='CAMERA'}),'camera_count':len([o for o in s.objects if o.type=='CAMERA']),'non_lamp_materials':sha(nonlamp),'non_lamp_lights':sha(lights),'all_worlds':sha(worlds),'active_world':s.world.name,'view_settings':{'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma,'look':s.view_settings.look,'transform':s.view_settings.view_transform},'render_settings':{'engine':s.render.engine,'samples':s.eevee.taa_render_samples,'ray_tracing':s.eevee.use_raytracing,'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'active_camera':s.camera.name}}
report={}
for kind in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'models/r10/piano_seaside_{kind}.blend'));s=bpy.context.scene;before=frozen();change=apply_lanterns(variant='b');s['stage']='r11 lamp-only correction; all R10 geometry/cameras/sky/coast/exposure frozen';s['lamp_lighting']='two physical lamp instances, each with existing internal point and four shadow-casting paper-exitance area proxies; shared across all cameras and both world states'
 bpy.ops.file.pack_all();dest=O/f'piano_seaside_{kind}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest));bpy.ops.wm.open_mainfile(filepath=str(dest));after=frozen();bad=[k for k in before if before[k]!=after[k]];assert not bad,bad
 report[kind]={'saved_file_reopened':True,'frozen_before':before,'frozen_after':after,'changed':change,'lamp_light_count':len([o for o in bpy.context.scene.objects if o.type=='LIGHT' and o.get('evidence_id') in LAMP_IDS]),'mesh_count':after['mesh_count'],'all_cameras_frozen':after['camera_count']==18}
 if kind=='material':bpy.ops.export_scene.gltf(filepath=str(O/'piano_seaside_material.glb'),export_format='GLB',export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
 else:
  # White GLB contains only unchanged geometry/material, without lights or world.
  src=R/'models/r09/piano_seaside_white.glb';(O/src.name).write_bytes(src.read_bytes());report[kind]['GLB']='byte-identical copy of R09 white GLB; not re-exported; will be reopened for this stage validation'
(Q/'lamp-only-saved-invariants.json').write_text(json.dumps(report,indent=2)+'\n');print('R11_SAVED_FREEZE_PASS')
