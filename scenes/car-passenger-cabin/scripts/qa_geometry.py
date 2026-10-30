import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/car_passenger_cabin_material.blend'))
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
rows=[]
for o in s.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data)
 rows.append({'id':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'boundary_edges':sum(e.is_boundary for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True),'hidden_render':o.hide_render})
 bm.free()
trees={}
for o in s.objects:
 if o.type=='MESH':trees[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons],all_triangles=False)
def cast(origin,direction,ignore=(),distance=2):
 hits=[]
 for name,tree in trees.items():
  if name in ignore:continue
  a,n,idx,dist=tree.ray_cast(Vector(origin),Vector(direction),distance)
  if a is not None:hits.append((dist,name,list(a)))
 return min(hits) if hits else None
window=[]
for i in range(20):
 for j in range(20):
  y=-.68+i*.037;z=1.08+j*.022
  hit=cast((.72,y,z),(1,0,0),ignore=['P12_side_window_glass'],distance=.40)
  window.append({'origin':[.72,y,z],'hit':hit})
pocket=[]
for i in range(10):
 for j in range(20):
  hit=cast((.805+i*.013,-.48+j*.045,.37),(0,0,-1),distance=.2)
  pocket.append(hit)
vent=[]
for i in range(21):
 for j in range(21):
  x=.8+(i-10)*.008;z=.77+(j-10)*.008
  if (x-.8)**2+(z-.77)**2 < .089**2 and all(abs(z-v)>.014 for v in [.715,.77,.825]):
   vent.append(cast((x,.59,z),(0,1,0),distance=.35))
report={'scope':'Mesh closure and sampled openings only. Not full cabin topology, collision sweep, measured scale, or source acceptance. Opaque white pane is a diagnostic material override.','meshes':rows,'total_meshes':len(rows),'all_closed_manifold':all(x['nonmanifold_edges']==0 for x in rows),'all_positive_volume':all(x['signed_volume']>0 for x in rows),'zero_area_faces_total':sum(x['zero_area_faces'] for x in rows),'window_rays':{'count':len(window),'unexpected_opaque_hits':sum(x['hit'] is not None for x in window),'samples':window},'pocket_rays':{'count':len(pocket),'base_hits':sum(x is not None and x[1]=='P09_pocket_base' for x in pocket),'samples':pocket},'vent_gap_rays':{'count':len(vent),'recess_end_hits':sum(x is not None and x[1]=='D05_vent_recess_end' for x in vent),'fascia_blockers':sum(x is not None and x[1]=='D02_dashboard_end_fascia' for x in vent),'samples':vent}}
(R/'qa/geometry-report.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:v for k,v in report.items() if k not in ['meshes','window_rays','pocket_rays','vent_gap_rays']})
print('BAD',[x for x in rows if x['nonmanifold_edges'] or x['zero_area_faces'] or x['signed_volume']<=0])
for key in ['window_rays','pocket_rays','vent_gap_rays']:print(key,{k:v for k,v in report[key].items() if k!='samples'})
