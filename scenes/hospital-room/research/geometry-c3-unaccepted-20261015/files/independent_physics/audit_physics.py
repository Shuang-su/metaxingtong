"""Read-only Blender evaluated-world-mesh independent physical audit.
Usage: blender -b --python audit_physics.py -- FILE.blend [...]
No .blend writes; JSON + gzipped evaluated mesh exports only in this directory.
"""
import bpy,sys,json,math,hashlib,gzip,time,itertools
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent
CURTAIN='Curtain • rebuilt uniform eight-fold drape'
EPS=1e-7

def bounds(v): return [[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]]
def aabb(a,b): return all(a[0][i] <= b[1][i]+EPS and b[0][i] <= a[1][i]+EPS for i in range(3))
def relevant(n):return any(k in n.lower() for k in ['curtain','window','blind','room_shell','pillar','connector'])
def extract(o,dg):
 eo=o.evaluated_get(dg); m=eo.to_mesh();m.calc_loop_triangles()
 v=[eo.matrix_world@x.co for x in m.vertices];tri=[tuple(t.vertices) for t in m.loop_triangles];faces=[tuple(f.vertices) for f in m.polygons]
 edgecounts={}
 for face in faces:
  for i,a in enumerate(face):
   b=face[(i+1)%len(face)];e=tuple(sorted((a,b)));edgecounts[e]=edgecounts.get(e,0)+1
 dat={'name':o.name,'raw_vertices':len(o.data.vertices),'evaluated_vertices':len(v),'evaluated_polygons':len(faces),'evaluated_triangles':len(tri),'bounds':bounds(v),'modifiers':[{'name':mod.name,'type':mod.type,'show_viewport':mod.show_viewport,'show_render':mod.show_render} for mod in o.modifiers],'hide_render':o.hide_render,'nonmanifold_edge_count':sum(x!=2 for x in edgecounts.values())}
 rec={'meta':dat,'verts':v,'triangles':tri,'faces':faces,'bvh':BVHTree.FromPolygons(v,tri,all_triangles=True,epsilon=0),'pbvh':BVHTree.FromPolygons(v,faces,all_triangles=False,epsilon=0)}
 eo.to_mesh_clear();return rec

def strict_edge_hit(p,q,a,b,c):
 # Moller-Trumbore segment/triangle crossing; t strictly interior means
 # an edge traverses the other surface rather than merely touching it.
 d=q-p;e1=b-a;e2=c-a;h=d.cross(e2);det=e1.dot(h)
 if abs(det)<1e-13:return None
 inv=1/det;s=p-a;u=inv*s.dot(h)
 if u < -1e-7 or u>1+1e-7:return None
 qq=s.cross(e1);v=inv*d.dot(qq)
 if v < -1e-7 or u+v >1+1e-7:return None
 t=inv*e2.dot(qq)
 if t < 1e-6 or t>1-1e-6:return None
 # Edge must have >1e-7 scene-unit penetration either side of triangle plane.
 normal=e1.cross(e2);ln=normal.length
 if ln<1e-15:return None
 d0=normal.dot(p-a)/ln;d1=normal.dot(q-a)/ln
 if d0*d1>=0 or min(abs(d0),abs(d1))<=EPS:return None
 return p+t*d

def crossing_points(a,b,pairs):
 count=0;pts=[]
 for ia,ib in pairs:
  aa=[a['verts'][i] for i in a['triangles'][ia]];bb=[b['verts'][i] for i in b['triangles'][ib]];hit=None
  for first,second in ((aa,bb),(bb,aa)):
   for k in range(3):
    hit=strict_edge_hit(first[k],first[(k+1)%3],*second)
    if hit is not None:break
   if hit is not None:break
  if hit is not None:count+=1;pts.append(hit)
 return count,pts

def record_pair(a,b):
 if not aabb(a['meta']['bounds'],b['meta']['bounds']):return None
 pairs=a['bvh'].overlap(b['bvh'])
 if not pairs:return None
 raw_count,pts=crossing_points(a,b,pairs)
 aa,bb=a['meta']['bounds'],b['meta']['bounds']
 axis_depths=[min(aa[1][i],bb[1][i])-max(aa[0][i],bb[0][i]) for i in range(3)]
 count=raw_count if min(axis_depths)>EPS else 0
 out={'a':a['meta']['name'],'b':b['meta']['name'],'triangle_overlap_pairs':len(pairs),'raw_triangle_edge_crossing_pairs':raw_count,'aabb_overlap_depth_xyz':axis_depths,'strict_transverse_crossing_pairs':count,'classification':'surface_crossing' if count else 'touch_or_coplanar_or_tolerance_needs_review','crossing_bounds':bounds(pts) if pts else None,'crossing_samples':[list(p) for p in pts[:5]]}
 n1,n2=out['a'],out['b']
 if CURTAIN in (n1,n2):
  other=n2 if n1==CURTAIN else n1
  out['semantic_interpretation']='unwanted_curtain_blind_interpenetration' if other.startswith('Blind') else 'curtain_structural_contact_requires_review'
 elif n1.startswith('Curtain rail') and n2.startswith('Curtain rail') or ('connector' in n1.lower() or 'connector' in n2.lower()) and ('rail' in n1.lower() or 'rail' in n2.lower() or 'pillar' in n1.lower() or 'pillar' in n2.lower()):
  out['semantic_interpretation']='allowable_join_if_intended_attachment'
 elif not n1.startswith('Blind') and not n2.startswith('Blind'):
  out['semantic_interpretation']='structural_window_frame_join_or_duplicate_requires_review'
 else:out['semantic_interpretation']='blind_structural_intersection_requires_review'
 return out

