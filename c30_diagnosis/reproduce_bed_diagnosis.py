from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parents[1];D=R/'c30_diagnosis';a=json.load(open(D/'c28_actual_bed_objects.json'));cams=json.load(open(R/'c27/blinds_projection_source.json'))['cameras'];bounds={}
for name,o in a.items():
 if 'verts_local' not in o:continue
 w=np.c_[o['verts_local'],np.ones(len(o['verts_local']))]@np.array(o['matrix_world']).T;bounds[name]={'min':w[:,:3].min(0).tolist(),'max':w[:,:3].max(0).tolist(),'hide_render':o['hide_render']}
obs={};fixed_y=bounds['Bed • mattress and sheet']['max'][1]
for k,points in [('G',[(1200,1057),(1400,1011),(1580,970)]),('N642',[(1200,1024),(1500,959),(1750,902)])]:
 inv=np.linalg.inv(np.array(cams[k]['projection']));obs[k]=[]
 for u,v in points:
  xy=[u/960-1,1-v/540];A=inv@np.array(xy+[-1,1]);B=inv@np.array(xy+[1,1]);A=A[:3]/A[3];B=B[:3]/B[3];pt=A+(fixed_y-A[1])/(B[1]-A[1])*(B-A);obs[k].append({'pixel':[u,v],'fixed_existing_far_y_ray_intersection':pt.tolist()})
(D/'bed_actual_world_bounds.json').write_text(json.dumps(bounds,indent=2));(D/'corrected_bed_edge_observations.json').write_text(json.dumps({'status':'diagnostic only; source edge uncertainty 2-4px; conditional ray interpretation fixes current far-y boundary, not calibrated measurement','fixed_far_y':fixed_y,'views':obs},indent=2))
for n,b in bounds.items():print(n,b)
