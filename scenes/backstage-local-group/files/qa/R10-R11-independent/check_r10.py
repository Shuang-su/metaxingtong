import bpy,bmesh,json,pathlib,hashlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-tabletop-qa-20261104');S={};R={}
def h(x):return hashlib.sha256(repr(x).encode()).hexdigest()
def nodes(nt):
 return {'nodes':[(n.name,n.type,[(i.name,list(i.default_value) if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else i.default_value) for i in n.inputs if hasattr(i,'default_value')]) for n in nt.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in nt.links]} if nt else None
for v in ['R09','R10']:
 for mode in ['material','white']:
  f=P/'models'/f'{v}_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(f));s={'mesh':{},'local':{},'uv':{},'camera':{},'light':{},'visibility':{},'world':(tuple(bpy.context.scene.world.color),nodes(bpy.context.scene.world.node_tree))};audit={}
  for o in bpy.context.scene.objects:
   s['visibility'][o.name]=(o.hide_render,o.hide_viewport,o.hide_get())
   if o.type=='MESH':
    coords=[tuple(o.matrix_world@v.co) for v in o.data.vertices];faces=[tuple(p.vertices) for p in o.data.polygons];s['mesh'][o.name]={'hash':h((coords,faces)),'unique_coords':sorted(set(coords)),'verts':len(coords),'faces':len(faces)};s['local'][o.name]=h(([tuple(v.co) for v in o.data.vertices],faces));s['uv'][o.name]=h([[tuple(x.uv) for x in uv.data] for uv in o.data.uv_layers]);bm=bmesh.new();bm.from_mesh(o.data);audit[o.name]={'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(p.calc_area()<1e-12 for p in bm.faces),'volume':bm.calc_volume(signed=True)};bm.free()
   if o.type=='CAMERA':s['camera'][o.name]=([list(r) for r in o.matrix_world],o.data.lens,o.data.sensor_width,o.data.sensor_height,o.data.sensor_fit,o.data.shift_x,o.data.shift_y)
   if o.type=='LIGHT':s['light'][o.name]=([list(r) for r in o.matrix_world],o.data.type,o.data.energy,tuple(o.data.color),o.data.shadow_soft_size,getattr(o.data,'size',None),nodes(o.data.node_tree))
  s['materials']={m.name:nodes(m.node_tree) for m in bpy.data.materials};imgs=[]
  for im in bpy.data.images:
   if im.source!='FILE':continue
   packed=bytes(im.packed_file.data) if im.packed_file else None;ext=P/'textures'/pathlib.Path(im.filepath).name
   imgs.append({'name':im.name,'size':list(im.size),'colorspace':im.colorspace_settings.name,'packed_bytes':len(packed) if packed else 0,'packed_sha':hashlib.sha256(packed).hexdigest() if packed else None,'external_sha':hashlib.sha256(ext.read_bytes()).hexdigest() if ext.exists() else None})
  key=v+'_'+mode;S[key]=s;R[key]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'mesh_count':len(s['mesh']),'camera_count':len(s['camera']),'anomalies':{n:a for n,a in audit.items() if a['nonmanifold'] or a['degenerate'] or a['volume']<=0},'images':imgs}
for mode in ['material','white']:
 for a,b in [('R09','R10')]:
  x,y=S[a+'_'+mode],S[b+'_'+mode];R[a+'_'+b+'_'+mode]={'changed_mesh':[n for n in x['mesh'] if x['mesh'][n]['hash']!=y['mesh'][n]['hash']],'added_mesh':list(y['mesh'].keys()-x['mesh'].keys()),'removed_mesh':list(x['mesh'].keys()-y['mesh'].keys()),'changed_local_geometry':[n for n in x['local'] if x['local'][n]!=y['local'][n]],'changed_uv':[n for n in x['uv'] if x['uv'][n]!=y['uv'][n]],'camera_equal':x['camera']==y['camera'],'old_camera_equal':all(x['camera'][n]==y['camera'][n] for n in x['camera']),'added_cameras':list(y['camera'].keys()-x['camera'].keys()),'light_equal':x['light']==y['light'],'world_equal':x['world']==y['world'],'visibility_equal':x['visibility']==y['visibility'],'old_visibility_equal':all(x['visibility'][n]==y['visibility'][n] for n in x['visibility']),'added_visibility':{n:y['visibility'][n] for n in y['visibility'].keys()-x['visibility'].keys()},'changed_material_nodes':[n for n in x['materials'] if x['materials'][n]!=y['materials'][n]],'material_node_before_after':{n:[x['materials'][n],y['materials'][n]] for n in x['materials'] if x['materials'][n]!=y['materials'][n]}}
R['R10_material_white']={k:S['R10_material'][k]==S['R10_white'][k] for k in ['mesh','uv','camera','light','world','visibility']}
(Q/'R10-diff-check.json').write_text(json.dumps(R,indent=2));print('DONE')
