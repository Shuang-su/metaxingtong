import bpy,json,hashlib,numpy as np
from pathlib import Path
P=Path('/workspace/scratch/fa58bfcf0425/seaside-chair-candidate-20261105');O=Path(__file__).resolve().parent;f=P/'models/material.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();R={'input_sha':sha(f),'script_sha':sha(P/'scripts/trial_chair_curve.py'),'result_sha':sha(P/'qa/chair-curve-trial.json'),'pairs':[]}
bpy.ops.wm.open_mainfile(filepath=str(f))
def winding(q,tri):
 v=tri[None,:,:,:]-q[:,None,None,:];a,b,c=v[:,:,0],v[:,:,1],v[:,:,2];la=np.linalg.norm(a,axis=-1);lb=np.linalg.norm(b,axis=-1);lc=np.linalg.norm(c,axis=-1);num=np.einsum('...i,...i->...',a,np.cross(b,c));den=la*lb*lc+np.einsum('...i,...i->...',a,b)*lc+np.einsum('...i,...i->...',b,c)*la+np.einsum('...i,...i->...',c,a)*lb;return np.sum(2*np.arctan2(num,den),axis=1)/(4*np.pi)
for idx,suffix in [('00',''),('11','.001')]:
 c=bpy.data.objects['C01 stripe '+idx];v=np.array([list(x.co) for x in c.data.vertices]);lo=v.min(0);hi=v.max(0);M=np.array(c.matrix_world);sample=np.array([[lo[0]+(hi[0]-lo[0])*u,lo[1]+(hi[1]-lo[1])*v,lo[2]+(hi[2]-lo[2])*t,1] for t in np.linspace(0,1,129) for u in np.linspace(0,1,5) for v in np.linspace(0,1,5)]);ts=np.repeat(np.linspace(0,1,129),25)
 for amp in [0,.97]:
  q=(sample@M.T)[:,:3];q[:,2]-=amp*np.interp(ts,np.linspace(0,1,33),np.linspace(0,1,33)*(1-np.linspace(0,1,33)))
  for name in ['C01 back rail'+suffix,'C01 cross leg B'+suffix,'C01 front bar']:
   w=bpy.data.objects[name];wv=np.array([list(x.co) for x in w.data.vertices]);mn=wv.min(0);mx=wv.max(0);inv=np.array(w.matrix_world.inverted());local=np.column_stack((q,np.ones(len(q))))@inv.T;inside=np.all((local[:,:3]>mn+1e-7)&(local[:,:3]<mx-1e-7),axis=1)
   # Verify the bounding box is the actual solid, not merely an AABB around arbitrary wood geometry.
   corners={tuple(x) for x in wv};expected={tuple([a,b,c]) for a in [mn[0],mx[0]] for b in [mn[1],mx[1]] for c in [mn[2],mx[2]]};w.data.calc_loop_triangles();W=np.array(w.matrix_world);world=(np.column_stack((wv,np.ones(len(wv))))@W.T)[:,:3];tri=world[np.array([list(t.vertices) for t in w.data.loop_triangles])];wn=winding(q,tri);depth=np.min(np.minimum(local[:,:3]-mn,mx-local[:,:3]),axis=1)
   R['pairs'].append({'cloth':c.name,'wood':name,'amp':amp,'box_vertices_exact':corners==expected and len(wv)==8,'faces':len(w.data.polygons),'triangles':len(tri),'samples':len(q),'obb_inside':int(inside.sum()),'t_range':[float(ts[inside].min()),float(ts[inside].max())],'max_sample_obb_depth':float(depth[inside].max()),'inside_samples_winding_minmax':[float(abs(wn[inside]).min()),float(abs(wn[inside]).max())],'winding_confirms_all_obb_interior':bool(np.all(abs(wn[inside])>.99999))})
R['input_unchanged']=sha(f)==R['input_sha'];(O/'check.json').write_text(json.dumps(R,indent=2));print('COMPLETE',[(p['cloth'],p['wood'],p['amp'],p['obb_inside']) for p in R['pairs']])
