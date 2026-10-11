import bpy,json,pathlib
from mathutils import Vector,Matrix
P=pathlib.Path(__file__).resolve().parent;o=bpy.data.objects['画外推定_开放前延伸_独立开关'];c=bpy.data.collections['画外推定_开放井格前延伸_OPTIONAL']
# Collection remains disabled. Reconstruct evaluated-free local TRS without enabling it.
m=Matrix.LocRotScale(o.location,o.rotation_euler.to_quaternion(),o.scale)
assert o.parent is None
assert all(abs(v)<1e-8 for v in o.delta_location) and all(abs(v-1)<1e-8 for v in o.delta_scale)
v=[m@p.co for p in o.data.vertices];ys=sorted(set(round(p.y,6) for p in v));zs=sorted(set(round(p.z,6) for p in v));r={'collection':c.name,'hide_render':c.hide_render,'hide_viewport':c.hide_viewport,'object_hide_render':o.hide_render,'parent':None,'transform_method':'local TRS, parent none; hidden collection was never enabled; matrix_world for excluded objects may be stale','world_bounds':[[min(x[k] for x in v),max(x[k] for x in v)] for k in range(3)],'y_vertex_levels':ys,'z_vertex_levels':zs,'location':list(o.location),'scale':list(o.scale),'constraints':len(o.constraints),'modifiers':[x.name for x in o.modifiers]}
(P/'optional_current_audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False,indent=2))
