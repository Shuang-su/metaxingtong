import bpy,bmesh,pathlib,json,math,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/butterfly-finite-stage-20261105');Q=pathlib.Path(__file__).resolve().parents[1]
f=P/'models/R04D_material.blend';sha=hashlib.sha256(f.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();ann=json.loads((Q/'independent-semantics/annotations-v1.json').read_text())
camnames=['SOURCE02_conditional_front','SOURCE05_conditional_close','SOURCE05_alternate_tilt_diagnostic'];cams={n:bpy.data.objects[n] for n in camnames};matrices={n:o.calc_matrix_camera(dg,x=1192,y=671,scale_x=1,scale_y=1)@o.matrix_world.inverted() for n,o in cams.items()}
names={'L':'CENTRAL_S_visible_1','R':'CENTRAL_S_visible_-1'};base={};C=Vector((0,-36,7));MAX_MOVE=.75;CUTOFF=.32
for side,n in names.items():
 o=bpy.data.objects[n];o.data.calc_loop_triangles();vs=[o.matrix_world@v.co for v in o.data.vertices];tris=[tuple(t.vertices) for t in o.data.loop_triangles];base[side]={'object':o,'v':vs,'tri':tris,'centers':[sum(vs[i:i+10],Vector())/10 for i in range(0,len(vs),10)]}
def project(n,pts):
 M=matrices[n];out=[]
 for v in pts:
  h=M@v.to_4d();out.append(((h.x/h.w+1)*596,(1-h.y/h.w)*335.5))
 return out
projection_error=max(abs(a-b) for n in camnames for v in base['L']['centers'] for a,b in zip(project(n,[v])[0],(world_to_camera_view(s,cams[n],v).x*1192,(1-world_to_camera_view(s,cams[n],v).y)*671)))
def deformation(v,ring,nrings,depth,lift):
 q=C+(v-C)*((36+v.y+depth)/(36+v.y));t=ring/(nrings-1);u=t/CUTOFF;w=(1-u)**2*(1+2*u) if u<1 else 0;q.z+=lift*w;return q

def candidate(depth,lift,vertices=False):
 out={};mx=0
 for side,b in base.items():
  nr=len(b['centers']);pts=b['v'] if vertices else b['centers'];v=[]
  for i,p in enumerate(pts):
   q=deformation(p,i//10 if vertices else i,nr,depth,lift);mx=max(mx,(q-p).length);v.append(q)
  out[side]=v
 return out,mx

def closest(poly,xy,closed=False):
 best=None
 for i in range(len(poly) if closed else len(poly)-1):
  a=Vector(poly[i]);b=Vector(poly[(i+1)%len(poly)]);p=Vector(xy);d=b-a;t=max(0,min(1,(p-a).dot(d)/max(1e-20,d.dot(d))));q=a+t*d;dist=(q-p).length
  if best is None or dist<best['distance_px']:best={'distance_px':dist,'dx_px':q.x-p.x,'dy_px':q.y-p.y,'closest_xy':list(q),'segment':i,'fraction':t}
 return best

def assess(depth,lift,cam):
 cs,_=candidate(depth,lift);results={}
 for a in ann['source05' if '05' in cam else 'source02']['points']:
  side='L' if '_L_' in a['id'] else 'R';pts=project(cam,cs[side]);r=closest(pts,a['xy']);r['subjective_error_px']=a['subjective_error_px'];r['semantic']=a['semantic'];r['comparison']='model section-center polyline vs appearance-strip proxy; not physical axis truth'
  if '_cap' in a['id']:
   vs,_=candidate(depth,lift,True);cap=project(cam,vs[side][:10]);r=closest(cap,a['xy'],True);r['subjective_error_px']=a['subjective_error_px'];r['semantic']=a['semantic'];r['comparison']='actual projected first-ring flat cap rim vs visible rounded cap boundary; not centerline endpoint, shape mismatch retained';r['projected_flat_cap_rim']=cap
  results[a['id']]=r
 return results

train=['S05_L_y150','S05_L_y225'];grid=[];best={n:None for n in camnames[1:]};rejected=0
for di in range(31):
 d=-.75+.05*di
 for li in range(33):
  z=-.4+.025*li
  _,move=candidate(d,z,True)
  if move>MAX_MOVE+1e-9:rejected+=1;continue
  row={'depth_along02_ray':d,'upper_lift':z,'max_actual_vertex_displacement':move}
  for cam in camnames[1:]:
   r=assess(d,z,cam);loss=sum(r[k]['distance_px']**2 for k in train)/len(train);row[cam+'_train_rmse']=math.sqrt(loss)
   if best[cam] is None or loss<best[cam]['train_mse']:
    best[cam]={'depth':d,'lift':z,'train_mse':loss,'max_actual_vertex_displacement':move}
  grid.append(row)
# Static targets: all other existing 115 meshes; no hypothetical support added.
static=[]
for o in s.objects:
 if o.type=='MESH' and o.name not in names.values():
  o.data.calc_loop_triangles();vs=[o.matrix_world@v.co for v in o.data.vertices];ts=[tuple(t.vertices) for t in o.data.loop_triangles];static.append((o.name,BVHTree.FromPolygons(vs,ts,all_triangles=True)))
def relations(depth,lift):
 vs,move=candidate(depth,lift,True);out={}
 for side,b in base.items():
  bv=BVHTree.FromPolygons(vs[side],b['tri'],all_triangles=True);overlap={}
  for name,other in static:
   pairs=bv.overlap(other)
   if pairs:overlap[name]=len(pairs)
  caps=[]
  for capi,label in [(0,'upper'),(len(b['centers'])-1,'lower')]:
   c=sum(vs[side][capi*10:capi*10+10],Vector())/10;nearest=[]
   for name,other in static:
    if not name.startswith('CENTRAL_'):continue
    pt,n,idx,dist=other.find_nearest(c)
    if pt is not None:nearest.append({'target':name,'center_to_surface_distance':dist})
   caps.append({'end':label,'center_world':list(c),'nearest_static_central':min(nearest,key=lambda x:x['center_to_surface_distance'])})
  mesh=bpy.data.meshes.new('temporary_diagnostic_mesh');mesh.from_pydata(vs[side],[],b['tri']);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);vol=bm.calc_volume(signed=True);deg=sum(f.calc_area()<1e-12 for f in bm.faces);bm.free();bpy.data.meshes.remove(mesh)
  out[side]={'surface_overlap_targets_triangle_pair_counts':overlap,'end_center_distances_not_true_min_surface_gap':caps,'signed_volume':vol,'degenerate_triangles':deg}
 return out
cases={'baseline':{'depth':0.,'lift':0.},'best_original05_camera':best[camnames[1]],'best_alternate05_camera':best[camnames[2]]}
for name,a in cases.items():
 d=a['depth'];z=a['lift'];a['all_fixed_camera_diagnostics']={cam:assess(d,z,cam) for cam in camnames};a['relations']=relations(d,z);cs,mx=candidate(d,z);a['world_centers']={side:[list(p) for p in pts] for side,pts in cs.items()};a['center_projections']={cam:{side:project(cam,pts) for side,pts in cs.items()} for cam in camnames};a['max_actual_vertex_displacement']=candidate(d,z,True)[1]
assert hashlib.sha256(f.read_bytes()).hexdigest()==sha
out={'status':'MEMORY_ONLY_TWO_PARAMETER_SENSITIVITY_DIAGNOSTIC_NOT_MODEL_REVISION','frozen_model':str(f),'sha256_before_after':sha,'all_existing_cameras_fixed':True,'other_115_meshes_untouched':True,'same_deformation_shared_by_two_existing_S_objects':'conditional bilateral model hypothesis, not proven exact physical symmetry','geometry_transform':'C02+(p-C02)*(36+p.y+depth)/(36+p.y), then z += lift*smoothstep_weight with support first 32% of ring order. Depth preserves camera02 projection by construction; not independent validation.','parameter_bounds':{'depth':[-.75,.75],'upper_lift':[-.4,.4],'max_actual_vertex_displacement':MAX_MOVE,'units':'unmeasured working units'},'training_points':train,'nonfit_diagnostic_points':'source05 y275 and right-side points; source02 middle segments; cap rims separate. All points known beforehand, NOT blind holdout or statistical generalization.','top_bottom_null_policy':'02 caps and both source lower ends remain null. No 02 speculative cap coordinate used. No connection behind performer inferred.','grid_valid_count':len(grid),'grid_rejected_move_bound':rejected,'projection_matrix_vs_blender_camera_max_error_px':projection_error,'best_cases':cases,'grid':grid,'unchanged_primary_artifacts':True,'no_blend_glb_or_render_saved':True}
(Q/'two-parameter-diagnostic.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'best':best,'grid_valid':len(grid),'rejected':rejected,'projection_error':projection_error},indent=2))
