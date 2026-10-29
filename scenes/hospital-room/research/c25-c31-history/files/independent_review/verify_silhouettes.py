"""Read-only actual-mesh source audit at native 1920x1080. No hull or raster fitting.
Source observations/tolerances are fixed. Panel branches use verified construction semantics.
Post INNER/OUTER measurements are directed x-at-observed-y, never nearest-any-boundary.
"""
import bpy,numpy as np,json,hashlib,argparse,sys,collections,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ap=argparse.ArgumentParser();ap.add_argument('--blend',required=True);ap.add_argument('--label',required=True);ap.add_argument('--out',required=True);ap.add_argument('--source',required=True);ap.add_argument('--lock',required=True);ap.add_argument('--semantics');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);O=Path(a.out);O.mkdir(parents=True,exist_ok=True)
P='Chair • narrow curved wraparound back';SUP=['Chair • slim back support','Chair • slim back support.001'];path=Path(a.blend);before=hashlib.sha256(path.read_bytes()).hexdigest();ann=json.load(open(a.source));lock=json.load(open(a.lock));bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
# Respect nested render-hidden/excluded collections and camera visibility.
visible=set()
def viscoll(c,blocked=False):
 blocked=blocked or c.exclude or c.collection.hide_render
 if not blocked:visible.update(o.name for o in c.collection.objects)
 for q in c.children:viscoll(q,blocked)
viscoll(bpy.context.view_layer.layer_collection)
MD={};names=[];tv=[];tf=[];tids=[];vo=0
for ob in s.objects:
 if ob.type!='MESH':continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg);me.calc_loop_triangles();local=np.array([list(q.co)for q in me.vertices],float);m=np.array(ev.matrix_world);v=local@m[:3,:3].T+m[:3,3];f=np.array([list(q.vertices)for q in me.loop_triangles],int);ev.to_mesh_clear()
 if not len(v)or not len(f):continue
 MD[ob.name]={'v':v,'f':f,'local':local,'tree':BVHTree.FromPolygons(v.tolist(),f.tolist(),all_triangles=True)}
 if ob.name in visible and not ob.hide_render and ob.visible_camera:
  ids=np.full(len(f),len(names),dtype=np.int32);names.append(ob.name);tids.append(ids);tv.append(v);tf.append(f+vo);vo+=len(v)
fullv=np.concatenate(tv);fullf=np.concatenate(tf);tids=np.concatenate(tids);FULL=BVHTree.FromPolygons(fullv.tolist(),fullf.tolist(),all_triangles=True);cams={}
for k in ['H','G','665']:
 ob=bpy.data.objects['C10_'+k+'_shared_sofa_height_CONDITIONAL'];mat=np.array(ob.matrix_world);proj=np.array(ob.calc_matrix_camera(dg,x=1920,y=1080,scale_x=s.render.pixel_aspect_x,scale_y=s.render.pixel_aspect_y));cams[k]={'obj':ob,'matrix':mat,'projection':proj,'clip':proj@np.linalg.inv(mat),'invproj':np.linalg.inv(proj)}
def project(k,v):
 h=np.c_[v,np.ones(len(v))]@cams[k]['clip'].T;h=h[:,:3]/h[:,3:];return np.c_[960*(h[:,0]+1),540*(1-h[:,1])]
def ray(k,p,target=None):
 c=cams[k];h=c['invproj']@np.array([p[0]/960-1,1-p[1]/540,-1,1]);q=h[:3]/h[3];d=Vector(c['matrix'][:3,:3]@q).normalized();pt,no,ix,dist=(MD[target]['tree']if target else FULL).ray_cast(Vector(c['matrix'][:3,3]),d,1000)
 return {'object':None if ix is None else target if target else names[tids[ix]],'distance':None if dist is None else float(dist),'xyz':None if pt is None else list(pt)}
def nearest(p,segs):
 if not len(segs):return None
 aa=segs[:,0];d=segs[:,1]-aa;t=np.clip(np.sum((p-aa)*d,axis=1)/np.maximum(np.sum(d*d,axis=1),1e-24),0,1);q=aa+t[:,None]*d;dist=np.linalg.norm(q-p,axis=1);i=int(np.argmin(dist));return float(dist[i]),q[i],i
