"""Only camera source_N6766 changes. Reopen both saved files and compare invariants."""
import bpy,json,hashlib,sys,array
from pathlib import Path
from mathutils import Vector,Quaternion
ROOT=Path(__file__).resolve().parents[1];QA=ROOT/'qa/r08';OUT=ROOT/'models/r08';OUT.mkdir(parents=True,exist_ok=True)
selected=json.loads((QA/'camera-selected.json').read_text())
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def val(v):
 if isinstance(v,(str,bool,int,float)) or v is None:return v
 try:return list(v)
 except:return getattr(v,'name',str(type(v)))
def nodes(tree):
 if not tree:return None
 return {'nodes':[{ 'name':n.name,'type':n.bl_idname,'inputs':{s.identifier:val(s.default_value) for s in n.inputs if hasattr(s,'default_value')},'operation':getattr(n,'operation',None),'image':getattr(getattr(n,'image',None),'name',None),'color_ramp':[(e.position,list(e.color)) for e in n.color_ramp.elements] if hasattr(n,'color_ramp') else None} for n in tree.nodes],'links':[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in tree.links]}
def mesh_hash(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();vs=array.array('f',[0])*len(m.vertices)*3;ls=array.array('i',[0])*len(m.loops);m.vertices.foreach_get('co',vs);m.loops.foreach_get('vertex_index',ls);r={'vertices':hashlib.sha256(vs.tobytes()).hexdigest(),'loops':hashlib.sha256(ls.tobytes()).hexdigest(),'polygons':[(p.loop_start,p.loop_total,p.material_index,p.use_smooth) for p in m.polygons]};ev.to_mesh_clear();return sha(r)
def camera(o):return {'location':list(o.location),'rotation_euler':list(o.rotation_euler),'lens_mm':o.data.lens,'clip_start':o.data.clip_start,'clip_end':o.data.clip_end,'shift_x':o.data.shift_x,'shift_y':o.data.shift_y,'sensor_width':o.data.sensor_width,'sensor_height':o.data.sensor_height,'type':o.data.type}
def snapshot():
 sc=bpy.context.scene;geo={};lights={}
 for o in sc.objects:
  if o.type=='MESH':geo[o.name]={'mesh':mesh_hash(o),'matrix':[list(v) for v in o.matrix_world],'materials':[m.name if m else None for m in o.data.materials],'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'evidence_id':o.get('evidence_id')}
  if o.type=='LIGHT':lights[o.name]={'matrix':[list(v) for v in o.matrix_world],'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'size':getattr(o.data,'size',None),'soft_radius':getattr(o.data,'shadow_soft_size',None)}
 used_materials={name for x in geo.values() for name in x['materials'] if name};used_images={n.image.name for m in bpy.data.materials if m.name in used_materials and m.node_tree for n in m.node_tree.nodes if hasattr(n,'image') and n.image}
 material={m.name:{'diffuse':list(m.diffuse_color),'nodes':nodes(m.node_tree)} for m in bpy.data.materials if m.name in used_materials};textures={i.name:hashlib.sha256(i.packed_file.data).hexdigest() if i.packed_file else i.filepath for i in bpy.data.images if i.name in used_images}
 return {'geometry_hash':sha(geo),'material_hash':sha(material),'light_hash':sha(lights),'world_hash':sha(nodes(sc.world.node_tree)),'texture_hash':sha(textures),'mesh_count':len(geo),'geometry_objects':geo,'other_cameras':{o.name:camera(o) for o in sc.objects if o.type=='CAMERA' and o.name!='source_N6766'},'N6766':camera(bpy.data.objects['source_N6766']),'active_camera':sc.camera.name,'render_engine':sc.render.engine,'eevee_samples':sc.eevee.taa_render_samples,'unused_datablocks':{'materials':[m.name for m in bpy.data.materials if m.name not in used_materials],'images':[i.name for i in bpy.data.images if i.name not in used_images]}}
checks={}
for kind in ['material','white']:
 base=ROOT/f'models/r07/piano_seaside_{kind}.blend';dest=OUT/f'piano_seaside_{kind}.blend';bpy.ops.wm.open_mainfile(filepath=str(base));before=snapshot();o=bpy.data.objects['source_N6766'];o.location=selected['location'];q=(Vector(selected['target'])-o.location).to_track_quat('-Z','Y');o.rotation_euler=(q@Quaternion((0,0,1),selected['roll_rad'])).to_euler();o.data.lens=selected['lens_mm'];bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(dest));bpy.ops.wm.open_mainfile(filepath=str(dest));after=snapshot();changed=[k for k in before if before[k]!=after[k] and k!='unused_datablocks'];assert changed==['N6766'],changed
 checks[kind]={'base':str(base.relative_to(ROOT)),'output':str(dest.relative_to(ROOT)),'changed_snapshot_sections':changed,'mesh_count':before['mesh_count'],'geometry_hash_before':before['geometry_hash'],'geometry_hash_after':after['geometry_hash'],'material_hash_before':before['material_hash'],'material_hash_after':after['material_hash'],'world_light_texture_identical':all(before[k]==after[k] for k in ['world_hash','light_hash','texture_hash']),'other_cameras_identical':before['other_cameras']==after['other_cameras'],'other_camera_count':len(after['other_cameras']),'before':before['N6766'],'after':after['N6766'],'actual_saved_file_reopened':True,'unused_datablocks_before':before['unused_datablocks'],'unused_datablocks_after':after['unused_datablocks'],'unused_cleanup_note':'Blender may purge unused datablocks when resaving white BLEND; no assigned material or texture changed.'}
 if kind=='material' and '--reuse-material-render' in sys.argv and (QA/'source_N6766.png').exists():
  checks[kind]['render_reused_from_completed_first_run']=True;continue
 sc=bpy.context.scene;sc.camera=bpy.data.objects['source_N6766'];sc.render.resolution_x=1920;sc.render.resolution_y=1080;sc.render.filepath=str(QA/('source_N6766.png' if kind=='material' else 'white_source_N6766.png'));bpy.ops.render.render(write_still=True)
(QA/'camera-only-invariants.json').write_text(json.dumps(checks,indent=2)+'\n');print('CAMERA_ONLY_COMPLETE')
