import numpy as np
def orient2(a,b,c):return float(np.cross(b-a,c-a))
def ptri2(p,t,eps):
 s=np.array([orient2(t[i],t[(i+1)%3],p)for i in range(3)]);return np.all(s>=-eps)or np.all(s<=eps)
def segseg2(a,b,c,d,eps):
 q=np.array([orient2(a,b,c),orient2(a,b,d),orient2(c,d,a),orient2(c,d,b)])
 if q[0]*q[1]<-eps*eps and q[2]*q[3]<-eps*eps:return True
 for x,u,v,s in [(c,a,b,q[0]),(d,a,b,q[1]),(a,c,d,q[2]),(b,c,d,q[3])]:
  if abs(s)<=eps and np.all(x>=np.minimum(u,v)-eps)and np.all(x<=np.maximum(u,v)+eps):return True
 return False
def segtri(p,q,t,eps):
 e1=t[1]-t[0];e2=t[2]-t[0];direction=q-p;h=np.cross(direction,e2);det=np.dot(e1,h)
 if abs(det)<eps*eps:return False
 inv=1/det;s=p-t[0];u=inv*np.dot(s,h)
 if u<-eps or u>1+eps:return False
 qq=np.cross(s,e1);v=inv*np.dot(direction,qq);tt=inv*np.dot(e2,qq)
 return v>=-eps and u+v<=1+eps and tt>=-eps and tt<=1+eps
def tri_intersect(A,B,eps=1e-9):
 na=np.cross(A[1]-A[0],A[2]-A[0]);nb=np.cross(B[1]-B[0],B[2]-B[0]);la=np.linalg.norm(na);lb=np.linalg.norm(nb)
 if la<1e-20 or lb<1e-20:return False
 da=(B-A[0])@(na/la);db=(A-B[0])@(nb/lb)
 if (np.all(da>eps)or np.all(da<-eps)or np.all(db>eps)or np.all(db<-eps)):return False
 if np.max(np.abs(da))<=eps and np.max(np.abs(db))<=eps:
  ax=np.argmax(np.abs(na));AA=np.delete(A,ax,axis=1);BB=np.delete(B,ax,axis=1)
  return any(ptri2(x,BB,eps)for x in AA)or any(ptri2(x,AA,eps)for x in BB)or any(segseg2(AA[i],AA[(i+1)%3],BB[j],BB[(j+1)%3],eps)for i in range(3)for j in range(3))
 return any(segtri(A[i],A[(i+1)%3],B,eps)or segtri(B[i],B[(i+1)%3],A,eps)for i in range(3))
