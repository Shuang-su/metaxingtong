import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).parent;R=O.parent/'backstage-pearl-r14-20261105';out={};snapshots={}
for stage in ['R13','R14']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'models/{stage}_material.blend'));s=bpy.context.scene;d={};dg=bpy.context.evaluated_depsgraph_get()
 for o in s.objects:
  if o.type!='MESH':continue
  e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();vs=[o.matrix_world@v.co for v in m.vertices];fs=[list(t.vertices) for t in m.loop_triangles];d[o.name]={'v':vs,'f':fs,'min':[min(v[k] for v in vs) for k in range(3)],'max':[max(v[k] for v in vs) for k in range(3)]};e.to_mesh_clear()
 bv={n:BVHTree.FromPolygons(x['v'],x['f'],all_triangles=True) for n,x in d.items()};names=sorted(n for n in d if n.startswith('NECKLACE_pearl_proxy_'));table=d['TABLE_top'];rows=[];relations=[];candidates=[]
 for n in names:
  x=d[n];bottom=[v for v in x['v'] if abs(v.z-x['min'][2])<1e-7];rows.append({'name':n,'bottom_z':x['min'][2],'table_top_z':table['max'][2],'z_gap':x['min'][2]-table['max'][2],'bottom_vertex_surface_min':min(bv['TABLE_top'].find_nearest(v)[3] for v in bottom),'bottom_vertex_xy_inside_table_bounds':all(table['min'][0]<v.x<table['max'][0] and table['min'][1]<v.y<table['max'][1] for v in bottom)})
  for k,y in d.items():
   if k==n or (k in names and k<n):continue
   sep=max(max(x['min'][j]-y['max'][j],y['min'][j]-x['max'][j]) for j in range(3))
   if sep>1e-7:continue
   cnt=len(bv[n].overlap(bv[k]));candidates.append({'a':n,'b':k,'triangle_pairs':cnt,'aabb_separation':sep})
   if cnt:relations.append({'a':n,'b':k,'triangle_pairs':cnt})
 snapshots[stage]=d
 out[stage]={'model_sha':hashlib.sha256((R/f'models/{stage}_material.blend').read_bytes()).hexdigest(),'pearls':rows,'aabb_candidates':candidates,'surface_relations':relations}
out['world_vertex_deltas']={n:{'min':[min((v-w)[j] for v,w in zip(snapshots['R14'][n]['v'],snapshots['R13'][n]['v'])) for j in range(3)],'max':[max((v-w)[j] for v,w in zip(snapshots['R14'][n]['v'],snapshots['R13'][n]['v'])) for j in range(3)]} for n in names}
(O/'contacts.json').write_text(json.dumps(out,indent=2));print('DONE')
