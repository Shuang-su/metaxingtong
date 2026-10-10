import bpy,json,sys,hashlib,inspect
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from layout_states import *
args=sys.argv[sys.argv.index('--')+1:];workspace=Path(args[0]);m=json.loads((root/'layout_state_manifest.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def material_snapshot():
 out=[]
 for mat in sorted(bpy.data.materials,key=lambda x:x.name):
  row={'name':mat.name,'diffuse':list(mat.diffuse_color),'metallic':mat.metallic,'roughness':mat.roughness,'use_nodes':mat.use_nodes}
  if mat.node_tree:
   row['nodes']=[]
   for node in sorted(mat.node_tree.nodes,key=lambda x:x.name):
    vals={}
    for sock in node.inputs:
     if hasattr(sock,'default_value'):
      v=sock.default_value
      try:v=list(v)
      except TypeError:pass
      if isinstance(v,(list,str,float,int,bool)) or v is None:vals[sock.identifier]=v
    row['nodes'].append({'name':node.name,'type':node.bl_idname,'inputs':vals,'operation':getattr(node,'operation',None),'blend_type':getattr(node,'blend_type',None),'image':getattr(getattr(node,'image',None),'name',None)})
   row['links']=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in mat.node_tree.links)
  out.append(row)
 return out

def immutable_snapshot():
 objs=[]
 for o in sorted(bpy.context.scene.objects,key=lambda x:x.name):
  row={'name':o.name,'type':o.type,'matrix_world':[list(x) for x in o.matrix_world],'matrix_local':[list(x) for x in o.matrix_local],'parent':o.parent.name if o.parent else None}
  if o.type=='MESH':
   row.update(vertices=[list(v.co) for v in o.data.vertices],edges=[list(e.vertices) for e in o.data.edges],polygons=[list(p.vertices) for p in o.data.polygons],polygon_material_indices=[p.material_index for p in o.data.polygons],uv=[{'name':u.name,'uv':[list(x.uv) for x in u.data]} for u in o.data.uv_layers],materials=[s.material.name if s.material else None for s in o.material_slots],modifiers=[{'name':md.name,'type':md.type,'show_viewport':md.show_viewport,'show_render':md.show_render} for md in o.modifiers])
  if o.type=='CAMERA':row.update(lens=o.data.lens,sensor_width=o.data.sensor_width,sensor_height=o.data.sensor_height,sensor_fit=o.data.sensor_fit,shift=[o.data.shift_x,o.data.shift_y])
  if o.type=='LIGHT':row.update(energy=o.data.energy,color=list(o.data.color),type_light=o.data.type)
  objs.append((o.name,digest(row)))
 return {'objects':dict(objs),'materials_sha256':digest(material_snapshot()),'all_objects_sha256':digest(objs)}

def full_visibility():
 sc=bpy.context.scene
 def layer(c):return {'name':c.name,'exclude':c.exclude,'hide_viewport':c.hide_viewport,'holdout':c.holdout,'indirect_only':c.indirect_only,'children':[layer(x) for x in c.children]}
 return {'objects':object_visibility(sc),'collections':{c.name:{'hide_render':c.hide_render,'hide_viewport':c.hide_viewport} for c in sorted(bpy.data.collections,key=lambda x:x.name)},'view_layers':{v.name:layer(v.layer_collection) for v in sc.view_layers}}

def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
base=workspace/m['base_blend']['workspace_relative_path'];assert sha(base)==m['base_blend']['sha256']
bpy.ops.wm.open_mainfile(filepath=str(base));sc=bpy.context.scene
baseline=immutable_snapshot();v0=full_visibility();names=visibility_targets(m)
assert set(m['furnishing_group']['objects'])=={o.name for o in bpy.data.collections[m['furnishing_group']['collection']].all_objects if o.type=='MESH'}
assert all(not v0['objects'][n]['hide_render'] and not v0['objects'][n]['hide_viewport'] for n in names)
cameras=sorted([o for o in sc.objects if o.type=='CAMERA'],key=lambda x:x.name);assert len(cameras)==18
switches=[];runs=[]
for state in ['furnished','unfurnished']:
 sid,selection=choose_state(m,state)
 for camera in cameras:
  sc.camera=camera
  entry=apply_layout(sc,m,sid,selection);bpy.context.view_layer.update();now=immutable_snapshot();vis=full_visibility()
  assert now==baseline
  assert vis['collections']==v0['collections'] and vis['view_layers']==v0['view_layers']
  assert all(vis['objects'][n]==v0['objects'][n] for n in vis['objects'] if n not in names)
  switches.append(dict(camera_selected_separately=camera.name,**entry))
  runs.append({'state':state,'camera':camera.name,'full_visibility_sha256':digest(vis),'immutable_sha256':digest(now),'visible_target_count':sum(not vis['objects'][n]['hide_render'] for n in names),'sofa_visible_count':sum(not vis['objects'][n]['hide_render'] for n in m['furnishing_group']['objects']),'dynamic_unchanged':True})
 assert len({x['full_visibility_sha256'] for x in runs if x['state']==state})==1
for state in ['furnished','unfurnished','furnished']:
 sid,selection=choose_state(m,state);switches.append(apply_layout(sc,m,sid,selection))
assert full_visibility()==v0 and immutable_snapshot()==baseline
# Timeline limits and manual override behaviour.
cases=[(6613.625823,'furnished'),(6626.597822,'unknown'),(6626.8,'unknown'),(6627.319120,'unknown'),(6627.396357,'unknown'),(6637.312808,'unfurnished'),(6638,'unknown'),(7000,'unknown'),(7105.257433,'unfurnished'),(7134.185133,'unfurnished'),(7135,'unknown'),(2117,'unknown'),(4529,'unknown'),(-1,'unknown'),(float('nan'),'unknown')]
for t,want in cases:assert timeline_state(m,t)==want
for t in [6626.8,7000,-1]:
 try:choose_state(m,source_time_seconds=t)
 except ValueError:pass
 else:raise AssertionError('Unknown time unexpectedly applied')
sid,selection=choose_state(m,'unfurnished',7000);assert selection['manual_override'] is True
for bad_time in [float('nan'),float('inf'),True,'6626']:
 try:choose_state(m,'furnished',bad_time)
 except ValueError:pass
 else:raise AssertionError('Nonfinite or nonnumeric time accepted')
# Invalid state rejection must not mutate visibility.
for bad in ['unknown','MATCH_D_01h58m39s_empty','']:
 old=full_visibility()
 try:apply_layout(sc,m,bad,{})
 except ValueError:pass
 else:raise AssertionError('Invalid state allowed')
 assert full_visibility()==old
assert 'camera' not in inspect.signature(apply_layout).parameters
src=inspect.getsource(apply_layout);assert 'scene.camera' not in src and 'bpy.context.scene.camera' not in src
report={'base_blend_sha256':sha(base),'all_36_camera_state_combinations_pass':True,'state_count':2,'camera_count':18,'only_explicit_18_plus_8_visibility_changes':True,'target_count':26,'furniture_count':18,'inferred_attachment_count':8,'collection_and_layer_visibility_preserved':True,'roundtrip_state_restores_baseline':True,'all_object_geometry_uv_material_slots_transforms_unchanged':True,'material_node_fingerprint_unchanged':True,'no_model_saved':True,'timeline_unknowns_rejected':True,'manual_override_logged':True,'invalid_explicit_time_rejected':True,'ambiguous_interval_closed_endpoints_unknown':True,'invalid_state_is_nonmutating':True,'camera_independent_function_interface':True,'immutable_baseline':baseline,'baseline_visibility':v0,'camera_state_runs':runs,'timeline_tests':[{'seconds':t if t==t else 'NaN','expected':s} for t,s in cases],'acceptance':{'state_contract':True,'source_geometry':False,'camera_calibration':False}}
dump(root/'qa/state_contract_audit.json',report);dump(root/'qa/state_switch_log.json',switches)
# Actual existing GLB import, without new export or duplication.
glb=workspace/m['shared_glb']['workspace_relative_path'];assert sha(glb)==m['shared_glb']['sha256']
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));sc=bpy.context.scene
imported=immutable_snapshot();v0=full_visibility();gs=[]
assert all(n in sc.objects for n in names)
for sid in ['unfurnished','furnished']:
 _,sel=choose_state(m,sid);gs.append(apply_layout(sc,m,sid,sel));assert immutable_snapshot()==imported
assert full_visibility()==v0
actual={'actual_import':True,'shared_glb_sha256':sha(glb),'mesh_count':sum(o.type=='MESH' for o in sc.objects),'all_18_sofa_and_8_inferred_attachment_nodes_found':True,'state_roundtrip_restores_visibility':True,'geometry_material_transform_hash_unchanged':True,'dynamic_groups':[{'id':g['id'],'present':[n for n in g['objects'] if n in sc.objects],'absent':[n for n in g['objects'] if n not in sc.objects]} for g in m['dynamic_groups']],'state_switches':gs,'new_glb_exported':False}
dump(root/'qa/actual_shared_glb_state_audit.json',actual)
print('STATE_AUDIT_PASS',len(runs),'camera/state cases; actual GLB mesh count',actual['mesh_count'],flush=True)
