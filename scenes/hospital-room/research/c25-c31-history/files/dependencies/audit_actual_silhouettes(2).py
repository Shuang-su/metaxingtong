import bpy,numpy as np,json,hashlib,collections,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from datetime import datetime,timezone
O=Path(__file__).resolve().parent;R=O.parent;W=R.parent
cfg=json.load(open(O/'config.json'));assert cfg['ready'];C=W/cfg['candidate'];L=W/cfg['fixed_branch_metadata'];A=W/'hospital_furniture_joint_C14_20261015/source_furniture_review/furniture_source_branches.json'
paths=[C,L,A,W/cfg['protocol']];hashes={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
assert hashlib.sha256(C.read_bytes()).hexdigest()==cfg['candidate_sha256']
lock=json.load(open(L));ann=json.load(open(A));bpy.ops.wm.open_mainfile(filepath=str(C));s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
P='Chair • narrow curved wraparound back';sup=['Chair • slim back support','Chair • slim back support.001'];MD={}; trees={}; names=[]; tids=[];tv=[];tf=[]
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg);me.calc_loop_triangles();local=np.array([list(q.co) for q in me.vertices],float);matrix=np.array(ev.matrix_world,float);v=local@matrix[:3,:3].T+matrix[:3,3];f=np.array([list(q.vertices) for q in me.loop_triangles],int);MD[ob.name]={'V':v,'F':f};trees[ob.name]=BVHTree.FromPolygons(v.tolist(),f.tolist(),all_triangles=True);ev.to_mesh_clear()
 if not ob.hide_render and ob.visible_camera and all(not col.hide_render for col in ob.users_collection):
  names.append(ob.name);tids.extend([len(names)-1]*len(f));tf.extend((f+len(tv)).tolist());tv.extend(v.tolist())
FULL=BVHTree.FromPolygons(tv,tf,all_triangles=True);cams={};
for k in ['H','G','665']:
 ob=bpy.data.objects['C14_N642_fixed_windows_CONDITIONAL' if k=='N642' else 'C10_'+k+'_shared_sofa_height_CONDITIONAL'];mat=np.array(ob.matrix_world);proj=np.array(ob.calc_matrix_camera(dg,x=1920,y=1080,scale_x=s.render.pixel_aspect_x,scale_y=s.render.pixel_aspect_y));cams[k]={'obj':ob,'matrix':mat,'P':proj,'clip':proj@np.linalg.inv(mat),'invP':np.linalg.inv(proj)}
def project(k,v):
 v=np.asarray(v);h=np.c_[v,np.ones(len(v))]@cams[k]['clip'].T;h=h[:,:3]/h[:,3:];return np.c_[960*(h[:,0]+1),540*(1-h[:,1])]
def ray(k,p,target=None):
 c=cams[k];h=c['invP']@np.array([p[0]/960-1,1-p[1]/540,-1,1]);v=h[:3]/h[3];di=Vector(c['matrix'][:3,:3]@v).normalized();origin=Vector(c['matrix'][:3,3]);pt,no,ix,dist=(trees[target] if target else FULL).ray_cast(origin,di,100)
 return {'object':None if ix is None else target if target else names[tids[ix]],'distance':None if dist is None else float(dist),'xyz':None if pt is None else list(pt)}
def nearest(p,segs):
 if not len(segs):return None
 a=segs[:,0];v=segs[:,1]-a;t=np.clip(np.sum((np.array(p)-a)*v,axis=1)/np.maximum(np.sum(v*v,axis=1),1e-24),0,1);q=a+t[:,None]*v;dist=np.linalg.norm(q-p,axis=1);i=int(np.argmin(dist));return float(dist[i]),q[i],i
# Verify fixed ring-major vertex IDs directly against evaluated local mesh, then
# classify silhouette edges by the original H-only spline-parameter intervals.
pl=lock['panel'];N=len(pl['parameter_u']);u=np.array(pl['parameter_u']);normal=np.array(lock['normal']);normal/=np.linalg.norm(normal)
assert len(MD[P]['V'])==len(pl['vertices'])==N*len(lock['profile_inset_depth'])
ob=bpy.data.objects[P]; ev=ob.evaluated_get(dg);me=ev.to_mesh();actual_local=np.array([list(v.co) for v in me.vertices]);ev.to_mesh_clear()
assert np.array_equal(actual_local,np.array(pl['vertices'],np.float32).astype(float)), 'Fixed vertex index mapping not independently verified'
assert np.array_equal(np.array(ob.matrix_world),np.eye(4)), 'Expected identity panel transform for parameter mapping'
def label_edge(edge):
 us=u[np.array(edge)%N];du=(us[1]-us[0]+6)%12-6;mid=(us[0]+du/2)%12
 if 0<=mid<=3:return 'top',float(mid)
 if 3.1<=mid<=6:return 'right_shoulder',float(mid)
 if 6.5<=mid<=9.5:return 'lower',float(mid)
 return 'transition_or_unobserved_closure',float(mid)