# Accept a declared semantic correspondence only after exact actual-coordinate verification.
semantic_check={}
if a.label=='C23':
 ref=np.asarray(lock['panel']['vertices'],np.float32).astype(float);assert np.array_equal(MD[P]['local'],ref),'C23 lock/mesh vertex mismatch';baseu=np.asarray(lock['panel']['parameter_u']);U=np.tile(baseu,len(ref)//len(baseu));semantic_check={'method':'Verified original C23 actual evaluated local32 coordinates against locked vertices; original ring-major u only for C23.','verified':True}
else:
 sem=json.load(open(a.semantics));ref=sem.get('vertices',sem.get('actual_vertices',sem.get('panel_vertices')))
 if ref is None and 'panel' in sem:ref=sem['panel'].get('vertices')
 if ref is not None:
  assert np.array_equal(MD[P]['local'],np.asarray(ref,np.float32).astype(float)),'C25 semantic coordinate mismatch'
 else:
  expected=sem.get('vertex_coordinate_sha256');actual=hashlib.sha256(np.asarray(MD[P]['local'],dtype=np.float32).tobytes()).hexdigest();assert expected is None or actual==expected,'C25 coordinate hash mismatch'
 us=sem.get('parameter_u_per_vertex',sem.get('vertex_parameter_u',sem.get('parameter_u')))
 if us is None and 'vertices_semantics' in sem:us=[v.get('parameter_u')for v in sem['vertices_semantics']]
 assert us is not None and len(us)==len(MD[P]['local']),'C25 must provide explicit u per actual vertex, never inferred reused ring IDs'
 U=np.array([np.nan if u is None else u for u in us],float);semantic_check={'method':'Explicit C25 per-vertex construction semantics bound to actual evaluated mesh hash and verified vertex count. No C23 ring IDs are reused. Independent H geometric inside-normal checks constrain top/lower/shoulder physical orientation; semantics are declared construction evidence, not independent source evidence.','verified':True,'source_file':str(a.semantics),'source_sha256':hashlib.sha256(Path(a.semantics).read_bytes()).hexdigest(),'non_null_parameter_count':int(np.sum(np.isfinite(U))),'mesh_vertices':len(U),'actual_mesh_local_float32_coordinate_sha256':hashlib.sha256(np.asarray(MD[P]['local'],dtype=np.float32).tobytes()).hexdigest(),'coordinate_reference_provided':ref is not None}
def label_edge(e):
 us=U[np.array(e)];
 if not np.all(np.isfinite(us)):return 'unclassified_cap',None
 du=(us[1]-us[0]+6)%12-6;mid=(us[0]+du/2)%12
 if 0<=mid<=3:return 'top',float(mid)
 if 3.1<=mid<=6:return 'right_shoulder',float(mid)
 if 6.5<=mid<=9.5:return 'lower',float(mid)
 return 'left_return_or_transition',float(mid)
EDGES={};CACHE={};summary={}
def facing_edges(k,target):
 key=(k,target)
 if key in EDGES:return EDGES[key]
 v,f=MD[target]['v'],MD[target]['f'];tri=v[f];normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);front=np.einsum('ij,ij->i',normal,cams[k]['matrix'][:3,3]-tri.mean(1));edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);face=np.tile(np.arange(len(f)),3);edges=np.sort(edges,axis=1);order=np.lexsort((edges[:,1],edges[:,0]));e=edges[order];fi=face[order];eq=np.all(e[1:]==e[:-1],axis=1);starts=np.r_[0,np.where(~eq)[0]+1];ends=np.r_[starts[1:],len(e)];two=ends-starts==2;ix=starts[two];mask=front[fi[ix]]*front[fi[ix+1]]<0;selected=e[ix[mask]];uv=project(k,v);EDGES[key]=[(ee,uv[ee])for ee in selected];return EDGES[key]
def geometric_label_ok(kind,inside):
 # Geometric orientation checks in H, the construction chart; no source point is used to relabel an edge.
 return kind!='top' or inside[1]>0.15

def silhouette(k,target):
 key=(k,target)
 if key in CACHE:return CACHE[key]
 edges=facing_edges(k,target);rows=[];rejected=[]
 for e,sg in edges:
  d=sg[1]-sg[0];length=np.linalg.norm(d)
  if length<1e-7:continue
  nn=np.array([-d[1],d[0]])/length;lab,u=label_edge(e)if target==P else('support_silhouette',None);cnt=max(1,int(np.ceil(length/.25)))
  for j in range(cnt):
   aa=sg[0]+j/cnt*d;bb=sg[0]+(j+1)/cnt*d;p=(aa+bb)/2
   if not(0<=p[0]<=1919 and 0<=p[1]<=1079):continue
   hm=ray(k,p-.05*nn,target);hp=ray(k,p+.05*nn,target)
   if(hm['object']==target)==(hp['object']==target):continue
   inside=nn if hp['object']==target else -nn
   geom_ok=True
   if target==P and k=='H':
    geom_ok=inside[1]>.15 if lab=='top' else inside[1]<-.15 if lab=='lower' else inside[0]<-.15 if lab=='right_shoulder' else True
   if not geom_ok:rejected.append({'edge':e.tolist(),'branch':lab,'xy':p.tolist(),'inside':inside.tolist()});continue
   hi=ray(k,p+.1*inside);ho=ray(k,p-.1*inside);vis=hi['object']==target and ho['object']!=target
   rows.append({'segment':[aa.tolist(),bb.tolist()],'mesh_edge_vertex_ids':e.tolist(),'construction_branch':lab,'parameter_midpoint':u,'inside_direction':inside.tolist(),'fullscene_visible':bool(vis),'inside_firsthit':hi['object'],'outside_firsthit':ho['object']})
 summary[k+'::'+target]={'facing_candidate_edges':len(edges),'self_boundary_native_subsegments':len(rows),'fullscene_visible_subsegments':sum(r['fullscene_visible']for r in rows),'branch_counts':dict(collections.Counter(r['construction_branch']for r in rows)),'orientation_rejected_count':len(rejected),'orientation_rejected_first_20':rejected[:20],'occluder_counts':dict(collections.Counter(r['inside_firsthit']for r in rows if not r['fullscene_visible']))};CACHE[key]=rows;print('SILHOUETTE',k,target,summary[k+'::'+target],flush=True);return rows

