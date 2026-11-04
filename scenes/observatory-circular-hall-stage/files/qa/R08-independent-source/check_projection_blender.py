import bpy,json,pathlib,hashlib,math
from mathutils import Matrix,Vector
from bpy_extras.object_utils import world_to_camera_view
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-exterior-fit-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-source15-qa-20261104');G=json.loads((P/'geometry.json').read_text());T=json.loads((P/'trials.json').read_text());F=json.loads((Q/'camera-fit-math-check.json').read_text());bpy.ops.wm.open_mainfile(filepath=G['model_path']);s=bpy.context.scene;s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100
checks={}
for n,o in G['objects'].items():
 ob=bpy.data.objects[n];coords=[list(ob.matrix_world@v.co) for v in ob.data.vertices];checks[n]={'max_coordinate_error':max(abs(x-y) for a,b in zip(coords,o['vertices']) for x,y in zip(a,b)),'counts_equal':len(coords)==len(o['vertices'])}
cam=bpy.data.objects.new('QA_TEMP',bpy.data.cameras.new('QA_TEMP'));s.collection.objects.link(cam);cam.data.sensor_width=36;cam.data.sensor_fit='AUTO';R=[]
for t,f in zip(T['trials'],F):
 m=Matrix(t['camera_rotation']).to_4x4();m.translation=Vector(t['camera_position']);cam.matrix_world=m;cam.data.lens=t['lens'];bpy.context.view_layer.update();err=[];edges=[]
 for e,expected in zip(f['edges'],t['edges']):
  pts=e['world_endpoints'];actual=[]
  for p in pts:
   v=world_to_camera_view(s,cam,Vector(p));actual.append([v.x*1192,(1-v.y)*671])
  err.extend(abs(x-y) for a,b in zip(actual,expected) for x,y in zip(a,b));proof=[]
  for ref in e['objects']:
   ob=bpy.data.objects[ref['object']];ids=ref['matching_vertex_ids'];proof.append({'object':ob.name,'actual_mesh_edge':any(set(ed.vertices)==set(ids) for ed in ob.data.edges)})
  edges.append(proof)
 R.append({'lens':t['lens'],'max_Blender_projection_delta_px':max(err),'selected_real_edges':edges})
(Q/'camera-fit-blender-check.json').write_text(json.dumps({'model_sha_matches':hashlib.sha256(pathlib.Path(G['model_path']).read_bytes()).hexdigest()==G['model_sha256'],'geometry_export_matches':checks,'trials':R},indent=2));print(R)
