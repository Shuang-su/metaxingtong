import bpy,json,pathlib,hashlib
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/butterfly-finite-stage-20261105');Q=pathlib.Path(__file__).resolve().parents[1]
f=P/'models/R04D_material.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(f)
bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
obs=json.loads((Q/'observations/source05-visible-strips.json').read_text()); W,H=1192,671
cam02=bpy.data.objects['SOURCE02_conditional_front']; cams=[bpy.data.objects[n] for n in ['SOURCE05_conditional_close','SOURCE05_alternate_tilt_diagnostic']]
def proj(p,c):
 q=world_to_camera_view(s,c,p);return [q.x*W,(1-q.y)*H]
def unproj(uv,c,Y):
 inv=c.calc_matrix_camera(dg,x=W,y=H,scale_x=1,scale_y=1).inverted(); p=inv@Vector((2*uv[0]/W-1,1-2*uv[1]/H,-1,1));p=Vector((p.x/p.w,p.y/p.w,p.z/p.w));orig=c.matrix_world.translation;ray=c.matrix_world.to_3x3()@p;t=(Y-orig.y)/ray.y
 return orig+ray*t

def atrow(points,row):
 hits=[]
 for a,b in zip(points[:-1],points[1:]):
  if (a[1]-row)*(b[1]-row)<=0 and a[1]!=b[1]:
   t=(row-a[1])/(b[1]-a[1]);hits.append(a[0]+t*(b[0]-a[0]))
 return hits

def closest_poly(p,pts):
 best=None
 for i,(a,b) in enumerate(zip(pts[:-1],pts[1:])):
  ab=b-a;t=max(0,min(1,(p-a).dot(ab)/ab.length_squared));v=a+t*ab;d=(p-v).length
  if best is None or d<best['distance']: best={'distance':d,'segment_index':i,'t':t,'point':list(v),'delta':list(p-v)}
 return best

out={'status':'READ_ONLY_FIXED_PLANE_APPEARANCE_HYPOTHESIS_NOT_MODEL','input_sha256':before,'model_unchanged':None,'source05_sha256':obs['sha256'],'method':'Backproject observed bright-core strip edges and appearance centers into fixed Y at original section-center mean/min/max. These are sensitivity hypotheses, not original S being planar or recovered depth. No fitting, smoothing, cap extension, geometry save or render. Original depth range explicitly retained.','null_rows':obs['nulls'],'used_segments_y':obs['used_segments_y'],'objects':{},'cases':[]}
# Targets from independent semantic original-pixel annotations. All already known, not blind tests.
targets={'L':[(550,559.5,[557,562]),(560,556.5,[554,559])], 'R':[(550,629,[626,632]),(560,632,[630,634])]}
for side,sign in [('L',1),('R',-1)]:
 o=bpy.data.objects[f'CENTRAL_S_visible_{sign}'];pts=[sum((o.matrix_world@o.data.vertices[j].co for j in range(i,i+10)),Vector())/10 for i in range(0,len(o.data.vertices),10)]
 ys=[p.y for p in pts];planes={'min':min(ys),'mean':sum(ys)/len(ys),'max':max(ys)};out['objects'][side]={'name':o.name,'section_count':len(pts),'original_section_center_Y_range':max(ys)-min(ys),'planes':planes,'original_world_centers':[list(p) for p in pts]}
 rows=[r for r in obs['rows'] if r['side']==side and r['use_for_planar_shape_diagnostic']]
 for cam in cams:
  for label,Y in planes.items():
   case={'side':side,'camera':cam.name,'plane':label,'Y':Y,'segments':[],'source02_diagnostic_rows':[],'max_source05_backproject_roundtrip_px':0}
   for lo,hi in obs['used_segments_y']:
    seg={'source05_rows':[lo,hi],'samples':[]}
    for r in rows:
     if not lo<=r['y']<=hi:continue
     rr=r['threshold_brackets']['225'];uv=r['center_proxy_xy'];center=unproj(uv,cam,Y);left=unproj([rr['left'],r['y']],cam,Y);right=unproj([rr['right'],r['y']],cam,Y)
     p05=proj(center,cam);e=((p05[0]-uv[0])**2+(p05[1]-uv[1])**2)**.5;case['max_source05_backproject_roundtrip_px']=max(e,case['max_source05_backproject_roundtrip_px'])
     sample={'source05_center_proxy':uv,'world_center_proxy':list(center),'source02_center_proxy':proj(center,cam02),'source02_core_left':proj(left,cam02),'source02_core_right':proj(right,cam02),'world_bright_core_width':(right-left).length,'threshold_brackets':{}}
     for th,edges in r['threshold_brackets'].items():
      sample['threshold_brackets'][th]={'source02_left':proj(unproj([edges['left'],r['y']],cam,Y),cam02),'source02_right':proj(unproj([edges['right'],r['y']],cam,Y),cam02)}
     seg['samples'].append(sample)
    seg['source02_y_span']=[min(x['source02_center_proxy'][1] for x in seg['samples']),max(x['source02_center_proxy'][1] for x in seg['samples'])]
    # Coverage ends are observations, not physical tube ends. Merely report proximity to baseline.
    seg['coverage_boundary_to_old_centerline']=[{'source05_row':z['source05_center_proxy'][1],**closest_poly(Vector(z['world_center_proxy']),pts)} for z in [seg['samples'][0],seg['samples'][-1]]]
    case['segments'].append(seg)
   for row,x,edge in targets[side]:
    rec={'y02':row,'target_center_proxy_x':x,'target_edges_x':edge,'subjective_center_tolerance_px':3,'intersections':[]}
    for seg in case['segments']:
     centers=atrow([p['source02_center_proxy'] for p in seg['samples']],row)
     left=atrow([p['source02_core_left'] for p in seg['samples']],row);right=atrow([p['source02_core_right'] for p in seg['samples']],row)
     if centers:rec['intersections'].append({'segment05':seg['source05_rows'],'center_proxy_x':centers,'signed_center_dx':[v-x for v in centers],'bright_core_edges_x':[left,right]})
    rec['null_reason']=None if rec['intersections'] else 'target row not covered by observed unambiguous source05 segments; no extrapolation'
    case['source02_diagnostic_rows'].append(rec)
   out['cases'].append(case)
out['model_unchanged']=before==sha(f);(Q/'fixed-plane-diagnostic.json').write_text(json.dumps(out,indent=2));print('READ_ONLY_FIXED_PLANES',len(out['cases']),'model_unchanged',out['model_unchanged'])
for c in out['cases']:
 if c['plane']=='mean':print(c['side'],c['camera'],[(r['y02'],[i['signed_center_dx'] for i in r['intersections']]) for r in c['source02_diagnostic_rows']])
