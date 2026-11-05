import bpy,json,hashlib,runpy,sys
from pathlib import Path
from mathutils.kdtree import KDTree
P=Path('/workspace/scratch/fa58bfcf0425/cyber-ring-emissive-band-study-20261105');O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def val(x):
 try:return list(x)
 except:return x if isinstance(x,(str,int,float,bool)) else str(x)
def nodes(nt):
 if not nt:return None
 return {'nodes':sorted([{'name':n.name,'type':n.bl_idname,'inputs':[(i.identifier,val(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]} for n in nt.nodes],key=lambda a:a['name']),'links':sorted([(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in nt.links])}
def snap():
 s=bpy.context.scene;bpy.context.view_layer.update();d={'mesh':{},'cams':{},'lights':{},'world':nodes(s.world.node_tree) if s.world else None,'materials':{},'render':{'engine':s.render.engine,'size':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'aspect':[s.render.pixel_aspect_x,s.render.pixel_aspect_y],'samples':s.cycles.samples,'denoise':s.cycles.use_denoising,'view':[s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,s.view_settings.gamma],'active':s.camera.name if s.camera else None}}
 for o in s.objects:
  if o.type=='MESH':
   payload={'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons],'matrix':[list(r) for r in o.matrix_world]}
   d['mesh'][o.name]={'hash':hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'world':[list(o.matrix_world@v.co) for v in o.data.vertices],'uv':[[list(x.uv) for x in u.data] for u in o.data.uv_layers],'visibility':[o.hide_render,o.hide_viewport], 'mats':[m.name for m in o.data.materials]}
  if o.type=='CAMERA':d['cams'][o.name]={'matrix':[list(r) for r in o.matrix_world],'frame':[list(v) for v in o.data.view_frame(scene=s)],'normalized_frame':[[v.x/-v.z,v.y/-v.z] for v in o.data.view_frame(scene=s)],'lens':o.data.lens,'shift':[o.data.shift_x,o.data.shift_y],'clip':[o.data.clip_start,o.data.clip_end]}
  if o.type=='LIGHT':d['lights'][o.name]={'matrix':[list(r) for r in o.matrix_world],'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'shape':o.data.shape if o.data.type=='AREA' else None,'size':o.data.size if o.data.type=='AREA' else None}
 for m in bpy.data.materials:
  if m.users:d['materials'][m.name]=nodes(m.node_tree)
 return d
def err(a,b):
 if isinstance(a,dict):return max([err(a[k],b[k]) for k in a] or [0]) if a.keys()==b.keys() else 1e99
 if isinstance(a,(list,tuple)):return max([err(x,y) for x,y in zip(a,b)] or [0]) if len(a)==len(b) else 1e99
 if isinstance(a,(int,float)) and isinstance(b,(int,float)):return abs(a-b)
 return 0 if a==b else 1e99
def compare_mesh(a,b):
 out={'names_equal':a.keys()==b.keys(),'objects':{}}
 for n in a.keys()&b.keys():
  av=a[n]['world'];bv=b[n]['world'];ka=KDTree(len(av));kb=KDTree(len(bv))
  for i,v in enumerate(av):ka.insert(v,i)
  for i,v in enumerate(bv):kb.insert(v,i)
  ka.balance();kb.balance()
  out['objects'][n]={'vertices':[len(av),len(bv)],'bidirectional_nearest_max':max(max(ka.find(v)[2] for v in bv),max(kb.find(v)[2] for v in av))}
 out['max']=max(x['bidirectional_nearest_max'] for x in out['objects'].values());return out
def uvset(o):
 if not o.data.uv_layers:return set()
 return {tuple(round(float(x),5) for x in list(o.matrix_world@o.data.vertices[o.data.loops[i].vertex_index].co)+list(o.data.uv_layers.active.data[i].uv)) for i in range(len(o.data.loops))}
R={};basis=P.parent/'cyber-roof-paired-shell-study-20261105/export/roof-paired-a055.blend';bpy.ops.wm.open_mainfile(filepath=str(basis));base=snap();band='STAGE_OUTER LED front full circumference inferred'
bpy.ops.wm.open_mainfile(filepath=str(P/'export/roof-led-surface-v3.blend'));mat=snap();ob=bpy.data.objects[band];R['band']={'slots':[m.name for m in ob.data.materials],'face_counts':{str(i):sum(f.material_index==i for f in ob.data.polygons) for i in range(len(ob.data.materials))},'uv_layers':[u.name for u in ob.data.uv_layers],'images':[],'uv_errors':[]};me=ob.data;import math
for f in me.polygons:
 if f.material_index==1:
  ii=[i%128 for i in f.vertices]
  for li,vi,i in zip(f.loop_indices,f.vertices,ii):
   u=i/128
   if 0 in ii and 127 in ii and i==0:u=1.
   expected=[u,(me.vertices[vi].co.z-.16)/.17];R['band']['uv_errors'].append(max(abs(a-b) for a,b in zip(expected,me.uv_layers.active.data[li].uv)))
band_uv_set=uvset(ob);newmat=ob.data.materials[1];R['band']['strength']=newmat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value
for n in newmat.node_tree.nodes:
 if n.type=='TEX_IMAGE':R['band']['images'].append({'name':n.image.name,'size':list(n.image.size),'colorspace':n.image.colorspace_settings.name,'packed_sha':hashlib.sha256(n.image.packed_file.data).hexdigest(),'external_sha':sha(P/'textures-v2'/n.image.name),'interpolation':n.interpolation})
bpy.ops.wm.open_mainfile(filepath=str(P/'export/roof-led-surface-v3-white.blend'));white=snap()
R['input_hashes']={f.name:sha(f) for f in (P/'export').glob('*v3*') if f.suffix in ['.blend','.glb','.json']}
R['all_geometry_exact']=all(base['mesh'][n]['hash']==mat['mesh'][n]['hash']==white['mesh'][n]['hash'] for n in base['mesh']);R['all_visibility_exact']=all(base['mesh'][n]['visibility']==mat['mesh'][n]['visibility']==white['mesh'][n]['visibility'] for n in base['mesh']);R['uv_changes']=[n for n in base['mesh'] if base['mesh'][n]['uv']!=mat['mesh'][n]['uv']];R['mat_white_uv_exact']=all(mat['mesh'][n]['uv']==white['mesh'][n]['uv'] for n in mat['mesh']);R['old_material_nodes_exact']={n:mat['materials'].get(n)==v for n,v in base['materials'].items()};R['new_cams']=list(mat['cams'].keys()-base['cams'].keys());R['old_camera_max']=max(err(base['cams'][n],mat['cams'][n]) for n in base['cams']);R['environment']={k:err(base[k],mat[k]) for k in ['lights','world','render']};R['white_environment']={k:err(mat[k],white[k]) for k in ['cams','lights','world','render']};R['glb']={}
for mode,ref in [('material',mat),('white',white)]:
 f=P/('export/roof-led-surface-v3'+('-white' if mode=='white' else '')+'.glb');bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(f));bpy.context.scene.render.resolution_x=1192;bpy.context.scene.render.resolution_y=671;raw=snap();uvmatch=uvset(bpy.data.objects[band])==band_uv_set;bpy.ops.wm.read_factory_settings(use_empty=True);sys.argv=['blender','--','--output',str(O/f'restored-{mode}.blend')]+(['--white'] if mode=='white' else []);runpy.run_path(str(P/'scripts/restore_led_surface_v3_glb.py'),run_name='__main__');rest=snap();R['glb'][mode]={'band_world_uv_set_round5_equal':uvmatch,'world_vertices':compare_mesh(ref['mesh'],raw['mesh']),'raw_cameras_by_field':{k:max(err(ref['cams'][n][k],raw['cams'][n][k]) for n in ref['cams']) for k in ['matrix','normalized_frame','shift','clip']},'restored':{k:err(ref[k],rest[k]) for k in ['cams','lights','world','render']},'counts':[len(rest['mesh']),len(rest['cams']),len(rest['lights'])]}
(O/'check.json').write_text(json.dumps(R,indent=2));print('COMPLETE')
