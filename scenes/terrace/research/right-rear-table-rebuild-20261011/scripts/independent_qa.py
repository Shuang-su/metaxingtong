import bpy,bmesh,json,pathlib,hashlib,math,time
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
P=(pathlib.Path(__file__).resolve().parents[2] if pathlib.Path(__file__).resolve().parent.name=='scripts' else pathlib.Path(__file__).resolve().parent);D=P/'delivery'
BASE=P/'baseline/Green_Terrace_V2_REVIEW_ONLY/Green_Terrace_Working_V16_CompleteSpace_REVIEW.blend'
NEW=D/'Terrace_RightRearTable_Rebuilt_20261011.blend'
def scalar(v):
 if v is None or isinstance(v,(str,int,float,bool)):return v
 if isinstance(v,bpy.types.ID):return [v.bl_rna.identifier,v.name]
 if hasattr(v,'bl_rna'):return props(v)
 try:return [scalar(x) for x in v]
 except:return str(v)
def props(o,exclude=()):
 out={}
 for p in o.bl_rna.properties:
  n=p.identifier
  if n in set(exclude)|{'rna_type','session_uid','preview','tag','is_updated','is_updated_data','is_updated_geometry','is_updated_shading'} or p.type=='COLLECTION':continue
  try:out[n]=scalar(getattr(o,n))
  except:pass
 return out
def h(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def mesh(d):
 return {'verts':h([list(v.co) for v in d.vertices]),'edges':h([list(e.vertices) for e in d.edges]),'polygons':h([[list(p.vertices),p.material_index,p.use_smooth] for p in d.polygons]),'uv':h([[l.name,[list(i.uv) for i in l.data]] for l in d.uv_layers]),'props':props(d,{'name','name_full','users','is_updated','is_updated_data','is_updated_geometry','is_updated_shading'})}
def data(d):
 if d is None:return None
 if isinstance(d,bpy.types.Mesh):return mesh(d)
 if isinstance(d,bpy.types.Curve):
  return {'props':props(d,{'users','is_updated','is_updated_data'}),'splines':[[props(s),[props(v) for v in s.points],[props(v) for v in s.bezier_points]] for s in d.splines]}
 return props(d,{'users','is_updated','is_updated_data'})
def snapshot():
 tab={o.name for o in bpy.data.collections['07_Moon_Side_Table'].all_objects}
 objects={}
 for o in bpy.data.objects:
  objects[o.name]={'type':o.type,'matrix_world':[list(r) for r in o.matrix_world],'matrix_basis':[list(r) for r in o.matrix_basis],'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hide_set':o.hide_get(),'visible_camera':o.visible_camera,'visible_shadow':o.visible_shadow,'visible_diffuse':o.visible_diffuse,'visible_glossy':o.visible_glossy,'visible_transmission':o.visible_transmission,'visible_volume_scatter':o.visible_volume_scatter,'collections':sorted(c.name for c in o.users_collection),'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else [],'data':data(o.data),'modifiers':[props(m) for m in o.modifiers],'constraints':[props(c) for c in o.constraints],'parent':o.parent.name if o.parent else None}
 mats={}
 for m in bpy.data.materials:
  mats[m.name]={'props':props(m,{'users','is_updated','is_updated_data'}),'nodes':[[n.name,props(n),[[s.identifier,scalar(s.default_value) if hasattr(s,'default_value') else None] for s in n.inputs],[[s.identifier,scalar(s.default_value) if hasattr(s,'default_value') else None] for s in n.outputs]] for n in m.node_tree.nodes] if m.node_tree else [],'links':[[l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier] for l in m.node_tree.links] if m.node_tree else []}
 return {'table':sorted(tab),'objects':objects,'materials':mats,'collections':{c.name:{'hide_render':c.hide_render,'hide_viewport':c.hide_viewport,'hide_select':c.hide_select,'children':sorted(x.name for x in c.children)} for c in bpy.data.collections},'scenes':{s.name:{'camera':s.camera.name if s.camera else None,'world':s.world.name if s.world else None,'frame':s.frame_current,'render':props(s.render),'view_settings':props(s.view_settings)} for s in bpy.data.scenes}}
print('BASE_START',flush=True);bpy.ops.wm.open_mainfile(filepath=str(BASE));before=snapshot();baseline_bounds={o.name:{'min':[min((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)],'max':[max((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)]} for o in bpy.data.collections['07_Moon_Side_Table'].all_objects if o.type=='MESH'};print('NEW_START',flush=True);bpy.ops.wm.open_mainfile(filepath=str(NEW));after=snapshot()
exclude=set(before['table'])|set(after['table'])
dif=[]
for name in sorted(set(before['objects'])|set(after['objects'])):
 if name in exclude:continue
 a=before['objects'].get(name);b=after['objects'].get(name)
 if a!=b:dif.append({'object':name,'different_keys':[k for k in set(a or {})|set(b or {}) if (a or {}).get(k)!=(b or {}).get(k)],'sample_before':a,'sample_after':b})
material_diff=[n for n in set(before['materials'])|set(after['materials']) if before['materials'].get(n)!=after['materials'].get(n)]
collections_diff=[n for n in set(before['collections'])|set(after['collections']) if before['collections'].get(n)!=after['collections'].get(n)]
report={'candidate_sha256':hashlib.sha256(NEW.read_bytes()).hexdigest(),'baseline_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'candidate':str(NEW),'baseline':str(BASE),'unrelated':{'object_count':len(before['objects'])-len(before['table']),'differences':dif,'material_differences':material_diff,'collection_visibility_differences':collections_diff,'scene_differences':{k:{'before':before['scenes'].get(k),'after':after['scenes'].get(k)} for k in before['scenes'] if before['scenes'][k]!=after['scenes'].get(k)}},'table_topology':{},'baseline_bounds':baseline_bounds,'bounds':{},'accessory_deltas':{}}
for name in sorted(after['table']):
 o=bpy.data.objects[name]
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data)
 stats={'vertices':len(bm.verts),'edges':len(bm.edges),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'signed_volume_local':bm.calc_volume(signed=True)}
 report['table_topology'][name]=stats;bm.free()
 ps=[o.matrix_world@v.co for v in o.data.vertices];report['bounds'][name]={'min':[min(p[i] for p in ps) for i in range(3)],'max':[max(p[i] for p in ps) for i in range(3)]}
 if name in before['objects'] and not name.startswith('Side_table_') and name!='White_sphere_under_table':
  a=before['objects'][name];b=after['objects'][name]
  report['accessory_deltas'][name]={'geometry_unchanged':a['data']==b['data'],'materials_unchanged':a['materials']==b['materials'],'translation':[b['matrix_world'][i][3]-a['matrix_world'][i][3] for i in range(3)],'other_transform_unchanged':all(a['matrix_world'][i][j]==b['matrix_world'][i][j] for i in range(4) for j in range(4) if not(i<3 and j==3))}
(D/'independent_geometry_qa.json').write_text(json.dumps(report,indent=2))
print('EARLY_REPORT',json.dumps({'unrelated':report['unrelated'],'table_topology':{k:v for k,v in report['table_topology'].items() if k.startswith('Side_table') or k.startswith('White_')}}),flush=True)
