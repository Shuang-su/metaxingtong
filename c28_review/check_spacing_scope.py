import pathlib,json,numpy as np
R=pathlib.Path(__file__).resolve().parents[1];P=R/'c27';O=R/'c28_review';j=json.loads((P/'blinds_projection_source.json').read_text());f=json.loads((P/'bank1_fit.json').read_text());o=json.loads((R/'c28/upper_line_observations.json').read_text());d=json.loads((O/'upper_prediction_only.json').read_text());out={'method':'No parameter fit. Compare observed ridge line spacing at common native x against C27 lower projected envelope; evaluate projected full-slat visibility under illustrative center-Z scales 0.8, 0.84, 0.86, 0.9. Occlusion ignored.','fit_scope_note':'Original C27 width trimming retained. Each slat world-Z vertex offset equals (scale-1)*(true mean world-Z of that slat - slat02 mean world-Z); slat02 fixed; cross section shape unchanged.','spacing':{},'visibility':{}}
for k,rows in d['views'].items():
 x={'H':787.5,'G':202.5}[k];ys=np.array([np.polyval(a['fit_y_ax_b'],x) for a in o[k]['lines']]);py=ys+np.array([a['C27']['line_signed_mean_px'] for a in rows]);out['spacing'][k]={'sample_x':x,'source_ridge_y':ys.tolist(),'C27_lower_envelope_y':py.tolist(),'source_adjacent_spacing_px':(-np.diff(ys)).tolist(),'C27_adjacent_spacing_px':(-np.diff(py)).tolist(),'C27_spacing_excess_px':(-np.diff(py)+np.diff(ys)).tolist(),'source_over_C27_span_ratio':float((ys[0]-ys[-1])/(py[0]-py[-1])),'C27_signed_vertical_error_px':(py-ys).tolist()}
anchor=np.array(j['objects'][f['target_group'][1]]['world_vertices']).mean(0)[2];out['anchor_world_z']=float(anchor)
def project(k,v):
 q=np.c_[v,np.ones(len(v))]@np.array(j['cameras'][k]['projection']).T;uv=q[:,:2]/q[:,3:4];return np.c_[(uv[:,0]+1)*960,(1-uv[:,1])*540]
for k in ['H','G','N642']:
 out['visibility'][k]={}
 for sc in [1.,.9,.86,.84,.8]:
  rows=[]
  for idx in range(2,27):
   v=np.array(j['objects'][f'Blind bank 1 • physical slat {idx:02d}']['world_vertices']);lo=v[:,0].min();hi=v[:,0].max();v[:,0]=lo+(v[:,0]-lo)*(hi+f['selected_H_G_only']['right_trim_scene_units']-lo)/(hi-lo);v[:,2]+=(sc-1)*(v[:,2].mean()-anchor);uv=project(k,v);mn=uv.min(0);mx=uv.max(0)
   if mx[0]>=0 and mn[0]<=1920 and mx[1]>=0 and mn[1]<=1080: rows.append({'slat':idx,'x_minmax':[float(mn[0]),float(mx[0])],'y_minmax':[float(mn[1]),float(mx[1])]})
  out['visibility'][k][str(sc)]=rows
(O/'spacing_scope_diagnosis.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out['spacing'],indent=2))
for k,x in out['visibility'].items():
 for sc,rows in x.items(): print(k,sc,[(r['slat'],tuple(round(v,2) for v in r['y_minmax'])) for r in rows])
