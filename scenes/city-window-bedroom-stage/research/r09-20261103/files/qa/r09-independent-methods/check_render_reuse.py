import bpy,json,hashlib
from pathlib import Path
P=Path('/workspace/scratch/fa58bfcf0425/cityroom-refinement-20261103');O=Path(__file__).parent
def val(v):
 try:return list(v)
 except:return str(v)
def props(x):
 out={}
 for p in x.bl_rna.properties:
  if p.identifier in ['rna_type','name','session_uid']:continue
  if p.type in ['BOOLEAN','INT','FLOAT','STRING','ENUM']:
   try:
    v=getattr(x,p.identifier);out[p.identifier]=list(v) if p.is_array else v
   except:pass
 return out
def nodes(t):
 if not t:return None
 return {'nodes':{n.name:{'type':n.bl_idname,'props':props(n),'inputs':{i.identifier:val(i.default_value) for i in n.inputs if hasattr(i,'default_value')}} for n in t.nodes},'links':sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in t.links)}
def snap(f):
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f));s=bpy.context.scene
 return {'objects':{o.name:{'matrix':list(map(list,o.matrix_world)),'hide':o.hide_render,'modifiers':[props(m) for m in o.modifiers],'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'light':props(o.data) if o.type=='LIGHT' else None} for o in s.objects if o.type!='CAMERA'},'materials':{m.name:{'props':props(m),'nodes':nodes(m.node_tree)} for m in bpy.data.materials},'world':{'props':props(s.world),'nodes':nodes(s.world.node_tree)},'cameras':{o.name:{'matrix':list(map(list,o.matrix_world)),'props':props(o.data)} for o in s.objects if o.type=='CAMERA'},'view_settings':props(s.view_settings),'frame':s.frame_current}
a=snap('R09_camera_trial.blend');b=snap('R09b_material.blend');(O/'render-reuse-a.json').write_text(json.dumps(a,default=str));(O/'render-reuse-b.json').write_text(json.dumps(b,default=str));diff=[k for k in a if k!='cameras' and a[k]!=b[k]];cams=[k for k in a['cameras'] if a['cameras'][k]!=b['cameras'][k]]
r={'different_render_state_sections':diff,'different_cameras':cams,'D_E_reuse_supported':not diff and set(cams)<= {'SOURCE_F_fan4k'},'scope':'Compared scene object matrices/modifiers/material slots/visibility/lights, material nodes/input values/link topology/scalar RNA, world nodes/scalar RNA, color management/current frame; geometry checked separately. Render runtime config must match; no rerender pixel identity asserted.'};(O/'R09b-render-reuse-independent.json').write_text(json.dumps(r,indent=2));print(r)
