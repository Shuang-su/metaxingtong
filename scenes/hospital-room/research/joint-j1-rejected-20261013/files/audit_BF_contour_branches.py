from screen_joint_candidate import *
Q=json.load(open(R/'joint_candidate_screening.json'))['selected'];g=Q['geometry'];HC=json.load(open(R/'heldout_camera_validation.json'));aa={f['id']:f for f in ann['features']}
observ={'B':{'left_side':[[708,1070]],'upper':[[787,955],[1510,923]],'right_side':[[1810,1020]]},'F':{'left_side':aa['F_bed_upper_left_visible']['source_xy'][:4],'upper':aa['F_bed_upper_left_visible']['source_xy'][4:]}}
vert=bed_transform(V[BED],g);out={'status':'DIRECTED_BRANCH_AUDIT_NOT_CAMERA_CALIBRATION','mesh_identity':BED,'geometry_modified':False,'camera_modified':False,'source_identity_limits':['B contour points remain manual approximate silhouette observations.','F points are from audited native image annotation; split at curved left shoulder is approximate.','No point is claimed to be the projection of a named mesh vertex.','B/F cameras are TV-plane hypotheses, not externally calibrated patient cameras.'],'views':{}}
for k,groups in observ.items():
 cam=np.array(HC['views'][k]['camera']);proj=project(cam,vert);poly=proj[ConvexHull(proj).vertices];a=poly;b=np.roll(poly,-1,axis=0);v=b-a;res={}
 for branch,points in groups.items():
  records=[]
  for uv in points:
   u=np.array(uv);t=np.clip(((u-a)*v).sum(1)/(v*v).sum(1),0,1);ds=((u-(a+t[:,None]*v))**2).sum(1);i=ds.argmin();nearp=a[i]+t[i]*v[i]
   # Select envelope by branch and cross-section, no index pair or arbitrary hull edge.
   axis=0 if branch=='upper' else 1;vals=[]
   for p0,p1 in zip(a,b):
    if min(p0[axis],p1[axis])<=u[axis]<=max(p0[axis],p1[axis]) and abs(p1[axis]-p0[axis])>1e-8:
     z=p0+(u[axis]-p0[axis])/(p1[axis]-p0[axis])*(p1-p0);vals.append(z)
   if vals:
    target=(min(vals,key=lambda z:z[1]) if branch=='upper' else (min(vals,key=lambda z:z[0]) if branch=='left_side' else max(vals,key=lambda z:z[0])))
    directed=float(target[1]-u[1] if branch=='upper' else target[0]-u[0]);status='supported_cross_section'
   else:target=None;directed=None;status='source_sample_outside_projected_silhouette_extent'
   records.append({'source_xy':uv,'nearest_any_hull_xy':nearp.tolist(),'nearest_any_hull_distance_px':float(np.sqrt(ds[i])),'branch_target_xy':target.tolist() if target is not None else None,'directed_axis_residual_px':directed,'branch_status':status})
  res[branch]=records
 out['views'][k]={'branch_records':res,'not_a_geometry_pass':True}
(R/'BF_directed_contour_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2))
