import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
P=Path('/workspace/scratch/fa58bfcf0425/butterfly-finite-stage-20261105');Q=P.parent/'butterfly-s-rail-analysis-20261105';O=Path(__file__).parent;report=json.load(open(Q/'two-parameter-diagnostic.json'));ann=json.load(open(Q/'independent-semantics/annotations-v1.json'));f=P/'models/R04D_material.blend';sha=hashlib.sha256(f.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene
names={'L':'CENTRAL_S_visible_1','R':'CENTRAL_S_visible_-1'};base={};static={}
for o in s.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();vs=[o.matrix_world@v.co for v in o.data.vertices];ts=[tuple(t.vertices)for t in o.data.loop_triangles]
 if o.name in names.values():base[o.name]=(vs,ts)
 else:static[o.name]=BVHTree.FromPolygons(vs,ts,all_triangles=True)
def proj(cam,vs):
 out=[]
 for v in vs:
  q=world_to_camera_view(s,bpy.data.objects[cam],v);out.append([q.x*1192,(1-q.y)*671])
 return out
def nearest(poly,point,closed=False):
 best=1e100;found=None
 for i in range(len(poly)if closed else len(poly)-1):
  a,b=poly[i],poly[(i+1)%len(poly)];dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((point[0]-a[0])*dx+(point[1]-a[1])*dy)/max(1e-20,dx*dx+dy*dy)));q=[a[0]+t*dx,a[1]+t*dy];dist=math.hypot(q[0]-point[0],q[1]-point[1])
  if dist<best:best=dist;found={'distance_px':dist,'dx_px':q[0]-point[0],'dy_px':q[1]-point[1]}
 return found
out={'sha':sha,'producer_sha_match':sha==report['sha256_before_after'],'cases':{}}
for case,r in report['best_cases'].items():
 depth,lift=r['depth'],r['lift'];row={'parameters':[depth,lift],'sides':{},'diagnostics':{}};allmax=0
 for side,name in names.items():
  vs,ts=base[name];nr=len(vs)//10;new=[]
  for i,p in enumerate(vs):
   t=(i//10)/(nr-1)/.32;w=(1-t)**2*(1+2*t)if t<1 else 0;scale=1+depth/(36+p.y);q=Vector((p.x*scale,p.y+depth,7+(p.z-7)*scale+lift*w));new.append(q);allmax=max(allmax,(q-p).length)
  cs=[sum(new[i:i+10],Vector())/10 for i in range(0,len(new),10)];tree=BVHTree.FromPolygons(new,ts,all_triangles=True);rels={k:len(tree.overlap(v))for k,v in static.items()};rels={k:v for k,v in rels.items()if v};ends={}
  for i,label in [(0,'upper'),(-1,'lower')]:
   near=[(b.find_nearest(cs[i])[3],n)for n,b in static.items()if n.startswith('CENTRAL_')];ends[label]=min(near)
  row['sides'][side]={'overlap':rels,'overlap_exact_producer':rels==r['relations'][side]['surface_overlap_targets_triangle_pair_counts'],'end_center_to_surface_only':ends,'actual_mean_center_vs_producer_deformed_center_max':max((v-Vector(w)).length for v,w in zip(cs,r['world_centers'][side]))}
  for cam in r['all_fixed_camera_diagnostics']:
   row['sides'][side].setdefault('camera_forward_depth_range',{})[cam]=[min(-(bpy.data.objects[cam].matrix_world.inverted()@v).z for v in new),max(-(bpy.data.objects[cam].matrix_world.inverted()@v).z for v in new)]
   points=ann['source05'if'05'in cam else'source02']['points'];poly=proj(cam,cs);cap=proj(cam,new[:10]);row['diagnostics'].setdefault(cam,{})
   for a in points:
    if ('_L_'in a['id'])!=(side=='L'):continue
    z=nearest(cap if '_cap'in a['id']else poly,a['xy'],'_cap'in a['id']);old=r['all_fixed_camera_diagnostics'][cam][a['id']];z['distance_difference_producer']=z['distance_px']-old['distance_px'];row['diagnostics'][cam][a['id']]=z
 row['max_actual_vertex_displacement']=allmax;out['cases'][case]=row
out['model_sha_unchanged']=hashlib.sha256(f.read_bytes()).hexdigest()==sha;out['scope']='Only baseline+2 recorded bests; no grid rescan, render or production save. Actual deformed ring vertex averages used for projected centerline.';(O/'check.json').write_text(json.dumps(out,indent=2));print('DONE')