CACHE={};summary={}
def silhouette(k,target):
 key=(k,target)
 if key in CACHE:return CACHE[key]
 v,f=MD[target]['V'],MD[target]['F'];tri=v[f];norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);facing=np.einsum('ij,ij->i',norm,cams[k]['matrix'][:3,3]-tri.mean(1));ed={}
 for fi,t in enumerate(f):
  for a,b in zip(t,np.roll(t,-1)):ed.setdefault(tuple(sorted((int(a),int(b)))),[]).append(fi)
 uv=project(k,v);rows=[];sc=0
 for edge,adj in ed.items():
  if len(adj)!=2 or facing[adj[0]]*facing[adj[1]]>=0:continue
  e=np.array(edge);sg=uv[e];d=sg[1]-sg[0];length=np.linalg.norm(d)
  if length<1e-7:continue
  sc+=1;nn=np.array([-d[1],d[0]])/length;lab,wi=label_edge(edge) if target==P else ('support_side_unspecified',None)
  count=max(1,int(np.ceil(length/.25)))
  for j in range(count):
   a=sg[0]+j/count*d;b=sg[0]+(j+1)/count*d;p=(a+b)/2
   if not(0<=p[0]<=1919 and 0<=p[1]<=1079):continue
   hm=ray(k,p-.05*nn,target);hp=ray(k,p+.05*nn,target)
   if (hm['object']==target)==(hp['object']==target):continue
   ins=nn if hp['object']==target else -nn
   inside=ray(k,p+.10*ins);outside=ray(k,p-.10*ins);visible=inside['object']==target and outside['object']!=target
   rows.append({'segment':[a.tolist(),b.tolist()],'mesh_edge_vertex_ids':list(edge),'construction_branch':lab,'fixed_spline_parameter_midpoint':wi,'inside_direction':ins.tolist(),'fullscene_visible':bool(visible),'inside_firsthit':inside['object'],'outside_firsthit':outside['object']})
 summary[k+'::'+target]={'candidate_silhouette_edges':sc,'self_boundary_native_subsegments':len(rows),'visible_native_subsegments':sum(r['fullscene_visible'] for r in rows),'branch_counts':dict(collections.Counter(r['construction_branch'] for r in rows)),'occluding_firsthit_counts':dict(collections.Counter(r['inside_firsthit'] for r in rows if not r['fullscene_visible']))}
 CACHE[key]=rows;print('SILHOUETTE',k,target,summary[k+'::'+target],flush=True);return rows
R={'status':'C22_FIXED_PANEL_REAR_POSTS_SOURCE_UNACCEPTED','audit_utc':datetime.now(timezone.utc).isoformat(),'input_hashes':hashes,'native_resolution':[1920,1080],'method':'Actual evaluated triangulated mesh view-facing adjacency silhouette verified by target-only and full-scene first-hit rays. No convex hull. Correct physical branch labels from verified ring-major actual mesh vertex spline parameters; fixed H-defined intervals; transition/closure excluded. Primary projection uses world64 from evaluated local32 plus matrix32; Blender BVH ray tests use runtime float32 math and finite inside/outside probes. Native subsegments <=0.25px plus closest-foot probes. All49 source records retained.','roles':{'G':'TRAINING_FROM_PRIOR_WORK_NOT_C21_SELECTION; not a new holdout','H':'SOLE_C21_SHAPE_FIT_TRAINING','665':'PRIOR_TRAINING_REGRESSION_NOT_USED_TO_SELECT_C21; fragment visibility and person cuts retained'},'branches':[],'camera_projection':{k:{'matrix':c['matrix'].tolist(),'projection':c['P'].tolist(),'lens':c['obj'].data.lens,'sensor_fit':c['obj'].data.sensor_fit,'sensor_width':c['obj'].data.sensor_width,'shift':[c['obj'].data.shift_x,c['obj'].data.shift_y]} for k,c in cams.items()}}
allowed={'H_C_TOP','H_C_R_SHOULDER','H_C_LOWER','G_C_TOP','G_C_R_SHOULDER','N665_C_TOP_SLIVER','N665_C_LOWER_SLIVER'}
branches=[b for b in ann['branches'] if b['id'] in allowed]
assert sum(len(b['points_xy']) for b in branches)==49

