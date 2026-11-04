import bpy,json,hashlib,math
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];inp=R/'inputs/r06-material-frozen.blend'
assert hashlib.sha256(inp.read_bytes()).hexdigest()=='591c0347a4ab63be9f7c6028058874d846fb16e3ba10c5e4c18775a40ed06d06'
def mesh_state(o):return {'matrix':[list(x) for x in o.matrix_world],'verts':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'materials':[m.name for m in o.data.materials],'hide':[o.hide_render,o.hide_viewport]}
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
results=[]
for name,ratio in [('baseline',1.0),('height060',.60),('height082',.82)]:
 bpy.ops.wm.open_mainfile(filepath=str(inp));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_percentage=100
 before={o.name:mesh_state(o) for o in s.objects if o.type=='MESH'};cams={o.name:{'matrix':[list(x) for x in o.matrix_world],'lens':o.data.lens,'shift':[o.data.shift_x,o.data.shift_y],'sensor':[o.data.sensor_width,o.data.sensor_height],'sensor_fit':o.data.sensor_fit} for o in s.objects if o.type=='CAMERA'}
 bottom_errors={};param=[]
 for o in s.objects:
  if not o.name.startswith(('white-key-','black-key-')):continue
  z0=min(v.co.z for v in o.data.vertices);z1=max(v.co.z for v in o.data.vertices);bottom={v.index:o.matrix_world@v.co.copy() for v in o.data.vertices if abs(v.co.z-z0)<1e-7}
  for v in o.data.vertices:v.co.z=z0+ratio*(v.co.z-z0)
  bottom_errors[o.name]=max((o.matrix_world@o.data.vertices[i].co-p).length for i,p in bottom.items());param.append({'name':o.name,'local_z_bottom':z0,'old_local_top':z1,'new_local_top':z0+ratio*(z1-z0),'ratio':ratio,'fixed_bottom_vertices':list(bottom),'world_top_z':max((o.matrix_world@v.co).z for v in o.data.vertices)})
 bpy.context.view_layer.update()
 after={o.name:mesh_state(o) for o in s.objects if o.type=='MESH'};unchanged=[n for n in before if not n.startswith(('white-key-','black-key-'))]
 assert all(before[n]==after[n] for n in unchanged);assert max(bottom_errors.values())==0
 camafter={o.name:{'matrix':[list(x) for x in o.matrix_world],'lens':o.data.lens,'shift':[o.data.shift_x,o.data.shift_y],'sensor':[o.data.sensor_width,o.data.sensor_height],'sensor_fit':o.data.sensor_fit} for o in s.objects if o.type=='CAMERA'};assert cams==camafter
 out={'name':name,'white_ratio':ratio,'black_ratio':ratio,'input_sha256':hashlib.sha256(inp.read_bytes()).hexdigest(),'operation':'memory only local Z affine about each original bottom face; no save_as_mainfile; positions/rotations/materials/cameras unchanged','other_meshes_exact_unchanged':len(unchanged),'all_11_cameras_exact_unchanged':cams==camafter,'bottom_vertex_world_max_error':max(bottom_errors.values()),'before_mesh_state_sha256':digest(before),'after_mesh_state_sha256':digest(after),'parameter_rows':param,'projected_geometry_boxes':{}}
 white_tops=[x['world_top_z'] for x in param if x['name'].startswith('white')];black_tops=[x['world_top_z'] for x in param if x['name'].startswith('black')];out['white_minus_black_top_world_z_min']=min(white_tops)-max(black_tops);assert min(white_tops)>max(black_tops)
 folder=R/'results'/name;folder.mkdir(exist_ok=True)
 for src in [17,20,21]:
  cam=s.objects[f'source{src}-conditional'];rows=[]
  for o in s.objects:
   if not o.name.startswith(('white-key-','black-key-')):continue
   ps=[world_to_camera_view(s,cam,o.matrix_world@v.co) for v in o.data.vertices];xs=[p.x*1192 for p in ps];ys=[(1-p.y)*671 for p in ps];rows.append({'id':o.name,'bbox_xyxy':[min(xs),min(ys),max(xs),max(ys)],'all_positive_depth':all(p.z>0 for p in ps)})
  out['projected_geometry_boxes'][str(src)]=rows;s.camera=cam;s.render.filepath=str(folder/f'source{src}.png');bpy.ops.render.render(write_still=True)
 (folder/'state.json').write_text(json.dumps(out,indent=2));results.append(out)
(R/'results/trial-index.json').write_text(json.dumps({'baseline_input_sha256':hashlib.sha256(inp.read_bytes()).hexdigest(),'render_dimensions':[1192,671],'samples':8,'denoising':False,'threads':6,'trials':results,'warning':'Uncalibrated same-screen geometry-box comparisons are not visible silhouettes, source instance correspondence, or geometric acceptance.'},indent=2))
