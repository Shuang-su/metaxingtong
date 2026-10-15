import json,numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).parent;D=json.load(open(R/'D_scene_meshes.json'));A=json.load(open(R.parent/'hospital_empty_frame_annotation_20261014/source_contour_branches_N640_G_H.json'))
MAP={'sofa_back_left':'Sofa • reclined back cushion 1','sofa_back_right':'Sofa • reclined back cushion 2','sofa_arm_left':'Sofa • broad padded arm','sofa_arm_right':'Sofa • broad padded arm.001','green_chair_back':'Chair • narrow curved wraparound back'}
def project(V,c):
 m=np.array(c['matrix']); rot=m[:3,:3];rot=rot/np.linalg.norm(rot,axis=0);t=m[:3,3];p=(V-t)@rot;f=1920*c['lens']/c['sensor_width'];return np.c_[960+f*p[:,0]/-p[:,2],540-f*p[:,1]/-p[:,2]]
def edges(M):
 e=set()
 for p in M['polygons']:
  for a,b in zip(p,p[1:]+p[:1]): e.add(tuple(sorted((a,b))))
 return np.array(sorted(e))
def directed(P,E,pts,axis,side):
 out=[]
 for pt in pts:
  axis=axis;target=pt[axis];a=P[E[:,0]];b=P[E[:,1]];valid=(np.minimum(a[:,axis],b[:,axis])<=target)&(np.maximum(a[:,axis],b[:,axis])>=target)&(abs(a[:,axis]-b[:,axis])>1e-9)
  aa=a[valid];bb=b[valid]
  if len(aa):
   val=aa[:,1-axis]+(target-aa[:,axis])*(bb[:,1-axis]-aa[:,1-axis])/(bb[:,axis]-aa[:,axis]);idx=np.argmin(val) if side=='min' else np.argmax(val);pred=[None,None];pred[axis]=target;pred[1-axis]=val[idx];out.append({'source':pt,'projection':pred,'residual':val[idx]-pt[1-axis]})
  else:out.append({'source':pt,'projection':None,'residual':None})
 return out
out=[]
for k,n in [('G','MATCH_G_Sofa_And_Bed'),('H','MATCH_H')]:
 c=D['cameras'][n];src=R.parent/'hospital_anchor_preparation_20261014/restored'/('hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png' if k=='G' else 'hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png');im=Image.open(src).convert('RGB');draw=ImageDraw.Draw(im)
 for br in A['branches']:
  if br['frame']!=k or br['object_id'] not in MAP:continue
  name=MAP[br['object_id']];m=D['meshes'][name];P=project(np.array(m['vertices']),c);E=edges(m);branch=br['contour_branch'];axis=0 if branch in ['upper','lower'] else 1;side='min' if branch in ['upper','left'] else 'max';res=directed(P,E,br['source_points'],axis,side);out.append({'id':br['branch_id'],'mesh':name,'mode':'projection boundary diagnostic, visibility not yet checked','results':res})
  for a,b in E:draw.line([tuple(P[a]),tuple(P[b])],fill=(60,200,255),width=1)
  for item in res:
   u,v=item['source'];draw.ellipse((u-3,v-3,u+3,v+3),fill=(255,190,0))
   if item['projection']:draw.line([tuple(item['source']),tuple(item['projection'])],fill=(255,50,90),width=2)
 im.save(R/f'{k}_D_wire_branch_diagnostic.png')
(R/'D_directed_branch_precheck.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
for x in out:
 v=[t['residual'] for t in x['results'] if t['residual'] is not None];print(x['id'],len(v),'mean',round(np.mean(v),2) if v else None,'max',round(max(abs(t) for t in v),2) if v else None)
