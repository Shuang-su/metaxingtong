import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(D/'models/R07_lantern_trial_material.blend'));out={}
for name in ['LANTERN_round_R0','LANTERN_string0_10']:
 ob=bpy.data.objects[name];tree=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons]);rows=[]
 for rib in [o for o in bpy.context.scene.objects if o.name.startswith(name+'_rib_')]:
  v=[rib.matrix_world@x.co for x in rib.data.vertices];centres=[sum(v[i:i+8],Vector())/8 for i in range(0,len(v),8)];dist=[tree.find_nearest(c)[3] for c in centres];rows.append({'rib':rib.name,'max_sampled_section_center_to_paper_mesh':max(dist),'first_last_to_paper':[dist[0],dist[-1]]})
 out[name]=rows
out['scope']='Sampled tube section centres lie on tessellated shell; finite rib radius intentionally overlaps paper. Not exact union, load proof or global clearance check.'
(D/'qa/R07_lantern/sampled-rib-shell-contact.json').write_text(json.dumps(out,indent=2))