def run(path):
 t=time.time();before=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));dg=bpy.context.evaluated_depsgraph_get()
 recs={o.name:extract(o,dg) for o in bpy.data.objects if o.type=='MESH' and relevant(o.name)}
 report={'file':str(path),'source_sha256_before':before,'units':'arbitrary D scene units; not metric recovered dimensions','source_fidelity_accepted':False,'physical_audit_is_not_source_acceptance':True,'method':{'geometry':'evaluated dependency-graph meshes, transformed by evaluated matrix_world','bvh':'zero-epsilon triangle BVH plus original polygon BVH for historic count comparison','strict_crossing':'at least one edge penetrates both sides of opposing triangle plane by >1e-7 scene units, and positive AABB overlap >1e-7 on all axes; exact tangencies/float noise cannot certify volume interpenetration; no assertion from AABB alone','limits':['Structural intersections are categorized as possible intended joins, not silently called defects.','No render or camera/source match assessed.','No solid-containment check for unrelated nested objects; curtain/blind tested with transverse surface intersections.']},'objects':[r['meta'] for r in recs.values()]}
 export={n:{'vertices_world':[list(v) for v in r['verts']],'triangles':r['triangles']} for n,r in recs.items()}
 with gzip.open(OUT/(path.stem+'_evaluated_world_meshes.json.gz'),'wt',encoding='utf8') as f:json.dump(export,f,ensure_ascii=False)
 ps=[]
 for a,b in itertools.combinations(recs.values(),2):
  p=record_pair(a,b)
  if p:ps.append(p)
 report['intersecting_pairs']=ps
 curtain=recs[CURTAIN];blinds=[r for n,r in recs.items() if n.startswith('Blind bank 3')]
 cb=[]
 for r in blinds:
  p=next((x.copy() for x in ps if set((x['a'],x['b']))==set((CURTAIN,r['meta']['name']))),None)
  if p:p['original_polygon_overlap_pairs']=len(curtain['pbvh'].overlap(r['pbvh']));cb.append(p)
 report['curtain_bank3_intersections']=cb
 report['curtain_bank3_surface_crossing_object_count']=sum(r['strict_transverse_crossing_pairs']>0 for r in cb)
 cymax=curtain['meta']['bounds'][1][1];bymin=min(r['meta']['bounds'][0][1] for r in blinds)
 margin=.005;delta_front=bymin-cymax-margin
 report['depth_separation_parameters']={'preferred_clearance_example':margin,'curtain_shift_y_max_for_zero_clearance':bymin-cymax,'curtain_shift_y_for_example_clearance':delta_front,'blind_shift_y_for_example_clearance':-delta_front,'note':'Negative world Y points toward room/camera. Values provide conservative global Y interval separation independent of camera; example clearance is not source-measured.'}
 # Synthetic BVH-only translation of curtain, no edit to Blender object or data.
 shifts=[0,bymin-cymax,delta_front]
 report['synthetic_curtain_depth_tests']=[]
 for shift in shifts:
  vv=[v+Vector((0,shift,0)) for v in curtain['verts']];synth={**curtain,'verts':vv,'bvh':BVHTree.FromPolygons(vv,curtain['triangles'],all_triangles=True,epsilon=0),'meta':{**curtain['meta'],'bounds':bounds(vv)}}
  tested=[]
  for n,r in recs.items():
   if n==CURTAIN:continue
   p=record_pair(synth,r)
   if p:tested.append(p)
  report['synthetic_curtain_depth_tests'].append({'shift_y':shift,'bounds':synth['meta']['bounds'],'intersecting_pairs':tested,'bank3_surface_crossing_object_count':sum(p['strict_transverse_crossing_pairs']>0 and any(n.startswith('Blind bank 3') for n in (p['a'],p['b'])) for p in tested)})
 report['source_sha256_after']=hashlib.sha256(path.read_bytes()).hexdigest();report['source_unchanged']=before==report['source_sha256_after'];report['seconds']=time.time()-t
 (OUT/(path.stem+'_physical_audit.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print('AUDIT',path.stem,'curtain/blind=',report['curtain_bank3_surface_crossing_object_count'],'allpairs=',len(ps),'dy',delta_front,'seconds',report['seconds'],flush=True)
for s in sys.argv[sys.argv.index('--')+1:]:run(Path(s))
