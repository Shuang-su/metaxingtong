import bpy,bmesh,json,hashlib,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
r=Path(__file__).parent;NAMES=['Bed end • moulded central recess','Bed end • cream inset face']
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def mesh(o):return {'vertices':[list(v.co) for v in o.data.vertices],'edges':[list(e.vertices) for e in o.data.edges],'faces':[list(f.vertices) for f in o.data.polygons],'smooth':[p.use_smooth for p in o.data.polygons],'material_index':[p.material_index for p in o.data.polygons],'matrix':list(map(list,o.matrix_world)),'uv':{uv.name:[list(d.uv) for d in uv.data] for uv in o.data.uv_layers}}
def plain(v):
 if v is None or isinstance(v,(str,int,float,bool)):return v
 try:return [plain(x) for x in v]
 except TypeError:return str(v)
def props(x,names):return {n:plain(getattr(x,n)) for n in names}
def node_tree(t):return {'nodes':[(n.name,n.type,[(p.name,plain(p.default_value)) for p in n.inputs if hasattr(p,'default_value')]) for n in t.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in t.links]}
def snap(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));d={'objects':{},'materials':{},'world':None,'collections':{},'active_camera':bpy.context.scene.camera.name};geometry={}
 for o in bpy.context.scene.objects:
  v={'type':o.type,'matrix':list(map(list,o.matrix_world)),'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'visible_camera':o.visible_camera,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'modifiers':[(m.name,m.type) for m in o.modifiers]}
  if o.type=='MESH':v['mesh_hash']=sha(mesh(o));geometry[o.name]=mesh(o)
  if o.type=='CAMERA':v['camera']=props(o.data,['type','lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','clip_start','clip_end','ortho_scale'])
  if o.type=='LIGHT':v['light']=props(o.data,['type','energy','color'])
  d['objects'][o.name]=v
 for m in bpy.data.materials:
  if m.users:d['materials'][m.name]={'diffuse':list(m.diffuse_color),'nodes':node_tree(m.node_tree) if m.use_nodes else None}
 if bpy.context.scene.world:d['world']=node_tree(bpy.context.scene.world.node_tree) if bpy.context.scene.world.use_nodes else list(bpy.context.scene.world.color)
 for c in bpy.data.collections:d['collections'][c.name]=[c.hide_render,c.hide_viewport]
 return d,geometry
base,bg=snap(r.parent/'candidate_b/hospital_endboard_shape_B.blend');cand,cg=snap(r/'hospital_recess_outline_C.blend');white,wg=snap(r/'hospital_recess_outline_C_white.blend')
changed=[n for n in base['objects'] if base['objects'][n]!=cand['objects'].get(n)]
report={'blender_version':bpy.app.version_string,'object_count_B':len(base['objects']),'object_count_C':len(cand['objects']),'changed_objects':changed,'added':list(cand['objects'].keys()-base['objects'].keys()),'removed':list(base['objects'].keys()-cand['objects'].keys()),'only_target_meshes_changed':set(changed)==set(NAMES),'unaffected_meshes_byte_value_identical':all(bg[n]==cg[n] for n in bg if n not in NAMES),'all_camera_states_equal':all(o==cand['objects'][n] for n,o in base['objects'].items() if o['type']=='CAMERA'),'target_transforms_materials_visibility_equal':all({k:v for k,v in base['objects'][n].items() if k!='mesh_hash'}=={k:v for k,v in cand['objects'][n].items() if k!='mesh_hash'} for n in NAMES),'materials_lights_world_collections_preserved':base['materials']==cand['materials'] and base['world']==cand['world'] and base['collections']==cand['collections'] and all(o==cand['objects'][n] for n,o in base['objects'].items() if o['type']=='LIGHT'),'white_and_material_mesh_geometry_transforms_identical':{n:{k:v for k,v in g.items() if k!='material_index'} for n,g in cg.items()}=={n:{k:v for k,v in g.items() if k!='material_index'} for n,g in wg.items()},'active_camera_preserved':base['active_camera']==cand['active_camera'],'glb_roundtrip':{},'status':'Technical geometry checks only; no source fidelity acceptance'}
# Verify original UV values on the unchanged flat front/back planes, independent of material colors.
uv_checks={}
for name in NAMES:
 old,new=bg[name],cg[name];checks={}
 for side,edge in [('front',min(v[0] for v in old['vertices'])),('back',max(v[0] for v in old['vertices']))]:
  def cap_values(g,edge):
   off=0;out=[]
   for f in g['faces']:
    if len(f)>4 and all(abs(g['vertices'][i][0]-edge)<1e-7 for i in f):
     out.extend([(g['vertices'][vi],g['uv']['UVMap'][off+j]) for j,vi in enumerate(f)])
    off+=len(f)
   return out
  a,b=cap_values(old,edge),cap_values(new,edge)
  # Original box cap is a quad, so use its four coplanar loops if the >4 pass is empty.
  if not a:
   off=0
   for f in old['faces']:
    if len(f)>=4 and all(abs(old['vertices'][i][0]-edge)<1e-7 for i in f):a.extend([(old['vertices'][vi],old['uv']['UVMap'][off+j]) for j,vi in enumerate(f)])
    off+=len(f)
  assert len(a)>=4 and len(b)>=4
  A=np.array([[co[1],co[2],1] for co,uv in a]);U=np.array([uv for co,uv in a]);coef=np.linalg.lstsq(A,U,rcond=None)[0];B=np.array([[co[1],co[2],1] for co,uv in b]);V=np.array([uv for co,uv in b]);err=float(np.max(np.abs(B@coef-V)));checks[side]=err
  assert err<1e-6
 uv_checks[name]=checks
report['uv_original_flat_cap_field_max_abs_error']=uv_checks
def imported(path):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path));d={};qa=[];verts={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  world=[tuple(o.matrix_world@v.co) for v in o.data.vertices];verts[o.name]=world;tris=sorted(tuple(sorted(tuple(round(c,6) for c in world[i]) for i in f.vertices)) for f in o.data.polygons);d[o.name]=sha(tris)
  if o.name in NAMES:
   bm=bmesh.new();bm.from_mesh(o.data);raw_nonmanifold=sum(not e.is_manifold for e in bm.edges);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);qa.append({'object':o.name,'vertex_count_before_weld':len(o.data.vertices),'nonmanifold_before_weld':raw_nonmanifold,'nonmanifold_after_position_weld_1e_6':sum(not e.is_manifold for e in bm.edges),'degenerate_faces_after_weld':sum(f.calc_area()<1e-12 for f in bm.faces),'signed_volume_after_weld_local_units':bm.calc_volume(signed=True)});bm.free()
 return d,qa,verts