def metrics(vals,n,tol):
 valid=[v for v in vals if v is not None]
 return {'record_count':n,'scored_count':len(valid),'missing_count':n-len(valid),'rms_px':float(np.sqrt(np.mean(np.square(valid))))if valid else None,'max_px':float(max(valid))if valid else None,'within_tolerance_count':sum(v<=tol for v in valid),'all_original_points_within_tolerance':len(valid)==n and all(v<=tol for v in valid)}
R={'label':a.label,'blend':str(path),'sha256_before':before,'native_resolution':[1920,1080],'source_sha256':hashlib.sha256(Path(a.source).read_bytes()).hexdigest(),'method':'Actual evaluated mesh view-facing adjacency edges. Target-only ray tests establish self-silhouette, full-scene first-hit rays establish geometric visibility. Panel nearest distances are restricted to verified physical construction branch and <=0.25 px subsegments. Supports use named side x at the exact original observed y, never nearest-any-side. No convex hull, no dropping records or expanding source cuts.','roles':{'H':'Prior training / shape construction source','G':'Prior training regression, not a holdout','665':'Prior training regression; only annotated person-visible fragments, no completion through person cuts'},'semantic_check':semantic_check,'panel_branches':[],'support_branches':[],'return_object_diagnostics':[]}
panelids={'H_C_TOP','H_C_R_SHOULDER','H_C_LOWER','G_C_TOP','G_C_R_SHOULDER','N665_C_TOP_SLIVER','N665_C_LOWER_SLIVER'}
for b in ann['branches']:
 if b['id']not in panelids:continue
 k='665'if b['view']=='N665'else b['view'];bid=b['id'];kind='top'if 'TOP'in bid else'right_shoulder'if'SHOULDER'in bid else'lower';rows=[r for r in silhouette(k,P)if r['construction_branch']==kind];vis=[r for r in rows if r['fullscene_visible']];pts=[]
 for pp in b['points_xy']:
  p=np.array(pp,float);item={'source_xy':pp,'source_firsthit':ray(k,p),'source_target_only_firsthit':ray(k,p,P)}
  for title,rr in [('self_correct_branch',rows),('visible_correct_branch',vis)]:
   nr=nearest(p,np.array([r['segment']for r in rr]));item[title]=None
   if nr is not None:
    dist,q,i=nr;n=np.array(rr[i]['inside_direction']);hi=ray(k,q+.1*n);ho=ray(k,q-.1*n)
    item[title]={'distance_px':dist,'xy':q.tolist(),'mesh_edge':rr[i]['mesh_edge_vertex_ids'],'construction_branch':kind,'inside_firsthit':hi,'outside_firsthit':ho,'foot_visible_at_0p10':hi['object']==P and ho['object']!=P}
  pts.append(item)
 row={'id':bid,'view':k,'target':P,'physical_branch':kind,'tolerance_px':b['tolerance_px'],'source_annotation':b,'points':pts,'self_metrics':metrics([p['self_correct_branch']['distance_px']if p['self_correct_branch']else None for p in pts],len(pts),b['tolerance_px']),'visible_metrics':metrics([p['visible_correct_branch']['distance_px']if p['visible_correct_branch']else None for p in pts],len(pts),b['tolerance_px']),'nearest_self_foot_fullscene_visible_count':sum(bool(p['self_correct_branch']and p['self_correct_branch']['foot_visible_at_0p10'])for p in pts),'nearest_visible_foot_verified_count':sum(bool(p['visible_correct_branch']and p['visible_correct_branch']['foot_visible_at_0p10'])for p in pts),'self_subsegment_count':len(rows),'visible_subsegment_count':len(vis)};R['panel_branches'].append(row);print('PANEL',bid,row['visible_metrics'],flush=True)
