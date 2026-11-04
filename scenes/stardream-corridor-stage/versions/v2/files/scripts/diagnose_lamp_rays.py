import json,pathlib,numpy as np
P=pathlib.Path(__file__).resolve().parents[1];F=json.load(open(P/'qa/R02-line-fit.json'));S=json.load(open(P/'source-analysis/landmarks-v1.json'));D={'scope':'Conditional ray-plane diagnostic, not measured lamp locations. Plane x2.18 is current assumed diffuser-center plane; fixed-focal trained cameras and cross-view instance/state identity unverified. No geometry modified or accepted. Different inferred height/spacing cannot justify forced per-camera geometry.','frames':{}}
for key,name in [('023','SOURCE_23_oblique'),('026','SOURCE_26_side')]:
 d=F[name];M=np.array(d['matrix_world']);f=d['lens']/36*1192;pts=[]
 for pt in S['frames'][key]['visible_lamps']:
  if key=='023' and pt['xy'][0]<500:continue
  x,y=pt['xy'];v=np.array([(x-596)/f,-(y-335.5)/f,-1])@M[:3,:3].T;t=(2.18-M[0,3])/v[0];w=M[:3,3]+t*v;pts.append({'id':pt['id'],'observed':pt['xy'],'assumed_plane_intersection':w.tolist(),'ray_parameter':float(t),'manual_pixel_error':pt['error_px']})
 D['frames'][key]=pts
(P/'qa/R02-lamp-ray-diagnostic.json').write_text(json.dumps(D,indent=2))
