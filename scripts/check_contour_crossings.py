import ast,json,pathlib
P=pathlib.Path(__file__).resolve().parents[1]
def getpoly(p):
 for n in ast.parse(p.read_text()).body:
  if isinstance(n,ast.Assign) and any(isinstance(a,ast.Name) and a.id=='LL' for a in n.targets):return ast.literal_eval(n.value)
def smooth(p):
 out=[]
 for i in range(len(p)):
  a,b,c,d=[p[j%len(p)] for j in [i-1,i,i+1,i+2]]
  for j in range(4):
   t=j/4;out.append(tuple(.5*(2*b[k]+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t) for k in [0,1]))
 return out
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
r={}
for rev,file in [('R01','build_r01.py'),('R03','refine_r03.py')]:
 p=smooth(getpoly(P/'scripts'/file));bad=[]
 for i in range(len(p)):
  a,b=p[i],p[(i+1)%len(p)]
  for j in range(i+2,len(p)):
   if i==0 and j==len(p)-1:continue
   c,d=p[j],p[(j+1)%len(p)]
   if cross(a,b,c)*cross(a,b,d)<0 and cross(c,d,a)*cross(c,d,b)<0:bad.append({'i':i,'j':j,'segment1':[a,b],'segment2':[c,d]})
 r[rev]={'sampled_vertices':len(p),'strict_segment_crossings':bad}
(P/'qa/R03-lower-contour-crossing-evidence-repeat.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
