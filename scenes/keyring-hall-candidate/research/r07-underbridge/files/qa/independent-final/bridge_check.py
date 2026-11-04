import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).parent;root=O.parent
base=root/'keyring-hall-candidate-20261104/versions/R06/models/keyring-material.blend';new=root/'keyring-underbridge-r07-20261104/models/r07-material.blend'
def snap():
 d={};dg=bpy.context.evaluated_depsgraph_get()
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();d[o.name]={'v':[list(o.matrix_world@v.co) for v in m.vertices],'f':[list(t.vertices) for t in m.loop_triangles],'uv':[[list(x.uv) for x in l.data] for l in m.uv_layers],'hide':[o.hide_render,o.hide_viewport]};e.to_mesh_clear()
 c={o.name:([list(r) for r in o.matrix_world],o.data.lens,o.data.shift_x,o.data.shift_y) for o in bpy.context.scene.objects if o.type=='CAMERA'}
 return d,c
bpy.ops.wm.open_mainfile(filepath=str(base));d0,c0=snap();bpy.ops.wm.open_mainfile(filepath=str(new));d,c=snap();out={'model_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'original_162_exact':all(d[n]==x for n,x in d0.items()),'old_11_cameras_exact':all(c[n]==x for n,x in c0.items()),'added_meshes':sorted(set(d)-set(d0)),'added_cameras':sorted(set(c)-set(c0))}
bv={n:BVHTree.FromPolygons(x['v'],x['f'],all_triangles=True) for n,x in d.items()}
def inside(n,p):
 # signed solid angle over all actual evaluated triangles, independent of BVH parity
 s=0.;p=Vector(p)
 for f in d[n]['f']:
  a,b,c=(Vector(d[n]['v'][i])-p for i in f);la,lb,lc=a.length,b.length,c.length
  s+=2*math.atan2(a.dot(b.cross(c)),la*lb*lc+a.dot(b)*lc+b.dot(c)*la+c.dot(a)*lb)
 return s/(4*math.pi)
relations=[];witness=[]
for n in out['added_meshes']:
 pairs=[]
 for k in d0:
  ov=bv[n].overlap(bv[k])
  if ov:pairs.append({'other':k,'triangle_pairs':len(ov)})
 relations.append({'bridge':n,'surface_relations':pairs})
 # use mid-facet angle, not arc vertex: finite positive-volume witnesses
 if 'central-step' in n: pars=[('stage-central-solid',4.992,-.275),('stage-step-ring',5.025,-.275)];a=math.pi/96
 else:pars=[('stage-step-ring',5.995,-.375),('stage-outer-floor',6.025,-.375)];a=2.0734511513692637/96
 for k,r,z in pars:
  p=(r*math.sin(a),r*math.cos(a),z);witness.append({'bridge':n,'stage':k,'point':p,'bridge_winding':inside(n,p),'stage_winding':inside(k,p),'bridge_surface_distance':bv[n].find_nearest(Vector(p))[3],'stage_surface_distance':bv[k].find_nearest(Vector(p))[3]})
out['bridge_relations']=relations;out['finite_joint_interior_witnesses']=witness
names=['stage-central-solid','stage-step-ring','stage-outer-floor']+out['added_meshes']
def hit(x,y):return any(bv[n].ray_cast(Vector((x,y,5)),Vector((0,0,-1)),10)[0] is not None for n in names)
pts=[(x*.2,y*.2) for x in range(-24,25) for y in range(-24,25) if (x*.2)**2+(y*.2)**2<4.85**2];out['rays']={'central':{'samples':len(pts),'hits':sum(hit(*p) for p in pts)}}
for label,r,aa,bb in [('step',5.5,-math.pi,math.pi),('outer',7.5,-2,2),('central_gap',5.01,-math.pi,math.pi),('outer_gap',6.01,-2,2)]:
 pts=[(r*math.sin(a:=aa+(bb-aa)*i/180),r*math.cos(a)) for i in range(181)];out['rays'][label]={'samples':len(pts),'hits':sum(hit(*p) for p in pts)}
(O/'bridge-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
