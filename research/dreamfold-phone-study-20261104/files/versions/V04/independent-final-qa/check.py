import bpy,pathlib,json,hashlib,sys
from mathutils.kdtree import KDTree
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/dreamfold-phone-study-20261104/versions');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-dreamfold-phone-v04-qa-20261104')
def nodes(nt):
 return {'nodes':[(n.name,n.type,[(i.name,list(i.default_value)if hasattr(i.default_value,'__len__')and not isinstance(i.default_value,str)else i.default_value)for i in n.inputs if hasattr(i,'default_value')])for n in nt.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in nt.links]}if nt else None
def snap():
 s=bpy.context.scene;d={'mesh':{},'cameras':{},'lights':{},'world':(tuple(s.world.color),s.world.use_nodes,nodes(s.world.node_tree))if s.world else None,'render':{k:getattr(s.render,k)for k in ['resolution_x','resolution_y','resolution_percentage','pixel_aspect_x','pixel_aspect_y','film_transparent']},'view':{k:getattr(s.view_settings,k)for k in ['view_transform','look','exposure','gamma']}}
 for o in s.objects:
  if o.type=='MESH':d['mesh'][o.name]={'vertices':[tuple(o.matrix_world@v.co)for v in o.data.vertices],'local':[tuple(v.co)for v in o.data.vertices],'faces':[tuple(p.vertices)for p in o.data.polygons],'uv':[[tuple(v.uv)for v in u.data]for u in o.data.uv_layers],'materials':[(m.name,nodes(m.node_tree))for m in o.data.materials]}
  if o.type=='CAMERA':d['cameras'][o.name]={'matrix':[list(r)for r in o.matrix_world],'frame':[tuple(v.normalized())for v in o.data.view_frame(scene=s)],'clip':[o.data.clip_start,o.data.clip_end]}
  if o.type=='LIGHT':d['lights'][o.name]=([list(r)for r in o.matrix_world],o.data.type,o.data.energy,tuple(o.data.color),o.data.shape,o.data.size,o.data.size_y)
 return d
R={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'V03/models'/f'phone-{mode}.blend'));old=snap();f=P/'V04/models'/f'phone-{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(f));new=snap();out={'blend_sha':hashlib.sha256(f.read_bytes()).hexdigest(),'mesh_exact_with_V02':new['mesh']==old['mesh'],'lights_exact':new['lights']==old['lights'],'world_exact':new['world']==old['world'],'render_exact':new['render']==old['render'],'view_exact':new['view']==old['view'],'saved_camera_count':len(new['cameras']),'old_source_camera_exact':all(new['cameras'][n]==c for n,c in old['cameras'].items())}
 f=P/'V04/models'/f'phone-{mode}.glb';out['changed_world_mesh_names']=[n for n in old['mesh'] if old['mesh'][n]!=new['mesh'][n]];out['all_local_mesh_uv_materials_exact']=all({k:v for k,v in old['mesh'][n].items() if k!='vertices'}=={k:v for k,v in new['mesh'][n].items() if k!='vertices'} for n in old['mesh']);out['glb_sha']=hashlib.sha256(f.read_bytes()).hexdigest();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(f));s=bpy.context.scene;s.render.resolution_x=1080;s.render.resolution_y=603;s.render.resolution_percentage=100;native=snap();out['native_mesh_count']=len(native['mesh']);out['native_camera_count']=len(native['cameras']);out['native_light_count']=len(native['lights']);out['camera_error']={}
 for n,c in new['cameras'].items():
  z=native['cameras'][n];out['camera_error'][n]={'matrix_max':max(abs(c['matrix'][i][j]-z['matrix'][i][j])for i in range(4)for j in range(4)),'normalized_frame_max':max(abs(c['frame'][i][j]-z['frame'][i][j])for i in range(4)for j in range(3))}
 out['world_vertex_error']={}
 for n,m in new['mesh'].items():
  errs=[]
  for a,b in [(m['vertices'],native['mesh'][n]['vertices']),(native['mesh'][n]['vertices'],m['vertices'])]:
   kd=KDTree(len(b))
   for i,v in enumerate(b):kd.insert(v,i)
   kd.balance();errs.append(max(kd.find(v)[2]for v in a))
  out['world_vertex_error'][n]=max(errs)
 fp=P/'V04/scripts/restore-state.py';sys.argv=['blender','--',mode];exec(compile(fp.read_text(),str(fp),'exec'),{'__file__':str(fp)});rest=snap();bpy.ops.wm.save_as_mainfile(filepath=str(Q/f'restored-{mode}.blend'));out['restored_camera_equal']=rest['cameras']==new['cameras'];out['restored_lights_equal']=rest['lights']==new['lights'];out['restored_world_equal']=rest['world']==new['world'];out['restored_render_equal']=rest['render']==new['render'];out['restored_view_equal']=rest['view']==new['view'];out['restore_preserves_imported_mesh']=rest['mesh']==native['mesh'];out['restore_differences']={k:{'original':new[k],'restored':rest[k]}for k in ['cameras','lights','world'] if new[k]!=rest[k]};R[mode]=out
(Q/'check.json').write_text(json.dumps(R,indent=2));print(R)
