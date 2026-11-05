import bpy,numpy as np,json,hashlib,math
from pathlib import Path
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;R=P.parent;study=R/'cyber-roof-paired-shell-study-20261105';src=R/'cyber-roof-stage-20261105/models/roof-r05.blend';sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
objs={o.name:o for o in s.objects if o.type=='MESH'};old={n:np.array([list(o.matrix_world@v.co)for v in o.data.vertices])for n,o in objs.items()};new={n:v.copy()for n,v in old.items()};N=2145;shell='ROOF_MAIN closed shell'
# Direct delta in the single permitted parameter; both actual original vertices share it.
for k in range(N):
 u=2*(k%65)/64-1;t=2*(k//65)/32-1;dx=11.4*u*(.55-.74)*(1-abs(t));new[shell][[k,k+N],0]+=dx
base=json.load(open(study/'sources/previous-ring-baseline.json'));re=[]
for row in base['tube_checks']:
 n=row['object'];c0=np.array([r['centerline']for r in row['rings']]);c1=c0.copy();count=len(c0)
 for j in range(count):
  if ' rib 'in n:u=2*int(n.rsplit(' ',1)[1])/44-1;t=2*j/48-1
  elif n.endswith('gold ridge'):u=2*j/64-1;t=0
  else:u=-1 if old[n][:,0].mean()<0 else 1;t=2*j/48-1
  c1[j,0]+=11.4*u*(.55-.74)*(1-abs(t))
 def tang(c):
  ds=np.diff(c,axis=0);ds/=np.linalg.norm(ds,axis=1)[:,None];v=np.vstack([ds[0],ds[:-1]+ds[1:],ds[-1]]);return v/np.linalg.norm(v,axis=1)[:,None]
 a,b=tang(c0),tang(c1)
 for j,r in enumerate(row['rings']):
  ids=r['actual_vertex_ids'];q=old[n][ids]-c0[j];axis=np.cross(a[j],b[j]);sn=np.linalg.norm(axis);co=float(a[j]@b[j]);theta=math.atan2(sn,co)
  if sn<1e-12:
   assert co>0;rot=q.copy()
  else:
   ax=axis/sn;rot=q*math.cos(theta)+np.cross(ax,q)*math.sin(theta)+np.outer(q@ax,ax)*(1-math.cos(theta))
  new[n][ids]=rot+c1[j];re.append(float(abs(np.linalg.norm(q,axis=1)-np.linalg.norm(rot,axis=1)).max()))
tri={};tree={}
for n,o in objs.items():
 o.data.calc_loop_triangles();tri[n]=np.array([list(t.vertices)for t in o.data.loop_triangles],int)
 if n in [shell,'ROOF_MAIN rib 00','CLOUD_0 silhouette decorative proxy']:
  for state,vs in [('old',old[n]),('new',new[n])]:tree[state,n]=BVHTree.FromPolygons(vs.tolist(),tri[n].tolist(),all_triangles=True)
d0=old[shell][N:]-old[shell][:N];d1=new[shell][N:]-new[shell][:N];normal={}
for st,vs in [('old',old[shell]),('new',new[shell])]:
 top=tri[shell][np.max(tri[shell],axis=1)<N];tp=vs[top];cross=np.cross(tp[:,1]-tp[:,0],tp[:,2]-tp[:,0]);nv=np.zeros((N,3))
 for k in range(3):np.add.at(nv,top[:,k],cross)
 nv/=np.linalg.norm(nv,axis=1)[:,None]
 m=bpy.data.meshes.new('temp normals');m.from_pydata(vs[:N],[],[list(p.vertices)for p in objs[shell].data.polygons if max(p.vertices)<N]);m.update();bn=np.array([list(v.normal)for v in m.vertices]);bn/=np.linalg.norm(bn,axis=1)[:,None];bpy.data.meshes.remove(m)
 normal[st]={}
 for label,n in [('triangle_area_weighted',nv),('blender_polygon',bn)]:
  ang=np.degrees(np.arccos(np.clip(np.sum(-d1*n,axis=1)/np.linalg.norm(d1,axis=1),-1,1)));normal[st][label]={'angle_max':float(ang.max()),'projection_min':float(abs(np.sum(d1*n,axis=1)).min())}
main=[n for n in objs if n.startswith('ROOF_MAIN')]
# Independently repeat only reported local rib/cloud bidirectional whole-centroid evidence.
def winding(p,v,t):
 q=v[t]-p;a,b,c=q[:,0],q[:,1],q[:,2];la,lb,lc=np.linalg.norm(a,axis=1),np.linalg.norm(b,axis=1),np.linalg.norm(c,axis=1)
 den=la*lb*lc+(a*b).sum(1)*lc+(b*c).sum(1)*la+(c*a).sum(1)*lb
 return float(np.arctan2((a*np.cross(b,c)).sum(1),den).sum()/(2*np.pi))
local=[]
for source,target in [('ROOF_MAIN rib 00','CLOUD_0 silhouette decorative proxy'),('CLOUD_0 silhouette decorative proxy','ROOF_MAIN rib 00')]:
 row={'source':source,'target':target,'states':{}}
 for st,vs in [('old',old),('new',new)]:
  pts=vs[source][tri[source]].mean(1);lo=vs[target].min(0);hi=vs[target].max(0);inside=[]
  for i,p in enumerate(pts):
   if np.any(p<lo)or np.any(p>hi):continue
   w=winding(p,vs[target],tri[target]);d=tree[st,target].find_nearest(p)[3]
   if abs(w)>.5 and d>1e-6:inside.append({'tri':i,'winding':w,'distance':d})
  row['states'][st]={'total_centroids':len(pts),'inside':inside,'max_distance':max([a['distance']for a in inside],default=0),'surface_pairs':len(tree[st,source].overlap(tree[st,target]))}
 local.append(row)
res={'input_sha':sha,'vector_max_error':float(abs(d1-d0).max()),'ring_radius_max_error':max(re),'eaves':{n:float(abs(new[n]-old[n]).max())for n in ['ROOF_MAIN gold front eave','ROOF_MAIN gold back eave inferred']},'nonmain_max_displacement':max(float(abs(new[n]-old[n]).max())for n in objs if n not in main),'normal':normal,'local_containment':local,'input_unchanged':sha==hashlib.sha256(src.read_bytes()).hexdigest()}
(P/'check.json').write_text(json.dumps(res,indent=2))
# Re-evaluate all recorded points/envelopes using these independently generated arrays; output redirected only.
code=(study/'scripts/project_single_arrays.py').read_text().replace("P/'sources/annotations-v1.json'","study/'sources/annotations-v1.json'")
exec(code)
print('DONE',res['vector_max_error'],res['normal'])
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
projection=json.load(open(P/'results/single-a055-projections.json'));pixel_errors=[];depths=[]
for row in projection['rows']:
 for p in row['points']:
  xyz=p.get('world',p.get('world_centerline'));w=world_to_camera_view(s,cams['11'],Vector(xyz));pixel_errors.append(float(np.linalg.norm(np.array([w.x*1192,(1-w.y)*671])-p['projected'])));depths.append(w.z)
 for source,bands in row['lower_envelopes'].items():
  for b in bands:
   for p in b['three_samples']:
    w=world_to_camera_view(s,cams[source],Vector(p['world_edge_intersection']));pixel_errors.append(float(np.linalg.norm(np.array([w.x*1192,(1-w.y)*671])-[p['x'],p['y']])));depths.append(w.z)
metrics=[]
for n in main:
 q=new[n][tri[n]];p0=old[n][tri[n]];v=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]);v0=np.cross(p0[:,1]-p0[:,0],p0[:,2]-p0[:,0]);metrics.append({'object':n,'degenerate_area2_le1e12':int((np.linalg.norm(v,axis=1)<=1e-12).sum()),'signed_volume':float(np.sum(q[:,0]*np.cross(q[:,1],q[:,2]))/6),'normal_reversal_count':int((np.sum(v*v0,axis=1)<=0).sum())})
res['geometry_metrics']=metrics;res['independent_world_to_camera_point_witness_max_px']=max(pixel_errors);res['minimum_witness_camera_depth']=min(depths);res['projection_scope']='all recorded points and all envelope witnesses checked with Blender world_to_camera_view; whole envelope selection rerun with original projection script over independent arrays; no first hit/ray visibility'
res['shell_eave_paired_displacement']=float(abs((new[shell]-old[shell])[list(range(65))+list(range(N-65,N))+list(range(N,N+65))+list(range(2*N-65,2*N))]).max())
(P/'check.json').write_text(json.dumps(res,indent=2))
