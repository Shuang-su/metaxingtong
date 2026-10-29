from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parents[2];P=R/'c29';j=json.load(open(R/'c29_diagnosis/c28_curtain_mesh_readonly.json'));v=np.array(j['verts_local']);a=v[:225,:2];b=v[14625:14625+225,:2];params=json.load(open(P/'profile_candidates.json'))
def crossings(A,B,same=False):
 p=A[:-1,None,:];r=(A[1:]-A[:-1])[:,None,:];q=B[None,:-1,:];s=(B[1:]-B[:-1])[None,:,:];cr=lambda x,y:x[...,0]*y[...,1]-x[...,1]*y[...,0];den=cr(r,s);good=np.abs(den)>1e-12;t=np.divide(cr(q-p,s),den,out=np.zeros_like(den),where=good);u=np.divide(cr(q-p,r),den,out=np.zeros_like(den),where=good);hit=good&(t>1e-7)&(t<1-1e-7)&(u>1e-7)&(u<1-1e-7)
 if same:hit&=np.abs(np.arange(len(A)-1)[:,None]-np.arange(len(B)-1)[None,:])>1
 return np.argwhere(hit).tolist()
def rebuild(a,b,delta):
 aa=a.copy();aa[:,0]+=delta;old_t=np.gradient(a,axis=0);new_t=np.gradient(aa,axis=0);theta=np.arctan2(new_t[:,1],new_t[:,0])-np.arctan2(old_t[:,1],old_t[:,0]);d=b-a;c=np.cos(theta);s=np.sin(theta);dr=np.c_[c*d[:,0]-s*d[:,1],s*d[:,0]+c*d[:,1]];bb=aa+dr;bb[:29]=b[:29];bb[196:]=b[196:];return aa,bb
out={'baseline':{'front_back_crossings':crossings(a,b),'front_self':crossings(a,a,True),'back_self':crossings(b,b,True)},'variants':{}}
for tag,p in params.items():
 aa,bb=rebuild(a,b,np.array(p['local_x_delta']));bad=b.copy();bad[:,0]+=p['local_x_delta'];out['variants'][tag]={'old_translation_shell_front_back_crossings':crossings(aa,bad),'reoriented_shell_front_back_crossings':crossings(aa,bb),'front_self':crossings(aa,aa,True),'back_self':crossings(bb,bb,True),'paired_thickness_length_max_error':float(np.max(np.abs(np.linalg.norm(bb-aa,axis=1)-np.linalg.norm(b-a,axis=1)))),'front_new_local_xy':aa.tolist(),'back_new_local_xy':bb.tolist()}
(P/'shell_profile_verification.json').write_text(json.dumps(out,indent=2));print({k:{q:(len(w) if isinstance(w,list) else w) for q,w in x.items() if 'new_local' not in q} for k,x in out['variants'].items()})