# Exact-y directed support boundary, using ray tests at the interpolated edge foot.
def directed(k,target,p,side):
 choices=[]
 for e,sg in facing_edges(k,target):
  if abs(sg[1,1]-sg[0,1])<1e-10:continue
  t=(p[1]-sg[0,1])/(sg[1,1]-sg[0,1])
  if t<-1e-10 or t>1+1e-10:continue
  q=sg[0]+t*(sg[1]-sg[0]);left=ray(k,q+[-.05,0],target)['object']==target;right=ray(k,q+[.05,0],target)['object']==target
  if left==right:continue
  if(side=='left'and not right)or(side=='right'and not left):continue
  inside=np.array([1.,0.])if right else np.array([-1.,0.]);hi=ray(k,q+.1*inside);ho=ray(k,q-.1*inside);choices.append({'x':float(q[0]),'xy':q.tolist(),'mesh_edge':e.tolist(),'fullscene_visible':hi['object']==target and ho['object']!=target,'inside_firsthit':hi,'outside_firsthit':ho})
 if not choices:return {'source_xy':p,'selected_boundary':None,'signed_x_error_px':None,'absolute_x_error_px':None,'source_firsthit':ray(k,p),'boundary_candidates':0}
 chosen=(min if side=='left'else max)(choices,key=lambda x:x['x']);d=chosen['x']-p[0]
 return {'source_xy':p,'selected_boundary':chosen,'signed_x_error_px':float(d),'absolute_x_error_px':float(abs(d)),'source_firsthit':ray(k,p),'source_target_only_firsthit':ray(k,p,target),'boundary_candidates':len(choices)}
extraids={'H_C_L_RETURN_OUTER','H_C_L_SUPPORT_INNER','H_C_R_SUPPORT_INNER','H_C_R_SUPPORT_OUTER','N665_C_L_SUPPORT_OUTER','N665_C_L_SUPPORT_INNER'}
for b in ann['branches']:
 if b['id']not in extraids:continue
 k='665'if b['view']=='N665'else b['view'];bid=b['id'];target=SUP[1]if'_R_SUPPORT'in bid else SUP[0];side='left'if ('L_RETURN'in bid or ('L_SUPPORT'in bid and'OUTER'in bid)or('R_SUPPORT'in bid and'INNER'in bid))else'right'
 def onerow(target):
  pts=[directed(k,target,p,side)for p in b['points_xy']];vals=[p['absolute_x_error_px']for p in pts];visiblevals=[p['absolute_x_error_px']if p['selected_boundary']and p['selected_boundary']['fullscene_visible']else None for p in pts]
  return {'id':bid,'view':k,'target':target,'direction':side,'measurement':'x at original source y; explicitly named physical side','tolerance_px':b['tolerance_px'],'source_annotation':b,'points':pts,'self_metrics':metrics(vals,len(pts),b['tolerance_px']),'visible_metrics':metrics(visiblevals,len(pts),b['tolerance_px'])}
 row=onerow(target);R['support_branches'].append(row);print('SUPPORT',bid,target,row['visible_metrics'],flush=True)
 if bid=='H_C_L_RETURN_OUTER':
  diag=onerow(P);diag['interpretation']='Separate panel-only diagnostic of composite source return. Never combined by best-any-object selection; source does not independently establish the split between frame and panel.';R['return_object_diagnostics'].append(diag)
R['source_counts']={'panel_original_records':sum(len(b['points'])for b in R['panel_branches']),'ancillary_original_records':sum(len(b['points'])for b in R['support_branches']),'extra_panel_return_diagnostic_records_not_additional_evidence':8}
assert R['source_counts']['panel_original_records']==49 and R['source_counts']['ancillary_original_records']==27
R['fullscene_firsthit_scope']={'included_mesh_count':len(names),'mesh_names':names,'limitations':'Geometric opaque surfaces only; material alpha/transmission and synthetic person/foreground occluders are not simulated. Source person/image cuts remain exactly the original annotated fragments. Finite ray probes and numerical projection, not interval-certified visibility.'};R['silhouette_extraction']=summary;R['camera_projection']={k:{'matrix_world':c['matrix'].tolist(),'projection':c['projection'].tolist(),'lens':c['obj'].data.lens,'shift':[c['obj'].data.shift_x,c['obj'].data.shift_y]}for k,c in cams.items()};R['sha256_after']=hashlib.sha256(path.read_bytes()).hexdigest();R['input_unchanged']=before==R['sha256_after'];(O/(a.label+'_silhouette_report.json')).write_text(json.dumps(R,ensure_ascii=False,indent=2));print('DONE',a.label,flush=True)
