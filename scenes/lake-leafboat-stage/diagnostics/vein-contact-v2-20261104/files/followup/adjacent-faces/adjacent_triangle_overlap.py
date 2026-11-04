"""Float64 off-shared-simplex triangle-intersection diagnostic, not exact arithmetic."""
import math
from itertools import combinations
from triangle_distance import sub,add,mul,dot,cross,length2,point_triangle2,segment_segment2
EPS=1e-9

def segment_hit(p,q,a,b,c):
 d=sub(q,p);e1=sub(b,a);e2=sub(c,a);h=cross(d,e2);det=dot(e1,h)
 if abs(det)<1e-18:return None
 v=sub(p,a);u=dot(v,h)/det
 if u < -EPS or u>1+EPS:return None
 k=cross(v,e1);w=dot(d,k)/det
 if w < -EPS or u+w>1+EPS:return None
 t=dot(e2,k)/det
 if t < -EPS or t>1+EPS:return None
 return add(p,mul(d,min(1,max(0,t))))
def point_segment2(p,a,b):
 ab=sub(b,a);den=length2(ab)
 if den==0:return length2(sub(p,a))
 return length2(sub(p,add(a,mul(ab,min(1,max(0,dot(sub(p,a),ab)/den))))))
def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def coplanar_clip(a,b,normal):
 drop=max(range(3),key=lambda i:abs(normal[i]));axes=[i for i in range(3) if i!=drop]
 project=lambda p:(p[axes[0]],p[axes[1]])
 bb=[project(p) for p in b];sign=1 if orient(*bb)>=0 else -1;poly=list(a)
 for j in range(3):
  edgea,edgeb=bb[j],bb[(j+1)%3];new=[]
  for p,q in zip(poly,poly[1:]+poly[:1]):
   dp=sign*orient(edgea,edgeb,project(p));dq=sign*orient(edgea,edgeb,project(q))
   pin=dp>=-1e-14;qin=dq>=-1e-14
   if pin:new.append(p)
   if pin!=qin:
    den=dp-dq
    if abs(den)>1e-30:new.append(add(p,mul(sub(q,p),dp/den)))
  poly=new
  if not poly:break
 return poly

def off_shared_extent(a,b,shared):
 na=cross(sub(a[1],a[0]),sub(a[2],a[0]));nb=cross(sub(b[1],b[0]),sub(b[2],b[0]));la=math.sqrt(length2(na));lb=math.sqrt(length2(nb))
 if la<1e-18 or lb<1e-18:raise ValueError('Degenerate triangle')
 parallel=length2(cross(na,nb))/(la*la*lb*lb)<1e-18
 sameplane=max(abs(dot(na,sub(p,a[0])))/la for p in b)<1e-9
 if parallel and sameplane:points=coplanar_clip(a,b,na);mode='coplanar_clip'
 else:
  points=[];mode='edge_plane'
  for x,y in [(a,b),(b,a)]:
   for i in range(3):
    p=segment_hit(x[i],x[(i+1)%3],*y)
    if p is not None:points.append(p)
 if len(shared)==1:dist=lambda p:math.sqrt(length2(sub(p,shared[0])))
 elif len(shared)==2:dist=lambda p:math.sqrt(point_segment2(p,*shared))
 else:raise ValueError('Need one or two shared vertices')
 return max((dist(p) for p in points),default=0.),mode,len(points)

def tests():
 a=((0.,0.,0.),(1.,0.,0.),(0.,1.,0.));cases=[
 ('edge_only_flat',a,((0.,0.,0.),(1.,0.,0.),(0.,-1.,0.)),[a[0],a[1]],False),
 ('shared_edge_coplanar_overlap',a,((0.,0.,0.),(1.,0.,0.),(.5,.5,0.)),[a[0],a[1]],True),
 ('edge_only_fold',a,((0.,0.,0.),(1.,0.,0.),(0.,0.,1.)),[a[0],a[1]],False),
 ('vertex_only',a,((0.,0.,0.),(-1.,0.,0.),(0.,-1.,0.)),[a[0]],False),
 ('shared_vertex_piercing',a,((0.,0.,0.),(.5,.5,-1.),(.5,.5,1.)),[a[0]],True),
 ('vertex_coplanar_overlap',a,((0.,0.,0.),(.5,.1,0.),(.1,.5,0.)),[a[0]],True)]
 out=[]
 for name,a,b,sh,expected in cases:
  extent,mode,n=off_shared_extent(a,b,sh);rev=off_shared_extent(b,a,sh)[0];actual=extent>1e-6
  assert actual==expected and abs(extent-rev)<1e-9,(name,extent,rev)
  out.append(dict(name=name,extent=extent,expected_overlap=expected,observed_overlap=actual,mode=mode,symmetry_error=abs(extent-rev)))
 return out
if __name__=='__main__':print(tests())
