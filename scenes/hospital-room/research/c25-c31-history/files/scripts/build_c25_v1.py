import bpy,numpy as np,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'v1';O.mkdir(exist_ok=True)
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
controls=np.array([[448,1078,-.008,.0085,.010],[452,1055,-.009,.010,.014],[458,1020,-.012,.0125,.018],[461,980,-.013,.0135,.019],[461,944,-.012,.012,.017],[457,920,-.010,.009,.012],[449,910,-.008,.006,.009],[441,906,-.006,.0028,.004],[447,903,-.004,.003,.0035],[458,905,-.003,.0035,.0035],[470,914,-.002,.004,.004]])
# Cubic Hermite interpolation through broad shape controls, no pixel optimizer.
def interp(t):
 i=min(len(controls)-2,int(t));a=t-i;p0=controls[max(0,i-1)];p1=controls[i];p2=controls[i+1];p3=controls[min(len(controls)-1,i+2)];return .5*((2*p1)+(-p0+p2)*a+(2*p0-5*p1+4*p2-p3)*a*a+(-p0+3*p1-3*p2+p3)*a*a*a)
rows=[interp(t) for t in np.linspace(0,len(controls)-1,180)];centers=np.array([lift(q[:2],q[2]) for q in rows]);VV=[];FF=[];K=40
for j,(q,c) in enumerate(zip(rows,centers)):
 tan=centers[min(j+1,len(centers)-1)]-centers[max(j-1,0)];tan/=np.linalg.norm(tan);width=CM[:3,0]-tan*(tan@CM[:3,0]);width/=np.linalg.norm(width);depth=np.cross(tan,width);depth/=np.linalg.norm(depth)
 for a in np.arange(K)*2*np.pi/K:VV.append(c+width*max(q[3],.001)*np.cos(a)+depth*max(q[4],.001)*np.sin(a))
for j in range(len(rows)-1):
 for i in range(K):a=j*K+i;b=j*K+(i+1)%K;FF.append([a,b,b+K,a+K])
FF.extend([list(range(K))[::-1],list(range((len(rows)-1)*K,len(rows)*K))])
ob=bpy.data.objects[L];bv=[list(v.co) for v in ob.data.vertices];bf=[list(f.vertices) for f in ob.data.polygons];base=len(bv);setmesh(ob,bv+np.array(VV).tolist(),bf+[[i+base for i in f] for f in FF]);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
rem=ob.modifiers.new('C25 side frame and upright union','REMESH');rem.mode='VOXEL';rem.voxel_size=.00065;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
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
json.dump({'status':'C25_V1_INTEGRATED_LIP_HYPOTHESIS_UNREVIEWED','source_model_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'intended_changed_meshes':[P,L],'shell_thickness':.010,'whole_panel_bow':.008,'sideframe_controls_Hxy_offset_width_depth':controls.tolist(),'sideframe_union_voxel_size':.00065,'cameras_materials_visibility_unchanged_in_material_model':True,'hidden_lower_support_endpoints':'Inherited conditional C23 construction; not measured','source_pose':'H/G/665 cross-time shared pose conditional','new_frames':'Semantic evidence only, not camera calibrated','boundary_semantics':'Outer leftreturn is now composite shell+sideframe, inner band transition is not claimed measured seam'},open(O/'build_manifest.json','w'),indent=2)
print('C25_BUILD_READY',O,flush=True)
