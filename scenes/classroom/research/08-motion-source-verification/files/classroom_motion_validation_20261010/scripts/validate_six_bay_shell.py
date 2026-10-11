import bpy,json,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
P=Path('/workspace/scratch/fa58bfcf0425/classroom_motion_validation_20261010/six_bay_candidate/qa');arch=[];verts=[];faces=[];stats=[]
def render_visible(o):
 def walk(c,parent=True):
  ok=parent and not c.hide_render
  return (ok and o.name in c.objects) or any(walk(k,ok) for k in c.children)
 return not o.hide_render and walk(bpy.context.scene.collection)
keys=['wall','slab','floor','masonry','spandrel','upright','horizontal','glass','glazing','casement','door','window','fullroom']
for o in bpy.data.objects:
 n=o.name.lower()
 if o.type!='MESH' or not render_visible(o) or not any(k in n for k in keys):continue
 if any(k in n for k in ['city','foliage','grade','bookcase','pictogram','vent','monitor','perforated','label','front empty','continuous back upright']):continue
 bb=[o.matrix_world@Vector(v) for v in o.bound_box]
 if min(v.x for v in bb)<-5 or max(v.x for v in bb)>5:continue
 arch.append(o.name);m=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh();off=len(verts);verts.extend([o.matrix_world@v.co for v in m.vertices]);faces.extend([tuple(off+i for i in f.vertices) for f in m.polygons]);o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
 bm=bmesh.new();bm.from_mesh(o.data);stats.append({'name':o.name,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=True)});bm.free()
bvh=BVHTree.FromPolygons(verts,faces);results={}
for side,axis,sign in [('left',0,1),('right',0,-1),('front',1,-1),('rear',1,1),('ceiling',2,1),('floor',2,-1)]:
 miss=[];allowed=[];total=0
 for a in (np.linspace(.02,11.48,180) if axis==0 else np.linspace(-3.97,4.0,140)):
  for b in (np.linspace(.02,2.91,70) if axis<2 else np.linspace(.02,11.48,180)):
   point=[0,float(a),float(b)] if axis==0 else [float(a),5.75,float(b)] if axis==1 else [float(a),float(b),1.5]
   direction=[0,0,0];direction[axis]=sign;hit=bvh.ray_cast(Vector(point),Vector(direction),20);total+=1
   if hit[0] is None:
    if side=='left' and .79<a<1.976 and .64<b<1.855:allowed.append(point)
    else:miss.append(point)
 results[side]={'samples':total,'unintentional_misses':len(miss),'miss_points':miss,'intentional_open_casement_rays':len(allowed)}
out={'architecture_objects':arch,'mesh_stats':stats,'rays':results,'interpretation':'Closed solids independently; intentional opened casement aperture is allowed. Door is in closed observed state. No single-watertight-scene requirement. Ray samples are numerical coverage, not an exact theorem.','resources':{'packed_images':sum(bool(i.packed_file) for i in bpy.data.images),'unpacked_files':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file],'external_libraries':[l.filepath for l in bpy.data.libraries]}}
(P/'fullroom_validation.json').write_text(json.dumps(out,indent=2));print({k:{a:b for a,b in v.items() if a!='miss_points'} for k,v in results.items()});print('BAD MESH', [s for s in stats if s['boundary_edges'] or s['volume']<=0])
