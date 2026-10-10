import bpy,json,hashlib,collections,time
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];M=R/'models';TOL=1e-5

def inventory():
 out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  me=o.data;me.calc_loop_triangles();pos=np.round(np.array([list(o.matrix_world@v.co) for v in me.vertices]),5);d={};layers=list(me.uv_layers)
  for t in me.loop_triangles:
   order=sorted(range(3),key=lambda i:tuple(pos[t.vertices[i]]));key=tuple(tuple(float(v) for v in pos[t.vertices[i]]) for i in order)
   uvs=tuple(tuple(float(v) for li in order for v in uv.data[t.loops[li]].uv) for uv in layers)
   d.setdefault(key,[]).append(uvs)
  out[o.name]={'layer_names':[x.name for x in layers],'triangles':d,'triangle_count':len(me.loop_triangles)}
 return out
bpy.ops.wm.open_mainfile(filepath=str(M/'CastleHall_Shared_White_Candidate.blend'));a=inventory()
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(M/'CastleHall_Shared_White_Candidate.glb'));b=inventory()
out={'blend_sha256':hashlib.sha256((M/'CastleHall_Shared_White_Candidate.blend').read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256((M/'CastleHall_Shared_White_Candidate.glb').read_bytes()).hexdigest(),'method':'Compare each mesh by name; triangulate source and imported mesh, match triangles via sorted world-position corners rounded to 1e-5 model units; compare corresponding per-loop UV pairs in that corner order, independent of vertex/index reorder. All UV layers compared by layer index; names recorded but not required. Duplicate spatial triangles matched to nearest unused UV tuple.','uv_absolute_tolerance':TOL,'world_position_key_precision':1e-5,'meshes_compared':0,'triangles_compared':0,'uv_corner_pairs_compared':0,'max_uv_absolute_component_error':0.,'missing_meshes':sorted(set(a)-set(b)),'extra_meshes':sorted(set(b)-set(a)),'layer_count_mismatches':[],'geometry_triangle_key_mismatches':[],'uv_mismatches':[],'source_uv_layer_count_histogram':dict(collections.Counter(len(x['layer_names']) for x in a.values())),'imported_uv_layer_count_histogram':dict(collections.Counter(len(x['layer_names']) for x in b.values()))}
for name in sorted(set(a)&set(b)):
 x=a[name];y=b[name];out['meshes_compared']+=1
 if len(x['layer_names'])!=len(y['layer_names']):out['layer_count_mismatches'].append({'name':name,'source':x['layer_names'],'imported':y['layer_names']});continue
 xt=x['triangles'];yt=y['triangles']
 if set(xt)!=set(yt) or any(len(xt[k])!=len(yt.get(k,[])) for k in xt):out['geometry_triangle_key_mismatches'].append({'name':name,'source_triangles':x['triangle_count'],'imported_triangles':y['triangle_count'],'missing_keys':len(set(xt)-set(yt)),'extra_keys':len(set(yt)-set(xt))});continue
 meshmax=0.;bad=0
 for key,srcs in xt.items():
  dsts=list(yt[key])
  for src in srcs:
   src=np.array(src);errs=[float(np.max(np.abs(src-np.array(dst)))) if src.size else 0. for dst in dsts];j=int(np.argmin(errs));err=errs[j];dsts.pop(j);out['triangles_compared']+=1;out['uv_corner_pairs_compared']+=3*len(x['layer_names']);meshmax=max(meshmax,err)
   if err>TOL:bad+=1
 out['max_uv_absolute_component_error']=max(out['max_uv_absolute_component_error'],meshmax)
 if bad:out['uv_mismatches'].append({'name':name,'triangles_above_tolerance':bad,'max_error':meshmax})
out['pass']=not any(out[k] for k in ['missing_meshes','extra_meshes','layer_count_mismatches','geometry_triangle_key_mismatches','uv_mismatches']) and out['uv_corner_pairs_compared']>0
out['scope']='UV data round-trip only. Does not validate source imagery, texture quality, material appearance, or hidden geometry.'
(R/'qa/glb_uv_corner_roundtrip_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));print('UV_CORNER_AUDIT_DONE',flush=True)
