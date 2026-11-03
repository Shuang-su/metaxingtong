import bpy,json,hashlib,struct,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path('/workspace/scratch/fa58bfcf0425/cityroom-refinement-20261103');O=Path(__file__).parent
fit=json.load(open(P/'qa/R09b-camera-fit.json'))
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));a={};cams={}
 for o in bpy.data.objects:
  if o.type=='MESH':
   h=hashlib.sha256()
   for v in o.data.vertices:h.update(struct.pack('ddd',*(o.matrix_world@v.co)))
   for f in o.data.polygons:h.update(str(tuple(f.vertices)).encode())
   a[o.name]=h.hexdigest()
  if o.type=='CAMERA':cams[o.name]={'matrix':list(map(list,o.matrix_world)),'lens':o.data.lens,'shift':[o.data.shift_x,o.data.shift_y]}
 return {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'geometry':a,'cameras':cams,'hidden':[o.name for o in bpy.data.objects if o.type=='MESH' and (o.hide_render or o.hide_viewport)]}
a=snapshot(P/'models/R08_material.blend');b=snapshot(P/'models/R09b_material.blend');out={'baseline':a,'trial':b,'geometry_equal':a['geometry']==b['geometry'],'changed_cameras':[k for k in a['cameras'] if a['cameras'][k]!=b['cameras'][k]],'projection':[]}
for r in fit['results']:
 cam=bpy.data.objects[r['camera']];s=bpy.context.scene;s.render.resolution_x=r['width'];s.render.resolution_y=r['height'];s.render.resolution_percentage=100
 pts=[]
 for radius,z in [(.315,.903),(.301,0),(.098,.455)]:
  pts += [Vector((radius*math.cos(t*2*math.pi/512),1.25+radius*math.sin(t*2*math.pi/512),z)) for t in range(512)]
 pts += [Vector((x,4.98,z)) for x in [1.345,1.4,1.455] for z in [.18,6.438]]
 errors=[];depth=[]
 for p in pts:
  q=cam.matrix_world.inverted()@p;depth.append(-q.z);u=world_to_camera_view(s,cam,p);manual=(r['width']/2+r['fixed_focal_px']*q.x/-q.z,r['height']/2-r['fixed_focal_px']*q.y/-q.z);errors.append(math.hypot(u.x*r['width']-manual[0],(1-u.y)*r['height']-manual[1]))
 out['projection'].append({'camera':r['camera'],'sample_count':len(pts),'min_forward_depth':min(depth),'max_forward_depth':max(depth),'max_blender_vs_pinhole_px':max(errors)})
(O/'R09b-independent-check.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['baseline','trial']},indent=2))