mi,mqa,mverts=imported(r/'hospital_recess_outline_C.glb');wi,wqa,wverts=imported(r/'hospital_recess_outline_C_white.glb')
report['glb_roundtrip']={'imported_material_mesh_count':len(mi),'imported_white_mesh_count':len(wi),'all_world_triangles_equal_rounded_1e_6':mi==wi,'material_targets':mqa,'white_targets':wqa}
# Actual candidate-to-reimported vertex set comparison in both directions, in world space.
bpy.ops.wm.open_mainfile(filepath=str(r/'hospital_recess_outline_C.blend'));distances={}
images=[{'name':im.name,'source':im.source,'packed':bool(im.packed_file),'size':list(im.size),'users':im.users} for im in bpy.data.images if im.users]
(r/'texture_dependency_qa.json').write_text(json.dumps({'images':images,'unpacked_external_used_images':[x['name'] for x in images if x['source']=='FILE' and not x['packed']]},ensure_ascii=False,indent=2))
assert all(x['packed'] for x in images if x['source']=='FILE')
for n in NAMES:
 o=bpy.data.objects[n];before=[o.matrix_world@v.co for v in o.data.vertices];after=[Vector(v) for v in mverts[n]]
 def haus(a,b):
  k=KDTree(len(b))
  for i,p in enumerate(b):k.insert(p,i)
  k.balance();return max(k.find(p)[2] for p in a)
 distances[n]=max(haus(before,after),haus(after,before))
report['glb_roundtrip']['target_bidirectional_world_vertex_max_distance']=distances
(r/'scope_and_roundtrip_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
assert report['only_target_meshes_changed'] and report['all_camera_states_equal'] and report['unaffected_meshes_byte_value_identical'] and report['target_transforms_materials_visibility_equal'] and report['materials_lights_world_collections_preserved'] and report['white_and_material_mesh_geometry_transforms_identical'] and mi==wi
assert all(q['nonmanifold_after_position_weld_1e_6']==0 and q['degenerate_faces_after_weld']==0 and q['signed_volume_after_weld_local_units']>0 for q in mqa+wqa)
assert max(distances.values())<1e-6
(r/'scope_and_roundtrip_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
