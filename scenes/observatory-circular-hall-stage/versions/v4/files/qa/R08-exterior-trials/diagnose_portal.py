from fit import *
from PIL import Image
tr=json.load(open(P/'trials.json'));v=np.array(G['objects']['TERRACE_portal_00']['vertices']);outer=v[54:81];inner=v[81:108]
def distances(points,line):
 a=line[:-1];b=line[1:];d=b-a;res=[]
 for pt in points:
  t=np.clip(np.sum((pt-a)*d,axis=1)/np.sum(d*d,axis=1),0,1);res.append(float(np.min(np.linalg.norm(pt-(a+t[:,None]*d),axis=1))))
 return res
res=[]
for lens,p in [(18,initial)]+[(t['lens'],np.array(t['parameters'])) for t in tr['trials']]:
 oq,_=project(outer,p,lens);iq,_=project(inner,p,lens)
 res.append({'lens':lens,'baseline':bool(np.array_equal(p,initial)),'L10_outer':distances(A['L10']['pixels'],oq),'L11_inner':distances(A['L11']['pixels'],iq),'scope':'Conditional diagnostic front planar rim edges only, not full ray visibility. Not used in initial training.'})
json.dump(res,open(P/'portal-diagnostics.json','w'),indent=2)
src=np.array(Image.open(A and P.parent/'observatory-candidate-20261104/sources/report/15.png').convert('RGB')).astype('uint16')
for lens in [12,35]:
 r=np.array(Image.open(P/f'trial_{lens}mm.png').convert('RGB')).astype('uint16');Image.fromarray(((src+r)//2).astype('uint8')).save(P/f'trial_{lens}mm_direct50.png')
for row in res:print(row['lens'],row['baseline'],np.mean(row['L10_outer']),np.mean(row['L11_inner']))
