import bpy,json,pathlib,hashlib,struct,tempfile,shutil,math
from mathutils import Vector
R=pathlib.Path('/workspace/scratch/fa58bfcf0425/metaxingtong-harbor-candidate-20261102');S=R/'stages/r06-review-candidate';O=pathlib.Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(x):return json.dumps(x,separators=(',',':'),sort_keys=True).encode()
def matrix(x):return [list(r) for r in x]
def snapshot(p):
 bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update()
 out={'file':str(p),'meshes':{},'cameras':{},'lights':{},'images':[],'linked_libraries':[l.filepath for l in bpy.data.libraries],'world':{}}
 for ob in bpy.context.scene.objects:
  if ob.type=='MESH':
   geom={'vertices':[list(v.co) for v in ob.data.vertices],'polygons':[list(p.vertices) for p in ob.data.polygons],'world_matrix':matrix(ob.matrix_world),'modifiers':[(m.type,m.show_render,m.show_viewport) for m in ob.modifiers],'hide_render':ob.hide_render,'hide_viewport':ob.hide_viewport}
   coords=[ob.matrix_world@v.co for v in ob.data.vertices];bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
   out['meshes'][ob.name]={'geometry_hash':sha(dump(geom)),'vertices':len(ob.data.vertices),'polygons':len(ob.data.polygons),'bounds':bounds,'editable_local':ob.library is None and ob.data.library is None}
  elif ob.type=='CAMERA':
   out['cameras'][ob.name]={'matrix_world':matrix(ob.matrix_world),'lens':ob.data.lens,'shift_x':ob.data.shift_x,'shift_y':ob.data.shift_y,'sensor_width':ob.data.sensor_width,'type':ob.data.type,'ortho_scale':ob.data.ortho_scale}
  elif ob.type=='LIGHT':
   d=ob.data;out['lights'][ob.name]={'matrix_world':matrix(ob.matrix_world),'type':d.type,'energy':d.energy,'color':list(d.color),'hide_render':ob.hide_render}
 for im in bpy.data.images:
  if im.type!='IMAGE':continue
  out['images'].append({'name':im.name,'packed':im.packed_file is not None,'packed_bytes':len(im.packed_file.data) if im.packed_file else 0,'packed_sha256':sha(im.packed_file.data) if im.packed_file else None,'dimensions':list(im.size),'pixel_buffer_length':len(im.pixels),'first_pixel':list(im.pixels[:4]),'filepath':im.filepath})
 w=bpy.context.scene.world
 if w and w.use_nodes:out['world']={n.name:{s.name:list(s.default_value) if hasattr(s.default_value,'__len__') else s.default_value for s in n.inputs if hasattr(s,'default_value') and isinstance(s.default_value,(int,float)) or hasattr(s,'default_value') and hasattr(s.default_value,'__len__')} for n in w.node_tree.nodes if n.type=='BACKGROUND'}
 return out
states={}
with tempfile.TemporaryDirectory(prefix='independent-harbor-read-') as td:
 for state in ['white','material']:
  p=S/f'harbor-r06-{state}.blend';t=pathlib.Path(td)/p.name;shutil.copyfile(p,t);assert sha(p.read_bytes())==sha(t.read_bytes());states[state]=snapshot(t);states[state]['file']=str(p.relative_to(R));states[state]['sha256']=sha(p.read_bytes())
r04=snapshot(R/'stages/r04-review-candidate/harbor-r04-material.blend')
roundtrips=[]
for state in ['white','material']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(S/f'harbor-r06-{state}.glb'));bpy.context.view_layer.update()
 imported={ob.name:ob for ob in bpy.context.scene.objects if ob.type=='MESH'};native=states[state]['meshes'];missing=sorted(set(native)-set(imported));extra=sorted(set(imported)-set(native));deltas=[]
 for name in set(native)&set(imported):
  ob=imported[name];coords=[ob.matrix_world@v.co for v in ob.data.vertices];bb=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)];delta=max(abs(bb[i][j]-native[name]['bounds'][i][j]) for i in range(3) for j in range(2));deltas.append({'name':name,'bbox_max_delta':delta})
 roundtrips.append({'state':state,'import_mesh_count':len(imported),'missing':missing,'extra':extra,'max_bbox_delta':max(d['bbox_max_delta'] for d in deltas),'object_bbox_deltas':sorted(deltas,key=lambda x:x['name'])})
summary={'blender':bpy.app.version_string,'white_mesh_count':len(states['white']['meshes']),'material_mesh_count':len(states['material']['meshes']),'white_material_meshes_exact':states['white']['meshes']==states['material']['meshes'],'white_material_cameras_exact':states['white']['cameras']==states['material']['cameras'],'white_material_lights_exact':states['white']['lights']==states['material']['lights'],'white_material_world_exact':states['white']['world']==states['material']['world'],'r04_r06_geometry_exact':r04['meshes']==states['material']['meshes'],'r04_source_cameras_retained_exact':all(states['material']['cameras'].get(k)==v for k,v in r04['cameras'].items() if k.startswith('SOURCE_')),'r04_r06_lights_exact':r04['lights']==states['material']['lights'],'both_states_no_linked_libraries':all(not s['linked_libraries'] for s in states.values()),'both_states_all_meshes_editable_local':all(v['editable_local'] for s in states.values() for v in s['meshes'].values()),'packed_all_images':all(v['packed'] and v['pixel_buffer_length']>0 for s in states.values() for v in s['images'])}
report={'summary':summary,'states':states,'actual_glb_reimports':roundtrips,'scope':'Independently open byte-identical BLEND copies without adjacent textures, inspect packed payloads, compare raw mesh topology/vertices/transforms and camera/light values, and import both GLBs in fresh empty scenes. No scene saved, no render repeated. Temp directory is not an OS filesystem isolation sandbox.'}
(O/'independent-native.json').write_text(json.dumps(report,indent=2));print('INDEPENDENT_NATIVE',json.dumps(summary));print('INDEPENDENT_REIMPORT',json.dumps([{k:v for k,v in r.items() if k!='object_bbox_deltas'} for r in roundtrips]))
