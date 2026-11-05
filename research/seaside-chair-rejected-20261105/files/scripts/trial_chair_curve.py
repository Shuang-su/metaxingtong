import bpy,bmesh,json,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=os.environ.get('MODEL_PATH',r+'/models/material.blend'))
cloth=[o for o in bpy.data.objects if o.name.startswith('C01 stripe')];original={o.name:o.data for o in cloth}
def tree(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[t.vertices[:] for t in o.data.loop_triangles],all_triangles=True)
def build(o,amp,N=32):
 old=original[o.name];lo=min(v.co.z for v in old.vertices);hi=max(v.co.z for v in old.vertices);corners=sorted([v.co.copy() for v in old.vertices if v.co.z==lo],key=lambda v:(v.x,v.y));assert len(corners)==4
 # ordered cross-section perimeter, local x/y.
 corners=[corners[i] for i in [0,2,3,1]];vs=[]
 for j in range(N+1):
  t=j/N
  for q in corners:
   v=q.copy();v.z=lo+(hi-lo)*t;w=o.matrix_world@v;w.z-=amp*t*(1-t);vs.append(o.matrix_world.inverted()@w)
 fs=[(3,2,1,0)]
 for j in range(N):
  for k in range(4):fs.append((4*j+k,4*j+(k+1)%4,4*(j+1)+(k+1)%4,4*(j+1)+k))
 fs.append(tuple(4*N+k for k in range(4)));me=bpy.data.meshes.new(o.name+' sag trial');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();return me
allmesh=[o for o in bpy.data.objects if o.type=='MESH'];out=[]
for amp in [0,.97]:
 for o in cloth:o.data=build(o,amp)
 bvs={o.name:tree(o) for o in allmesh};pairs=[]
 for o in cloth:
  for p in allmesh:
   if p in cloth:continue
   n=len(bvs[o.name].overlap(bvs[p.name]))
   if n:pairs.append({'cloth':o.name,'other':p.name,'triangle_intersections':n})
 checks=[]
 for o in cloth:
  bm=bmesh.new();bm.from_mesh(o.data);checks.append({'object':o.name,'vertices':len(o.data.vertices),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=True)});bm.free()
 neighbors=[]
 for i,o in enumerate(cloth):
  for p in cloth[i+1:]:
   n=len(bvs[o.name].overlap(bvs[p.name]))
   if n:neighbors.append({'a':o.name,'b':p.name,'triangle_intersections':n})
 wood=[o for o in allmesh if o.name.startswith('C01') and o not in cloth];inside=[]
 for o in cloth:
  old=original[o.name];mn=Vector(tuple(min(v.co[k] for v in old.vertices) for k in range(3)));mx=Vector(tuple(max(v.co[k] for v in old.vertices) for k in range(3)))
  for p in wood:
   inv=p.matrix_world.inverted();bmin=Vector(tuple(min(v.co[k] for v in p.data.vertices) for k in range(3)));bmax=Vector(tuple(max(v.co[k] for v in p.data.vertices) for k in range(3)));count=0;depth=0;ts=[]
   for j in range(129):
    t=j/128
    for u in [0,.25,.5,.75,1]:
     for v in [0,.25,.5,.75,1]:
      q=o.matrix_world@Vector((mn.x+(mx.x-mn.x)*u,mn.y+(mx.y-mn.y)*v,mn.z+(mx.z-mn.z)*t));tj=min(int(t*32),31);ta=tj/32;tb=(tj+1)/32;f=(t-ta)*32;q.z-=amp*((1-f)*ta*(1-ta)+f*tb*(1-tb));z=inv@q
      if all(bmin[k]+1e-7<z[k]<bmax[k]-1e-7 for k in range(3)):
       count+=1;ts.append(t);depth=max(depth,min(min(z[k]-bmin[k],bmax[k]-z[k]) for k in range(3)))
   if count:inside.append({'cloth':o.name,'wood':p.name,'samples_inside':count,'samples_total':3225,'t_range':[min(ts),max(ts)],'max_sample_depth_obb':depth})
 out.append({'neighbor_pairs':neighbors,'wood_volume_sampling':inside,'amplitude':amp,'max_sag':amp/4,'intersections_excluding_cloth':pairs,'topology':checks})
json.dump(out,open(r+'/qa/chair-curve-trial.json','w'),indent=2);print(out)
