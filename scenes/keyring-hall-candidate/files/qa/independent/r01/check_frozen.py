import bpy,bmesh,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path('/workspace/scratch/fa58bfcf0425/independent-keyring-r01-qa-20261104/frozen');O=Path(__file__).parent
out={'hashes':{},'variants':{}}; snaps={}
def snap():
 s=bpy.context.scene;d={}; audits=[];dg=bpy.context.evaluated_depsgraph_get()
 for o in s.objects:
  if o.type!='MESH':continue
  e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();v=[tuple(o.matrix_world@x.co) for x in m.vertices];f=[tuple(x.vertices) for x in m.loop_triangles];bm=bmesh.new();bm.from_mesh(m)
  au={'name':o.name,'vertices':len(v),'triangles':len(f),'nonmanifold_edges':sum(not x.is_manifold for x in bm.edges),'degenerate_faces':sum(x.calc_area()<1e-12 for x in bm.faces),'signed_volume':bm.calc_volume(signed=True)};bm.free();audits.append(au)
  d[o.name]={'v':v,'f':f,'uv':[[tuple(x.uv) for x in l.data] for l in m.uv_layers],'hide':[o.hide_render,o.hide_viewport]};e.to_mesh_clear()
 cams={o.name:{'matrix':[list(r) for r in o.matrix_world],'lens':o.data.lens,'sensor_fit':o.data.sensor_fit,'viewframe':[list(v) for v in o.data.view_frame(scene=s)]} for o in s.objects if o.type=='CAMERA'}
 return d,cams,audits
for variant in ['material','white']:
 p=R/f'models/keyring-{variant}.blend';out['hashes'][str(p.name)]=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p));d,c,a=snap();snaps[variant]=(d,c)
 s=bpy.context.scene;world={'use_nodes':s.world.use_nodes,'color':list(s.world.color),'nodes':[{ 'type':n.bl_idname,'name':n.name,'inputs':{i.name:list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value for i in n.inputs if hasattr(i,'default_value') and i.type in ['RGBA','VALUE']}} for n in s.world.node_tree.nodes] if s.world.use_nodes else []}
 out['variants'][variant]={'mesh_count':len(d),'camera_count':len(c),'audit':a,'world':world,'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'images':[{'name':im.name,'path':im.filepath,'packed':bool(im.packed_file)} for im in bpy.data.images]}
 # Representative contact edges: actual evaluated triangle BVH, not bounds
 targets=[('bench-seat','bench-leg-0'),('piano-body-rim','piano-leg-0'),('piano-body-rim','piano-soundboard'),('piano-body-rim','piano-open-lid'),('stage-central-solid','stage-step-ring'),('stage-central-solid','four-point-concave-floor-inlay'),('stage-outer-floor','white-key-00'),('stage-outer-floor','white-key-18')]
 bv={n:BVHTree.FromPolygons(x['v'],x['f'],all_triangles=True) for n,x in d.items()};pairs=[]
 for x,y in targets:
  ds=[(bv[y].find_nearest(Vector(v))[3]) for v in d[x]['v']]; ds +=[(bv[x].find_nearest(Vector(v))[3]) for v in d[y]['v']]
  pairs.append({'a':x,'b':y,'bvh_surface_pairs':len(bv[x].overlap(bv[y])),'nearest_vertex_surface_upper_bound':min(ds)})
 out['variants'][variant]['representative_contacts']=pairs
 p=R/f'models/keyring-{variant}.glb';out['hashes'][p.name]=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p));bpy.context.scene.render.resolution_x=1192;bpy.context.scene.render.resolution_y=671;di,ci,ai=snap()
 errs={}
 for n,x in d.items():
  if n not in di:continue
  # actual all vertices bidirectional nearest, no bbox-only claim
  from mathutils.kdtree import KDTree
  def nn(a,b):
   kd=KDTree(len(b));[kd.insert(Vector(v),i) for i,v in enumerate(b)];kd.balance();return max(kd.find(Vector(v))[2] for v in a)
  errs[n]=max(nn(x['v'],di[n]['v']),nn(di[n]['v'],x['v']))
 ce={n:max(abs(c[n]['viewframe'][i][j]/abs(c[n]['viewframe'][i][2])-ci[n]['viewframe'][i][j]/abs(ci[n]['viewframe'][i][2])) for i in range(4) for j in [0,1]) for n in c if n in ci}
 out['variants'][variant]['glb']={'meshes':len(di),'cameras':len(ci),'missing_mesh':list(set(d)-set(di)),'missing_camera':list(set(c)-set(ci)),'max_world_vertex_bidirectional_error':max(errs.values()),'permesh_error':errs,'camera_normalized_frame_error':ce,'lights':sum(o.type=='LIGHT' for o in bpy.context.scene.objects)}
 (O/'check.json').write_text(json.dumps(out,indent=2))
out['shared_geometry_uv_visibility_exact']=snaps['material'][0]==snaps['white'][0];out['shared_cameras_exact']=snaps['material'][1]==snaps['white'][1];(O/'check.json').write_text(json.dumps(out,indent=2))
print('DONE',out['shared_geometry_uv_visibility_exact'])
