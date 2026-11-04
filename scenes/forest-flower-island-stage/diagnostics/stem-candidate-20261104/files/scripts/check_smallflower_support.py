import bpy,pathlib,json
from mathutils import Vector
R=pathlib.Path('forest-diagnostic-replay-20261104').resolve();bpy.ops.wm.open_mainfile(filepath=str(R/'models/R09_material.blend'));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();rows=[]
for ob in s.objects:
 if not ob.name.startswith('SMALL_FLOWERS_patch_'):continue
 verts=[ob.matrix_world@v.co for v in ob.data.vertices]
 if len(verts)%30:raise RuntimeError('unexpected group layout '+ob.name)
 for idx,start in enumerate(range(0,len(verts),30)):
  vv=verts[start:start+30];c=sum(vv,Vector())/30
  # ray begins below lowest flower petal vertex to avoid its own head
  origin=Vector((c.x,c.y,min(v.z for v in vv)-.0001));hit,loc,norm,face,target,m=s.ray_cast(dg,origin,Vector((0,0,-1)),distance=2)
  rows.append({'patch':ob.name,'head':idx,'head_centre':list(c),'head_low_z':min(v.z for v in vv),'hit_below':target.name if hit else None,'vertical_gap_below_head':origin.z-loc.z if hit else None})
(R/'qa/smallflower-support-check.json').write_text(json.dumps({'method':'grouped original five-petal head vertices; central downward representative ray from just under head bottom, not full collision/contact test','heads':rows},indent=2));print('HEADS',len(rows));print('gaps > .05',sum(x['vertical_gap_below_head'] is not None and x['vertical_gap_below_head']>.05 for x in rows));print('hits',sorted(set(x['hit_below'] or 'NONE' for x in rows)))
