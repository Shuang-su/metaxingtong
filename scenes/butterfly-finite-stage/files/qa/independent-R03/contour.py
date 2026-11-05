import ast,json,pathlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/butterfly-finite-stage-20261105');O=pathlib.Path(__file__).parent
# Independent scalar Catmull-Rom closed sampler, matching documented t in [0,.25,.5,.75].
def sample(p):
 out=[];N=len(p)
 for i in range(N):
  q=[p[(i+j)%N] for j in [-1,0,1,2]]
  for t in [0,.25,.5,.75]:out.append(tuple(.5*(2*q[1][k]+(-q[0][k]+q[2][k])*t+(2*q[0][k]-5*q[1][k]+4*q[2][k]-q[3][k])*t*t+(-q[0][k]+3*q[1][k]-3*q[2][k]+q[3][k])*t*t*t) for k in range(2)))
 return out
def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
out={}
for v,f in [('R01','build_r01.py'),('R03','refine_r03.py')]:
 t=ast.parse((P/'scripts'/f).read_text());poly=next(ast.literal_eval(n.value)for n in t.body if isinstance(n,ast.Assign)and any(isinstance(k,ast.Name)and k.id=='LL'for k in n.targets));p=sample(poly);N=len(p);hits=[]
 for i in range(N):
  for j in range(i+2,N):
   if i==0 and j==N-1:continue
   a,b,c,d=p[i],p[(i+1)%N],p[j],p[(j+1)%N]
   if orient(a,b,c)*orient(a,b,d)<-1e-12 and orient(c,d,a)*orient(c,d,b)<-1e-12:hits.append([i,j])
 out[v]={'sample_count':N,'strict_crossings':hits,'limit':'Strict crossing test only; does not alone certify no collinear overlap/tangencies or 3D shell self-intersection.'}
(O/'contour-check.json').write_text(json.dumps(out,indent=2));print(out)
