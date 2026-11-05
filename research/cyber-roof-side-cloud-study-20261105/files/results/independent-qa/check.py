import bpy,bmesh,math,json,hashlib,numpy as np
from pathlib import Path
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent; R=P.parent
src=R/'cyber-roof-cloud-r06-20261105/models/roof-r06b-experiment.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src))
def geo(o):
 o.data.calc_loop_triangles();return [o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices) for t in o.data.loop_triangles]
def bt(v,t):return BVHTree.FromPolygons(v,t,all_triangles=True)
v=[]
for y in (3.72,3.8):
 v.append((-11.6,y,6.25))
 for k in range(144):
  a=k*2*math.pi/144;rr=1+.17*math.sin(5*a)+.08*math.sin(9*a);v.append((-11.6+1.3*1.6*rr*math.cos(a),y,6.25+1.3*.65*rr*math.sin(a)))
f=[]
for k in range(144):
 i=1+k;j=1+(k+1)%144;f.extend([(0,i,j),(145,145+j,145+i),(i,145+i,145+j,j)])
me=bpy.data.meshes.new('independent_memory_only');me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.calc_loop_triangles();vv=[x.co.copy() for x in me.vertices];tt=[tuple(x.vertices) for x in me.loop_triangles];tree=bt(vv,tt)
names=['ROOF_MAIN closed shell','ROOF_MAIN rib 00','ROOF_MAIN rib 01','ROOF_MAIN rib 02','ROOF_MAIN side gold 0']
# Discover exact intersecting roof trim name rather than presume author naming.
roof=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith('ROOF_MAIN'):
  ov,ot=geo(o);pairs=tree.overlap(bt(ov,ot))
  if pairs:roof.append((o,ov,ot,pairs))
clouds=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('CLOUD_0')]
def winding(points,v,t):
 tri=np.asarray(v,dtype=np.float64)[np.asarray(t)]
 out=[]
 for p in points:
  a,b,c=(tri-np.asarray(p))[:,0],(tri-np.asarray(p))[:,1],(tri-np.asarray(p))[:,2]
  la=np.linalg.norm(a,axis=1);lb=np.linalg.norm(b,axis=1);lc=np.linalg.norm(c,axis=1)
  den=la*lb*lc+np.einsum('ij,ij->i',a,b)*lc+np.einsum('ij,ij->i',b,c)*la+np.einsum('ij,ij->i',c,a)*lb
  n=np.einsum('ij,ij->i',a,np.cross(b,c));out.append(float(np.arctan2(n,den).sum()/(2*math.pi)))
 return out
out={'input_sha256':original,'candidate_vertices':len(vv),'candidate_triangles':len(tt),'pairs':[]}
for o,ov,ot,pairs in roof:
 row={'object':o.name,'new_surface_pairs':len(pairs),'baseline_tubes':{}}
 for c in clouds:
  cv,ct=geo(c);row['baseline_tubes'][c.name]=len(bt(cv,ct).overlap(bt(ov,ot)))
 if o.name=='ROOF_MAIN closed shell':
  ids=sorted(set(i for _,j in pairs for i in ot[j]));points=[ov[i] for i in ids];w=winding(points,vv,tt)
  cp=[sum((vv[i] for i in t),vv[0]*0)/3 for t in tt];cw=winding(cp,ov,ot)
  row['fill_face_centroids_in_roof']={'count':len(cp),'inside_abs_gt_0p99':sum(abs(x)>.99 for x in cw),'winding':cw,'inside_samples':[{'triangle':i,'point':list(cp[i]),'winding':q,'nearest_roof_surface':bt(ov,ot).find_nearest(cp[i])[3]} for i,q in enumerate(cw) if abs(q)>.99]}
  row['containment']={'method':'solid angle winding on actual loop triangles; roof vertices of intersected triangles only, not full volume','roof_vertex_ids':ids,'winding':w,'inside_count_abs_gt_0p99':sum(abs(x)>.99 for x in w)}
 out['pairs'].append(row)
out['input_sha_unchanged']=sha(src)==original
(P/'check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