for b in branches:
 k='665' if b['view']=='N665' else b['view'];bid=b['id'];kind='top' if 'TOP' in bid else 'right_shoulder' if 'SHOULDER' in bid else 'lower' if 'LOWER' in bid else None;target=P if kind else sup[1] if '_R_SUPPORT' in bid else sup[0]
 rows=silhouette(k,target); selected=[r for r in rows if kind is None or r['construction_branch']==kind];segs=np.array([r['segment'] for r in selected]);valid=[i for i,r in enumerate(selected) if r['fullscene_visible']];vsegs=np.array([selected[i]['segment'] for i in valid]);points=[]
 for p in b['points_xy']:
  a=nearest(p,segs);z=nearest(p,vsegs);pr={'source_xy':p,'source_firsthit':ray(k,p),'source_target_only_hit':ray(k,p,target)}
  for field,nr,ixs in [('nearest_self_correct_branch',a,None),('nearest_visible_correct_branch',z,valid)]:
   if nr is None:pr[field]=None;continue
   ds,q,i=nr;i=i if ixs is None else ixs[i];rr=selected[i];nn=np.array(rr['inside_direction']);probes=[{'offset_px':off,'inside':ray(k,q+off*nn),'outside':ray(k,q-off*nn)} for off in [.03,.10,.25,.5,1.]]
   pr[field]={'distance_px':ds,'xy':q.tolist(),'segment_index':i,'construction_branch':rr['construction_branch'],'fullscene_visible_segment':rr['fullscene_visible'],'exact_ray':ray(k,q),'normal_probes':probes,'foot_visible_at_0p10':probes[1]['inside']['object']==target and probes[1]['outside']['object']!=target}
  points.append(pr)
 dd=[p['nearest_visible_correct_branch']['distance_px'] for p in points if p['nearest_visible_correct_branch']];ss=[p['nearest_self_correct_branch']['distance_px'] for p in points if p['nearest_self_correct_branch']];role=R['roles'][k];tol=b['tolerance_px'];row={'id':bid,'role':role,'target':target,'physical_branch':kind or 'identity_uncertain_support_silhouette','source_record_count':len(b['points_xy']),'retained_source_point_count':len(points),'tolerance_px':tol,'source_annotation':b,'self_segment_count':len(selected),'visible_segment_count':len(valid),'metrics':{'self_rms_px':float(np.sqrt(np.mean(np.square(ss)))) if ss else None,'self_max_px':max(ss) if ss else None,'visible_rms_px':float(np.sqrt(np.mean(np.square(dd)))) if dd else None,'visible_max_px':max(dd) if dd else None,'source_points_within_tolerance':sum(d<=tol for d in dd),'all_source_points_visible_distance_within_tolerance':len(dd)==len(points) and max(dd)<=tol,'nearest_foot_visibility_verified_count':sum(bool(p['nearest_visible_correct_branch'] and p['nearest_visible_correct_branch']['foot_visible_at_0p10']) for p in points)},'points':points,'actual_segments':selected}
 # Dense interpolation is secondary diagnostic, never extra evidence points.
 src=np.array(b['points_xy'],float);arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(src,axis=0),axis=1))];t=np.linspace(0,arc[-1],int(np.ceil(arc[-1]*2))+1);dense=np.c_[np.interp(t,arc,src[:,0]),np.interp(t,arc,src[:,1])];dense_d=[nearest(p,vsegs)[0] for p in dense] if len(vsegs) else [];row['dense_interpolated_source_diagnostic']={'count':len(dense_d),'rms_px':float(np.sqrt(np.mean(np.square(dense_d)))) if dense_d else None,'max_px':max(dense_d) if dense_d else None,'not_additional_source_evidence':True}
 R['branches'].append(row);print('BRANCH',bid,row['metrics'],flush=True)
