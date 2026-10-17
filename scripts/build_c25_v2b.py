import bpy,numpy as np,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'v2b';O.mkdir(exist_ok=True)
B=R/'inputs/hospital_C23_source_shaped_supports_CONDITIONAL.blend';bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene
lock=json.load(open(R/'dependencies/smooth_geometry_locked.json'));P='Chair • narrow curved wraparound back';L='Chair • slim back support';RR=L+'.001'
normal=np.array(lock['normal']);normal/=np.linalg.norm(normal);old=np.array(lock['panel']['mid_world']);center=old.mean(0);d=normal@center
cam=bpy.data.objects['C10_H_shared_sofa_height_CONDITIONAL'];CM=np.array(cam.matrix_world);CP=np.array(cam.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=1920,y=1080));clip=CP@np.linalg.inv(CM);ip=np.linalg.inv(CP)
def project(v):
 h=np.c_[np.asarray(v),np.ones(len(v))]@clip.T;h=h[:,:3]/h[:,3:];return np.c_[960*(h[:,0]+1),540*(1-h[:,1])]
def lift(xy,off=0):
 h=ip@np.array([xy[0]/960-1,1-xy[1]/540,-1,1]);ray=CM[:3,:3]@(h[:3]/h[3]);o=CM[:3,3];return o+ray*((d+off-normal@o)/(normal@ray))
def setmesh(ob,V,F):
 me=bpy.data.meshes.new(ob.name+' C25 structural volume');me.from_pydata(np.asarray(V).tolist(),[],F);me.update();mats=list(ob.data.materials);ob.data=me
 for m in mats:me.materials.append(m)
 for p in me.polygons:p.use_smooth=True
# Curved volume, rebuilt caps and side wall. Retain measured top/right/lower silhouette prior;
# replace explicitly unobserved left closure with an inner shell edge beneath side frame.
N=360;u=np.arange(N)/30;uv=np.array(lock['panel']['mid_H'])[::2].copy();assert len(uv)==N
for i,t in enumerate(u):
 if t>9.5:
  a=(t-9.5)/2.5;p0=np.array(lock['panel']['mid_H'])[570];p1=np.array([463.,1049.]);p2=np.array([472.,920.]);p3=np.array(lock['panel']['mid_H'])[0];uv[i]=(1-a)**3*p0+3*(1-a)**2*a*p1+3*(1-a)*a*a*p2+a**3*p3
# Close the visible backing gap behind the thin curled upper ribbon.
for i,t in enumerate(u):
 if 11.5<t<12:uv[i,0]-=14*np.sin(np.pi*(t-11.5)/.5)**2
W=np.array([lift(p) for p in uv]);C=W.mean(0)
# Rounded thickness transitions. Mild whole-panel bow changes volume, not camera alignment.
V=[];F=[];sem=[]
profiles=[tuple(q) for q in lock['profile_inset_depth']]
for inset,dep in profiles:
 for i,p in enumerate(W):
  q=p+(C-p)/np.linalg.norm(C-p)*inset
  V.append(q+normal*dep);sem.append(float(u[i]))
for j in range(len(profiles)-1):
 for i in range(N):a=j*N+i;b=j*N+(i+1)%N;F.append([a,b,b+N,a+N])
# Disk caps, interior curvature bows toward camera (negative fixed normal).
for side,j in [(-1,0),(1,len(profiles)-1)]:
 prev=list(range(j*N,(j+1)*N))
 for lev in range(1,21):
  r=1-lev/21;cur=[]
  for i,p in enumerate(W):
   q=C+(p-C)*r;bow=-.008*(1-r*r)
   cur.append(len(V));V.append(q+normal*(side*.005+bow));sem.append(None)
  for i in range(N):
   face=[prev[i],prev[(i+1)%N],cur[(i+1)%N],cur[i]]
   F.append(face[::-1] if side==-1 else face)
  prev=cur
 ci=len(V);V.append(C+normal*(side*.005-.008));sem.append(None)
 for i in range(N):F.append([prev[i],prev[(i+1)%N],ci][::-1] if side==-1 else [prev[i],prev[(i+1)%N],ci])
setmesh(bpy.data.objects[P],V,F)
# Apply consistent normals to closed rebuild.
bpy.context.view_layer.objects.active=bpy.data.objects[P];bpy.ops.object.select_all(action='DESELECT');bpy.data.objects[P].select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
me=bpy.data.objects[P].data;me.calc_loop_triangles();vol=sum(np.dot(np.array(me.vertices[t.vertices[0]].co),np.cross(np.array(me.vertices[t.vertices[1]].co),np.array(me.vertices[t.vertices[2]].co))) for t in me.loop_triangles)/6
if vol<0:
 for f in me.polygons:f.flip()
 me.update()
