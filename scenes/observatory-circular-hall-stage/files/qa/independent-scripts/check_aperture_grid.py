import bpy,math,pathlib,json,hashlib,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-qa-20261104')
s=.25;c=.55;cz=4.36;bz=1.35;t=math.acos(s/c)
poly=[(s,bz),(s,cz-c*math.sin(t))]+[(c*math.cos(-t+(math.pi+2*t)*j/48),cz+c*math.sin(-t+(math.pi+2*t)*j/48)) for j in range(1,49)]+[(-s,bz)]+[(s*math.cos(math.pi+math.pi*j/24),bz+s*math.sin(math.pi+math.pi*j/24)) for j in range(1,25)]
poly=poly[:-1]
def inside(x,z):
 yes=False
 for (x1,z1),(x2,z2) in zip(poly,poly[1:]+poly[:1]):
  if (z1>z)!=(z2>z) and x<(x2-x1)*(z-z1)/(z2-z1)+x1:yes=not yes
 return yes
def boundary_dist(x,z):
 out=1e9
 for (a,b),(c,d) in zip(poly,poly[1:]+poly[:1]):
  dx=c-a;dz=d-b;tt=max(0,min(1,((x-a)*dx+(z-b)*dz)/(dx*dx+dz*dz)));out=min(out,math.hypot(x-a-tt*dx,z-b-tt*dz))
 return out
half=6*math.tan(math.pi/12);grid=[(-half+.015+(2*half-.03)*i/80,.415+5.07*j/130) for i in range(81) for j in range(131)]
grid=[(x,z,inside(x,z)) for x,z in grid if boundary_dist(x,z)>1e-5]
R={'grid_per_bay':len(grid),'grid_boundary_exclusion':1e-5,'tested_bounds':[-half+.015,half-.015,.415,5.485],'expected_polygon':poly,'versions':{}}
for version in ['R03','R04']:
 f=P/'models'/f'{version}_material.blend';bpy.ops.wm.open_mainfile(filepath=str(f));res={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'panels':{},'all_mesh_bad':[]}
 for o in bpy.context.scene.objects:
  if o.type=='MESH':
   bm=bmesh.new();bm.from_mesh(o.data);v={'name':o.name,'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.calc_area()<1e-12 for f in bm.faces),'volume':bm.calc_volume(signed=True)};bm.free()
   if v['nonmanifold'] or v['degenerate'] or v['volume']<=0:res['all_mesh_bad'].append(v)
 for k in range(12):
  if k in (0,6):continue
  o=bpy.data.objects[f'WALL_{k:02d}_perforated'];o.data.calc_loop_triangles();tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices) for t in o.data.loop_triangles],all_triangles=True)
  a=-math.pi/2+k*math.tau/12;d=Vector((math.cos(a),math.sin(a),0)); counts={'open_expected':0,'wall_expected':0,'blocked_hole':0,'unplanned_hole':0,'first_mismatches':[]}
  for x,z,wantopen in grid:
   p=Vector((5.5*math.cos(a)-x*math.sin(a),5.5*math.sin(a)+x*math.cos(a),z));hit=tree.ray_cast(p,d,1)[0] is not None;counts['open_expected' if wantopen else 'wall_expected']+=1
   if hit==wantopen:
    counts['blocked_hole' if wantopen else 'unplanned_hole']+=1
    if len(counts['first_mismatches'])<12:counts['first_mismatches'].append([x,z,wantopen])
  res['panels'][o.name]=counts
 R['versions'][version]=res
(Q/'R04-aperture-grid.json').write_text(json.dumps(R,indent=2));print('DONE',[(v,sum(p['unplanned_hole'] for p in r['panels'].values()),sum(p['blocked_hole'] for p in r['panels'].values()),r['all_mesh_bad']) for v,r in R['versions'].items()])
