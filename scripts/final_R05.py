import bpy,bmesh,os,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[-6:]))
D=Path(__file__).resolve().parents[1];reports={}
for mode in['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R04_{mode}.blend'));s=bpy.context.scene;s.render.threads=6;s.cycles.samples=32;s.cycles.use_denoising=False
 # Correct finite near frame slant, not animated recursive motif.
 for prefix,y,delta in[('FRAME_NEAR',3.74,-60),('FRAME_SECOND',4.02,59)]:
  center=Vector((0,y,1.32));rot=Matrix.Rotation(math.radians(delta),4,'Y');T=Matrix.Translation(center)@rot@Matrix.Translation(-center)
  for o in s.objects:
   if o.name.startswith(prefix):o.matrix_world=T@o.matrix_world;o['R05_note']='Finite frame pose conditional from visible near-frame slant; dynamic recursive frames omitted'
 # Keep inferred front closure out of all trained crops, do not confuse it with real endpoint.
 stage=bpy.data.objects['STAGE_shared_rounded_lobes'];verts=list(stage.data.vertices);ys=sorted(set(round(v.co.y,5)for v in verts));cutoff=ys[1]+1e-4
 # Two forward outline points are those from explicit inferred pixel connections 1250.
 protocol=json.loads((D/'models/R04-stage-conditional-protocol.json').read_text());frontpts=protocol['world_polygon'][10:12] # verify against pixel count below rather than relying on assumed ordering
 n=len(protocol['world_polygon']);frontidx=[len(protocol['world_polygon'])-len(protocol['observed_left_top_edge_px'])-3,len(protocol['world_polygon'])-len(protocol['observed_left_top_edge_px'])-2]
 # Explicit polygon sequence:3 inferred back +7 reversed right +2 front +7 reversed left+1 end =20.
 frontidx=[10,11]
 for i in frontidx:
  for j in[i,i+n]:stage.data.vertices[j].co.y-=5
 border=bpy.data.objects['STAGE_shared_border']
 for i in frontidx:border.data.splines[0].points[i].co.y-=4.95
 # Style is approximate, not source material acceptance. Slightly darker physical red bases.
 if mode=='material':
  for name,c in[('Deep red lacquer',(.31,.009,.005)),('Orange rear board',(.65,.105,.022)),('Red umbrella paper',(.48,.012,.045))]:
   m=bpy.data.materials[name];m.diffuse_color=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1)
 # Internal check cameras are NOT new source viewpoints; same scene, no hiding.
 for i in range(8):
  a=2*math.pi*i/8;loc=(12*math.cos(a),1+12*math.sin(a),6 if i%2==0 else 4.5);bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=f'CHECK_{i:02d}';o.rotation_euler=(Vector((0,1,1.6))-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=24
 bpy.ops.object.camera_add(location=(9,-12,7));o=bpy.context.object;o.name='MAIN';o.rotation_euler=(Vector((0,1.2,1.3))-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=28
 s.camera=bpy.data.objects['SOURCE_P1_45'];s['R05_status']='FROZEN conditional remake; source alignment/unknown support/background/shape incomplete, all source angles training, no acceptance'
 deps=bpy.context.evaluated_depsgraph_get();audit=[];geometry=[]
 for o in s.objects:
  if o.type not in['MESH','CURVE']:continue
  ev=o.evaluated_get(deps);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me);bm.transform(o.matrix_world);boundary=sum(e.is_boundary for e in bm.edges);vol=bm.calc_volume(signed=True)if boundary==0 else None
  audit.append({'name':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':boundary,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume':vol,'min_z':min(v.co.z for v in bm.verts),'max_z':max(v.co.z for v in bm.verts),'open_leaf_intentional':o.name.startswith('PLANT_leaf')})
  geometry.append((o.name,[list(v.co)for v in bm.verts],[list(v.index for v in f.verts)for f in bm.faces]));bm.free();ev.to_mesh_clear()
 gh=hashlib.sha256(json.dumps(geometry,separators=(',',':')).encode()).hexdigest();reports[mode]={'geometry_sha256':gh,'objects':audit,'ground_actual_top_z':0,'umbrella_min_z':min(x['min_z']for x in audit if x['name'].startswith('UMBRELLA')),'stage_contact_bottom_z':min(x['min_z']for x in audit if x['name']=='STAGE_shared_rounded_lobes'),'limits':'Normal/closed topology pass not assembly/source pass. Intersecting stem/leaves, cap/band partial overlap, back closure and dimensions inferred. No hidden supports fabricated.'}
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/R05_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/R05_{mode}.glb'),export_format='GLB',export_cameras=True,export_lights=False)
(D/'models/R05-evaluated-audit.json').write_text(json.dumps(reports,indent=2));print('R05_FROZEN')
