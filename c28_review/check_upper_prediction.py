from pathlib import Path
exec(Path(__file__).with_name('compare_low_dof.py').read_text().split("bounds={'tilt_deg'")[0])
obsu=json.loads((R/'c28/upper_line_observations.json').read_text());fit=json.loads((O/'low_dof_comparison.json').read_text());params=fit['models']['tilt_deg+trim_dx']['parameters'];out={'parameter_source':'H/G lowest slat-only fit, no upper observations used; no re-fit','parameters':params,'views':{}}
for k,d in obsu.items():
 out['views'][k]=[]
 for ob in d['lines']:
  idx=ob['remaining_slat_index'];base=np.array(j['objects'][f'Blind bank 1 • physical slat {idx:02d}']['world_vertices']);lo=base[:,0].min();hi=base[:,0].max();base[:,0]=lo+(base[:,0]-lo)*(hi+f['selected_H_G_only']['right_trim_scene_units']-lo)/(hi-lo);center=base.mean(0);_,_,vh=np.linalg.svd(base[:,1:]-center[1:]);u=vh[0];u*=np.sign(u[0]);n=np.array([-u[1],u[0]]);x=np.linspace(ob['search_domain'][0]+5,ob['search_domain'][1]-5,24);yy=np.polyval(ob['fit_y_ax_b'],x);row={'slat':idx,'observed_line_slope':ob['fit_y_ax_b'][0],'observed_endpoint_heuristic_xy':ob['candidate_endpoint_xy']}
  for label,p in [('C27',{}),('tilt_trim',params)]:
   v=transform(list(p.values()),list(p));xy=projection(k,v);cap=xy[base[:,0]>base[:,0].max()-1e-6];tip=cap[np.argmax(cap[:,1])];h=xy[ConvexHull(xy).vertices];pred=[];th=[]
   for xx in x:
    ys=[a[1]+(b[1]-a[1])*(xx-a[0])/(b[0]-a[0]) for a,b in zip(h,np.roll(h,-1,axis=0)) if min(a[0],b[0])<=xx<=max(a[0],b[0]) and abs(a[0]-b[0])>1e-9];pred.append(max(ys));th.append(max(ys)-min(ys))
   pred=np.array(pred);row[label]={'endpoint_xy':tip.tolist(),'endpoint_heuristic_distance_px':float(np.linalg.norm(tip-ob['candidate_endpoint_xy'])),'line_mean_abs_vertical_px':float(np.mean(abs(pred-yy))),'line_signed_mean_px':float(np.mean(pred-yy)),'line_slope':float(np.polyfit(x,pred,1)[0]),'mean_vertical_thickness_px':float(np.mean(th))}
  out['views'][k].append(row)
(O/'upper_prediction_only.json').write_text(json.dumps(out,indent=2))
for k,rows in out['views'].items():
 for d in rows: print(k,d['slat'],'C27→tilt+trim','line',round(d['C27']['line_mean_abs_vertical_px'],3),round(d['tilt_trim']['line_mean_abs_vertical_px'],3),'end',round(d['C27']['endpoint_heuristic_distance_px'],3),round(d['tilt_trim']['endpoint_heuristic_distance_px'],3),'thick',round(d['C27']['mean_vertical_thickness_px'],3),round(d['tilt_trim']['mean_vertical_thickness_px'],3),'slope',d['observed_line_slope'],d['tilt_trim']['line_slope'])
