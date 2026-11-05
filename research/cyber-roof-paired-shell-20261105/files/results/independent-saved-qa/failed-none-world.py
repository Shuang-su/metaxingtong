import bpy,json,hashlib,runpy,sys
from pathlib import Path
from mathutils.kdtree import KDTree
P=Path('/workspace/scratch/fa58bfcf0425/cyber-roof-paired-shell-study-20261105');O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def val(x):
 try:return list(x)
 except:return x if isinstance(x,(str,int,float,bool)) else str(x)
def nodes(nt):
 if not nt:return None
 return {'nodes':sorted([{'name':n.name,'type':n.bl_idname,'inputs':[(i.identifier,val(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]} for n in nt.nodes],key=lambda a:a['name']),'links':sorted([(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in nt.links])}
def snap():
 s=bpy.context.scene;bpy.context.view_layer.update();d={'mesh':{},'cams':{},'lights':{},'world':nodes(s.world.node_tree),'materials':{},'render':{'engine':s.render.engine,'size':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'aspect':[s.render.pixel_aspect_x,s.render.pixel_aspect_y],'samples':s.cycles.samples,'denoise':s.cycles.use_denoising,'view':[s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,s.view_settings.gamma],'active':s.camera.name if s.camera else None}}
 for o in s.objects:
  if o.type=='MESH':
   payload={'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons],'matrix':[list(r) for r in o.matrix_world]}
   d['mesh'][o.name]={'hash':hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'world':[list(o.matrix_world@v.co) for v in o.data.vertices],'uv':[[list(x.uv) for x in u.data] for u in o.data.uv_layers],'visibility':[o.hide_render,o.hide_viewport], 'mats':[m.name for m in o.data.materials]}
  if o.type=='CAMERA':d['cams'][o.name]={'matrix':[list(r) for r in o.matrix_world],'frame':[list(v) for v in o.data.view_frame(scene=s)],'lens':o.data.lens,'shift':[o.data.shift_x,o.data.shift_y],'clip':[o.data.clip_start,o.data.clip_end]}
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
R={'input_hashes':{f.name:sha(f) for f in (P/'export').iterdir() if f.suffix in ['.blend','.glb','.json']}}
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'cyber-roof-stage-20261105/models/roof-r05.blend'));base=snap()
bpy.ops.wm.open_mainfile(filepath=str(P/'export/roof-paired-a055.blend'));mat=snap()
bpy.ops.wm.open_mainfile(filepath=str(P/'export/roof-paired-a055-white.blend'));white=snap()
recipe=json.loads((P/'renders/candidate-source11-recipe.json').read_text());R['saved_vs_execution_mesh_exact']={n:v['hash']==recipe['actual_mesh_hashes'][n] for n,v in mat['mesh'].items()}
R['mat_white_geometry_uv_visibility_exact']={n:all(mat['mesh'][n][k]==white['mesh'][n][k] for k in ['hash','uv','visibility']) for n in mat['mesh']}
R['material_vs_original_nodes_exact']=mat['materials']==base['materials'];R['original_environment']={k:err(base[k],mat[k]) for k in ['cams','lights','world']};R['white_environment']={k:err(white[k],mat[k]) for k in ['cams','lights','world','render']};R['saved_render']=mat['render']
R['glb']={}
for mode,reference in [('material',mat),('white',white)]:
 f=P/('export/roof-paired-a055'+('-white' if mode=='white' else '')+'.glb');bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(f));bpy.context.scene.render.resolution_x=1192;bpy.context.scene.render.resolution_y=671;raw=snap()
 bpy.ops.wm.read_factory_settings(use_empty=True);sys.argv=['blender','--','--output',str(O/f'restored-{mode}.blend')]+(['--white'] if mode=='white' else []);runpy.run_path(str(P/'scripts/restore_paired_a055_glb.py'),run_name='__main__');rest=snap()
 R['glb'][mode]={'raw_mesh':compare_mesh(reference['mesh'],raw['mesh']),'raw_camera':err(reference['cams'],raw['cams']),'restored_camera':err(reference['cams'],rest['cams']),'restored_lights':err(reference['lights'],rest['lights']),'restored_world':err(reference['world'],rest['world']),'restored_render':err(reference['render'],rest['render']),'counts':[len(rest['mesh']),len(rest['cams']),len(rest['lights'])],'raw_material_nodes':raw['materials'],'restored_world_detail':rest['world'],'reference_world_detail':reference['world']}
(O/'check.json').write_text(json.dumps(R,indent=2));print('QA_COMPLETE')
