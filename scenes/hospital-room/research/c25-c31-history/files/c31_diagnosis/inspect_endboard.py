import json,numpy as np
from collections import Counter,defaultdict
from pathlib import Path
P=Path(__file__).resolve().parent;D=json.load(open(P.parent/'c30_diagnosis/c28_actual_bed_objects.json'))
k='Bed • observed endboard, consistent width';o=D[k];v=np.array(o['verts_local']);m=np.array(o['matrix_world']);v=v@m[:3,:3].T+m[:3,3]
# Front planar surface at minimum world X: count edges belonging to coplanar faces.
faces=[f for f in o['faces'] if np.ptp(v[f,0])<1e-6 and abs(v[f[0],0]-v[:,0].min())<1e-6]
c=Counter(tuple(sorted((a,b))) for f in faces for a,b in zip(f,f[1:]+f[:1]));edges=[e for e,n in c.items() if n==1];adj=defaultdict(list)
for a,b in edges:adj[a].append(b);adj[b].append(a)
loops=[];todo=set(adj)
while todo:
 stack=[todo.pop()];ids=[]
 while stack:
  a=stack.pop();ids.append(a)
  for b in adj[a]:
   if b in todo:todo.remove(b);stack.append(b)
 w=v[ids];loops.append({'vertex_count':len(ids),'world_min':w.min(0).tolist(),'world_max':w.max(0).tolist(),'vertex_ids':ids,'yz':w[:,1:].tolist()})
r={'object':k,'method':'Minimum-world-X planar-face boundary connected components; closed degree-two contours identify external outline and two holes','front_planar_face_count':len(faces),'boundary_degrees':dict(Counter(map(len,adj.values()))),'loops':loops}
json.dump(r,open(P/'actual_endboard_hole_geometry.json','w'),indent=2)
for q in loops: print(q['vertex_count'],q['world_min'],q['world_max'])
from PIL import Image,ImageDraw
for name in ['1801.323','1804.861']:
 im=Image.open(P.parent/f'c26/new_evidence/frame_{name}.png'); im.crop((580,830,1560,1030)).resize((1960,400)).save(P/f'{name}_endboard_crop2x.png')
