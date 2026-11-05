import bpy,json,pathlib,numpy as np,hashlib
Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-butterfly-planar-qa-20261105');P=Q.parent/'butterfly-s-rail-planar-analysis-20261105';f=Q.parent/'butterfly-finite-stage-20261105/models/R04D_material.blend';before=hashlib.sha256(f.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();D=json.loads((P/'fixed-plane-diagnostic.json').read_text());out=[]
def M(name):
 c=bpy.data.objects[name];return np.array(c.calc_matrix_camera(dg,x=1192,y=671))@np.linalg.inv(np.array(c.matrix_world))
m02=M('SOURCE02_conditional_front')
def proj(m,p):
 a=m@np.r_[p,1];a=a[:3]/a[3];return np.array([(a[0]+1)*596,(1-a[1])*335.5])
for c in D['cases']:
 m=M(c['camera']);errs=[];pe=[];depth=[];rows=[]
 for seg in c['segments']:
  pts=[]
  for v in seg['samples']:
   u,y=v['source05_center_proxy']; nx=u/596-1;ny=1-y/335.5
   # Solve homogeneous projective equations with Y fixed, no ray helper reused.
   A=np.array([m[0]-nx*m[3],m[1]-ny*m[3],[0,1,0,-c['Y']]])
   p=np.linalg.solve(A[:,:3],-A[:,3]);errs.append(float(np.max(np.abs(p-v['world_center_proxy']))));xy=proj(m02,p);pe.append(float(np.max(np.abs(xy-v['source02_center_proxy']))));pts.append(xy.tolist());depth.append(float((m@np.r_[p,1])[3]))
  rows.append(pts)
 rr=[]
 for r in c['source02_diagnostic_rows']:
  hits=[]
  for pts in rows:
   for a,b in zip(pts[:-1],pts[1:]):
    if (a[1]-r['y02'])*(b[1]-r['y02'])<=0 and a[1]!=b[1]:hits.append(a[0]+(b[0]-a[0])*(r['y02']-a[1])/(b[1]-a[1])-r['target_center_proxy_x'])
  old=[z for i in r['intersections'] for z in i['signed_center_dx']];rr.append({'row':r['y02'],'residuals':hits,'old':old,'same_count':len(hits)==len(old),'max_difference':max([abs(a-b) for a,b in zip(hits,old)],default=0)})
 out.append({'side':c['side'],'camera':c['camera'],'plane':c['plane'],'sample_count':len(errs),'world_difference_max':max(errs),'pixel_difference_max':max(pe),'min_clip_w':min(depth),'rows':rr})
(Q/'check.json').write_text(json.dumps({'cases':out,'case_count':len(out),'model_sha':before,'model_unchanged':before==hashlib.sha256(f.read_bytes()).hexdigest()},indent=2));print('DONE',len(out),max(c['pixel_difference_max'] for c in out))
