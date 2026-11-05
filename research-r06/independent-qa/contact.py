import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
P=Path('/workspace/scratch/fa58bfcf0425/cyber-roof-cloud-r06-20261105');Q=Path(__file__).parent

def node(m):
 if not m or not m.use_nodes:return None
 return {'nodes':[(n.name,n.bl_idname,[(i.name, str(i.default_value[:]) if hasattr(i.default_value,'__len__') else str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in m.node_tree.nodes], 'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in m.node_tree.links]}
def snap():
 s=bpy.context.scene
 return {'meshes':{o.name:{'v':[tuple(o.matrix_world@v.co)for v in o.data.vertices],'p':[tuple(p.vertices)for p in o.data.polygons],'uv':[tuple(x.uv)for x in o.data.uv_layers.active.data]if o.data.uv_layers.active else None,'vis':[o.hide_render,o.hide_viewport],'materials':[node(m)for m in o.data.materials]}for o in s.objects if o.type=='MESH'},'cams':{o.name:[list(sum((tuple(r)for r in o.matrix_world),())),o.data.lens,o.data.sensor_fit]for o in s.objects if o.type=='CAMERA'},'lights':{o.name:[list(sum((tuple(r)for r in o.matrix_world),())),o.data.type,o.data.energy,list(o.data.color),o.data.size]for o in s.objects if o.type=='LIGHT'},'world':node(s.world)}
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r05.blend'));a=snap()
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r06b-experiment.blend'));b=snap();R={'removed':list(a['meshes'].keys()-b['meshes'].keys()),'added':list(b['meshes'].keys()-a['meshes'].keys()),'common_exact':{n:a['meshes'][n]==b['meshes'][n]for n in a['meshes'].keys()&b['meshes'].keys()},'cameras_exact':a['cams']==b['cams'],'lights_exact':a['lights']==b['lights'],'world_exact':a['world']==b['world']}
D={}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 d=o.data;d.calc_loop_triangles();v=[o.matrix_world@x.co for x in d.vertices];t=[tuple(x.vertices)for x in d.loop_triangles];D[o.name]=(v,t,BVHTree.FromPolygons(v,t,all_triangles=True))
new=R['added'];R['new_relations']={};R['self_nonshared_bvh_candidates']={};R['motif_forward_rays']={}
body=next(n for n in new if 'continuous' in n)
for n in new:
 v,t,bvh=D[n];R['new_relations'][n]={m:len(bvh.overlap(D[m][2]))for m in D if m!=n and bvh.overlap(D[m][2])}
 pairs=bvh.overlap(bvh);R['self_nonshared_bvh_candidates'][n]=len({tuple(sorted((i,j))) for i,j in pairs if i!=j and not set(t[i])&set(t[j])})
 if 'motif' in n:
  probes=v+[(v[x[0]]+v[x[1]]+v[x[2]])/3 for x in t];hits=[D[body][2].ray_cast(p,(0,1,0),1)[0] is not None for p in probes];R['motif_forward_rays'][n]={'vertices':len(v),'triangle_centroids':len(t),'hits':sum(hits),'miss':len(hits)-sum(hits)}
R['new_external_aabb_candidates']={n:[m for m in D if m not in new and all(max(p[k] for p in D[n][0]) >= min(p[k] for p in D[m][0]) and max(p[k] for p in D[m][0]) >= min(p[k] for p in D[n][0]) for k in range(3))]for n in new}
(Q/'contact.json').write_text(json.dumps(R,indent=2));print('DONE')
