import bpy,pathlib,json,math
from mathutils import Vector
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-mannequin-qa-20261104');R={};S={}
for ver in ['R05','R06']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'{ver}_material.blend'));upper=bpy.data.objects['MANNEQUIN_red_upper_clothing_proxy'];upper.data.calc_loop_triangles();ts=[[upper.matrix_world@upper.data.vertices[i].co for i in t.vertices]for t in upper.data.loop_triangles];S[ver]={};R[ver]={}
 def wind(p):
  total=0
  for t in ts:
   a,b,c=[v-p for v in t];den=a.length*b.length*c.length+a.dot(b)*c.length+b.dot(c)*a.length+c.dot(a)*b.length;total+=2*math.atan2(a.dot(b.cross(c)),den)
  return total/(4*math.pi)
 for side in [-1,1]:
  n=f'MANNEQUIN_red_bifurcated_lower_proxy_{side}';o=bpy.data.objects[n];v=[o.matrix_world@x.co for x in o.data.vertices];S[ver][n]=[list(x)for x in v];cap=v[-24:];cen=sum(cap,Vector())/24;probes=cap+[cen]+[(cen+cap[i]+cap[(i+1)%24])/3 for i in range(24)];w=[wind(p)for p in probes];R[ver][n]={'cap_probes':49,'inside_abs_winding_close1':sum(abs(abs(x)-1)<1e-5 for x in w),'winding':w,'scope':'24 rim vertices+center+24 fan triangle centroids, finite sample not every point/full self-occlusion proof'}
R['diff']={}
for n,a in S['R05'].items():
 b=S['R06'][n];ids=[i for i,(x,y)in enumerate(zip(a,b)) if x!=y];R['diff'][n]={'changed_ids':ids,'all_z_equal':all(x[2]==y[2]for x,y in zip(a,b)),'lower72_exactly_equal':a[:72]==b[:72]}
(Q/'R06-cap-containment.json').write_text(json.dumps(R,indent=2));print({k:{n:x.get('inside_abs_winding_close1')for n,x in v.items()}for k,v in R.items()})