R['silhouette_extraction']=summary;R['fullscene_geometric_firsthit_scope']={'included_mesh_count':len(names),'included_mesh_names':names,'limitations':'No alpha/material transmission simulation and no synthetic person occluder. Only original annotated visible 665 slivers evaluated; no continuation through person cuts. Finite ray probes are numerical checks, not an interval visibility certificate.'}
R['nearest_self_foot_guard']={'total':sum(len(b['points']) for b in R['branches']),'self_feet_fullscene_visible_at_0p10':sum(p['nearest_self_correct_branch']['foot_visible_at_0p10'] for b in R['branches'] for p in b['points']),'failures':[{'branch':b['id'],'source_xy':p['source_xy'],'self':p['nearest_self_correct_branch']} for b in R['branches'] for p in b['points'] if not p['nearest_self_correct_branch']['foot_visible_at_0p10']]}
# Actual G shoulder complexity without hull: distinct mesh silhouette edge directions and chord deviation.
g=next(b for b in R['branches'] if b['id']=='G_C_R_SHOULDER');sg=np.array([r['segment'] for r in g['actual_segments'] if r['fullscene_visible']]);pp=sg.reshape(-1,2);dd=sg[:,1]-sg[:,0];angles=np.rad2deg(np.arctan2(dd[:,1],dd[:,0]))%180
R['G_actual_shoulder_shape']={'actual_evaluated_mesh_branch':'right_shoulder','segment_count':len(sg),'distinct_original_mesh_edges':len(set(tuple(r['mesh_edge_vertex_ids']) for r in g['actual_segments'] if r['fullscene_visible'])),'direction_angle_span_degrees':float(np.max(angles)-np.min(angles)) if len(angles) else None,'native_bounds':np.array([pp.min(0),pp.max(0)]).tolist() if len(pp) else None,'interpretation':'Actual finite smooth C21 panel branch after one five-coefficient H-only erosion; no per-node compensation or G selection. All G points are now training; no circular radius or physical chair acceptance is certified.'}
R['inputs_unchanged']={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p.relative_to(W))] for p in paths};
view_artifacts=[]
for view in ['H','G','665']:
 rows=[b for b in R['branches'] if ('665' if b['source_annotation']['view']=='N665' else b['source_annotation']['view'])==view]
 filename=view+'_actual_silhouette_branches.json';path=O/filename;path.write_text(json.dumps({'view':view,'branches':rows},ensure_ascii=False,indent=2))
 view_artifacts.append({'view':view,'path':filename,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'branch_count':len(rows),'source_point_count':sum(b['source_record_count'] for b in rows)})
R['branch_metrics']=[{k:b[k] for k in ['id','role','target','physical_branch','source_record_count','retained_source_point_count','tolerance_px','metrics']} for b in R.pop('branches')];R['view_artifacts']=view_artifacts
(O/'actual_silhouette_audit.json').write_text(json.dumps(R,ensure_ascii=False,indent=2));print('DONE',flush=True)
# Additional existing annotations, kept separate from the 49 fixed panel points.
extra_ids={'H_C_L_RETURN_OUTER','H_C_L_SUPPORT_INNER','H_C_R_SUPPORT_INNER','H_C_R_SUPPORT_OUTER','N665_C_L_SUPPORT_OUTER','N665_C_L_SUPPORT_INNER'}
extra=[]
for b in ann['branches']:
 if b['id']not in extra_ids:continue
 k='665'if b['view']=='N665'else b['view'];target=sup[1]if '_R_SUPPORT'in b['id']else sup[0];rows=silhouette(k,target);valid=[r for r in rows if r['fullscene_visible']];segs=np.array([r['segment']for r in valid]);pts=[]
 for p in b['points_xy']:
  nn=nearest(p,segs);pts.append({'source_xy':p,'source_firsthit':ray(k,p),'source_post_only_firsthit':ray(k,p,target),'nearest_visible_post_boundary':None if nn is None else {'distance_px':nn[0],'xy':nn[1].tolist(),'object':target,'branch_identity':'unspecified_any_side_not_confirmed_inner_outer_correspondence'}})
 extra.append({'id':b['id'],'view':k,'target':target,'source_annotation':b,'points':pts,'actual_segments':rows,'interpretation':'Original observed source subset; no fitting, no heldout claim. Nearest any visible support boundary is only a permissive spatial mismatch diagnostic; inner/outer and left-return multi-part identity are not independently established. Original person/foreground/image cuts are preserved, not completed to feet.'})
(O/'additional_27_support_source_observations.json').write_text(json.dumps({'status':'SEPARATE_SOURCE_SCOPE_CHECK_NOT_SOURCE_ACCEPTANCE','source_points':sum(len(x['points'])for x in extra),'branches':extra,'panel_boundaries_for_return':{'H':silhouette('H',P)},'limitations':'No source-independent support side correspondence; no rendered person or foreground occluder. Frame-cropped paths below visible cuts must not be called measured legs or feet.'},ensure_ascii=False,separators=(',',':')))
print('ADDITIONAL_SOURCE27_COMPLETE',flush=True)