json.dump({'object':P,'parameter_u_per_vertex':sem,'original_boundary_mapping':'360 samples, parameter=i/30, original C21 top/right/lower retained; left closure rebuilt as inner edge','groups':{'top':[0,3],'right_shoulder':[3.1,6],'lower':[6.5,9.5],'left_inner_under_frame':[9.5,12]}},open(O/'panel_vertex_semantics.json','w'),indent=2)
# Side-frame hypothesis: upper upright broadens into a convex oval band and curls into a narrow lip.
# Lower C23 support is retained; same-mesh voxel union closes only intended transition.
# Convex ribbon volume hypothesis, replacing the oval sweep and its terminal cap.
# One bowed cross-section, curved thin top edge, broad middle and narrow lower taper.
# Same H-initialized 3D volume is used unchanged for all cameras.
U=48;T=112;VV=[];FF=[];ribbon_parameters={'top_xy_outer':[440,906],'top_inner_xy':[468,920],'bottom_y':1048,'bottom_outer_x':432,'top_width_px':28,'middle_width_gain_px':22,'bottom_width_gain_px':5,'front_bow_depth':.023,'wall_depth':.006}
for side in [0,1]:
 for j in range(T+1):
  t=j/T;z=np.clip((t-.10)/.70,0,1);smooth=z*z*(3-2*z);outer=440-8*smooth;width=28+22*np.sin(np.pi*t)**.8+5*t
  for i in range(U+1):
   u=i/U;x=outer+width*u;y=(1-t)*(906+14*u**1.6)+t*1048
   bow=(.011+.012*np.sin(np.pi*t))*np.sin(np.pi*u)**.85;offset=-.004-bow+side*.006
   VV.append(lift([x,y],offset))
Q=(U+1)*(T+1)
for side in [0,1]:
 for j in range(T):
  for i in range(U):
   q=side*Q+j*(U+1)+i;f=[q,q+1,q+U+2,q+U+1];FF.append(f[::-1] if side==0 else f)
# Boundary closes front/back; no loose lower or upper caps.
bound=list(range(U+1))+[j*(U+1)+U for j in range(1,T+1)]+[T*(U+1)+i for i in range(U-1,-1,-1)]+[j*(U+1) for j in range(T-1,0,-1)]
for i,a in enumerate(bound):
 b=bound[(i+1)%len(bound)];FF.append([a,b,b+Q,a+Q])
controls=[]
ob=bpy.data.objects[L];bv=[list(v.co) for v in ob.data.vertices];bf=[list(f.vertices) for f in ob.data.polygons];base=len(bv);setmesh(ob,bv+np.array(VV).tolist(),bf+[[i+base for i in f] for f in FF]);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
rem=ob.modifiers.new('C25 side frame and upright union','REMESH');rem.mode='VOXEL';rem.voxel_size=.00065;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
# Remove voxel remnants, preserving the main surface without smoothing.
import bmesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
me=ob.data;E=np.array([list(e.vertices) for e in me.edges]);graph=coo_matrix((np.ones(len(E)),(E[:,0],E[:,1])),shape=(len(me.vertices),len(me.vertices)));nc,labels=connected_components(graph,directed=False);counts=np.bincount(labels);main=int(np.argmax(counts));drop=set(np.where(labels!=main)[0].tolist());bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in drop],context='VERTS');bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,dist=1e-8,edges=list(bm.edges));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();json.dump({'original_components':int(nc),'component_vertex_counts':counts.tolist(),'discarded_vertices':len(drop),'scope':'No smoothing; remove only non-main voxel debris and degenerate elements'},open(O/'numerical_cleanup_manifest.json','w'),indent=2)
# Upper right junction widened toward source inner silhouette and tapered to original shaft.
ob=bpy.data.objects[RR];v=np.array([list(q.co) for q in ob.data.vertices]);uvR=project(v);left=CM[:3,0]
for i,co in enumerate(v):
 x,y=uvR[i];a=np.clip((1023-y)/35,0,1);side=np.clip((848-x)/21,0,1)
 ob.data.vertices[i].co=co
for ob in [bpy.data.objects[P],bpy.data.objects[L],bpy.data.objects[RR]]:
 for f in ob.data.polygons:f.use_smooth=True
 ob['C25_status']='Structural hypothesis; no source acceptance'
sc.camera=cam;bpy.ops.wm.save_as_mainfile(filepath=str(O/'hospital_C25_structural_volume_CONDITIONAL.blend'))
# White model: same complete geometry and scene, only material slots replaced.
white=bpy.data.materials.new('C25 neutral white geometry');white.diffuse_color=(.72,.72,.72,1);white.use_nodes=True;bs=white.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.72,.72,.72,1);bs.inputs['Roughness'].default_value=.68
for ob in bpy.data.objects:
 if ob.type=='MESH':
  ob.data.materials.clear();ob.data.materials.append(white)
  for f in ob.data.polygons:f.material_index=0
bpy.ops.wm.save_as_mainfile(filepath=str(O/'hospital_C25_white_geometry_CONDITIONAL.blend'))
json.dump({'status':'C25_V2B_RIBBON_WITH_BACKING_CONTINUITY_UNREVIEWED','source_model_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'intended_changed_meshes':[P,L],'shell_thickness':.010,'whole_panel_bow':.008,'ribbon_parameters':ribbon_parameters,'sideframe_union_voxel_size':.00065,'cameras_materials_visibility_unchanged_in_material_model':True,'hidden_lower_support_endpoints':'Inherited conditional C23 construction; not measured','source_pose':'H/G/665 cross-time shared pose conditional','new_frames':'Semantic evidence only, not camera calibrated','boundary_semantics':'Outer leftreturn is now composite shell+sideframe, inner band transition is not claimed measured seam'},open(O/'build_manifest.json','w'),indent=2)
print('C25_BUILD_READY',O,flush=True)
