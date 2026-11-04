import bpy,bmesh,json,hashlib,math,pathlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-qa-20261104')
def snap():
 out={}
 for o in bpy.context.scene.objects:
  if o.type=='MESH':
   bm=bmesh.new();bm.from_mesh(o.data)
   coords=[tuple(o.matrix_world@v.co) for v in o.data.vertices];faces=[list(p.vertices) for p in o.data.polygons]
   out[o.name]={'vertices':len(coords),'faces':len(faces),'worldhash':hashlib.sha256(repr((coords,faces)).encode()).hexdigest(),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.calc_area()<1e-12 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True),'hidden':o.hide_render};bm.free()
 return out
R={}
for mode in ['material','white']:
 f=P/'models'/f'R06_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(f));R[mode]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'meshes':snap(),'cameras':{o.name:[list(row) for row in o.matrix_world] for o in bpy.context.scene.objects if o.type=='CAMERA'}}
R['shared_geometry']=R['material']['meshes']==R['white']['meshes'];R['shared_cameras']=R['material']['cameras']==R['white']['cameras']
# World BVH of shell only, excluding glazing (none), detail ornament and exterior.
V=[];F=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith(('WALL_','DOOR_','COLUMN_','ROOF_','HALL_floor')):
  o.data.calc_loop_triangles();off=len(V);V.extend(o.matrix_world@v.co for v in o.data.vertices);F.extend(tuple(off+i for i in t.vertices) for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(V,F,all_triangles=True)
def ray(p,d,limit):
 hit=bvh.ray_cast(Vector(p),Vector(d),limit);return {'origin':p,'direction':d,'limit':limit,'hit':hit[0] is not None,'distance':hit[3],'point':list(hit[0]) if hit[0] else None}
R['apertures']=[]
for k in range(16):
 a=-math.pi/2+k*math.tau/16;d=[math.cos(a),math.sin(a),0]
 for z in ([.48,1,2.5,3.9] if k in (0,8) else [2,3.22,4.3]):
  R['apertures'].append({'bay':k,'z':z,**ray([5*d[0],5*d[1],z],d,2)})
R['seam_radial']=[]
for k in range(16):
 a=-math.pi/2+(k+.5)*math.tau/16;d=[math.cos(a),math.sin(a),0]
 for z in [.45,.58,2.95,5.45,5.52]:R['seam_radial'].append({'boundary':k,'z':z,**ray([5*d[0],5*d[1],z],d,2)})
R['roof_vertical']=[]
for k in range(24):
 a=k*math.tau/24
 for r in [0,5.7,6,6.15]:R['roof_vertical'].append(ray([r*math.cos(a),r*math.sin(a),5.4],[0,0,1],2))
(Q/'R06-check.json').write_text(json.dumps(R,indent=2));print('DONE',len(R['material']['meshes']),[n for n,v in R['material']['meshes'].items() if v['nonmanifold'] or v['degenerate'] or v['signed_volume']<=0]);print('shared',R['shared_geometry'],R['shared_cameras']);print('seam_misses',sum(not x['hit'] for x in R['seam_radial']),'roofmiss',sum(not x['hit'] for x in R['roof_vertical']))
