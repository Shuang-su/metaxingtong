import sys
sys.path.pop(0)
import pathlib,runpy,json,numpy as np
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-exterior-fit-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-source15-qa-20261104');ns=runpy.run_path(str(P/'fit.py'));G=ns['G'];A=ns['A'];t=next(x for x in json.loads((P/'trials.json').read_text())['trials'] if x['lens']==18);v=np.array(G['objects']['TERRACE_portal_00']['vertices']);door=np.array(G['objects']['DOOR_00_upper']['vertices'])[1::4];door=np.vstack([[-1.05,-6.16,.4],door,[1.05,-6.16,.4]]);lines={'L10':v[54:81],'L11':v[81:108],'L09':door};out=[]
for id,line in lines.items():
 uv,depth=ns['project'](line,t['parameters'],18)
 for pix in A[id]['pixels']:
  a,b=uv[:-1],uv[1:];d=b-a;par=np.clip(np.sum((np.array(pix)-a)*d,axis=1)/np.sum(d*d,axis=1),0,1);err=np.linalg.norm(np.array(pix)-(a+par[:,None]*d),axis=1);k=int(np.argmin(err));z=par[k];world=((1-z)*line[k]/depth[k]+z*line[k+1]/depth[k+1])/((1-z)/depth[k]+z/depth[k+1]);out.append({'id':id,'source_pixel':pix,'error_px':float(err[k]),'projected_pixel':(a[k]+z*d[k]).tolist(),'world_target':world.tolist()})
(Q/'trial18-correspondences.json').write_text(json.dumps({'camera':t,'points':out},indent=2));print([(i,np.mean([x['error_px'] for x in out if x['id']==i]),max(x['error_px'] for x in out if x['id']==i)) for i in lines])
