import bpy,json,hashlib,array
R="/workspace/scratch/fa58bfcf0425/terrace_table_candidate_v2"
def snapshot(o):
 import array
 h=hashlib.sha256()
 d={'matrix':[list(r) for r in o.matrix_world], 'hide':[o.hide_render,o.hide_viewport], 'data':o.data.name if o.data else None,'mods':[(m.name,m.type) for m in o.modifiers]}
 if o.type=='MESH':
  d['materials']=[m.name if m else None for m in o.data.materials]
  for coll,prop,count,typ in [(o.data.vertices,'co',len(o.data.vertices)*3,'f'),(o.data.loops,'vertex_index',len(o.data.loops),'i'),(o.data.polygons,'loop_total',len(o.data.polygons),'i')]:
   ar=array.array(typ,[0])*count;coll.foreach_get(prop,ar);h.update(ar.tobytes())
  for l in o.data.uv_layers:
   ar=array.array('f',[0])*(len(l.data)*2);l.data.foreach_get('uv',ar);h.update(ar.tobytes())
 if o.type=='CAMERA': d['parameters']={k:getattr(o.data,k) for k in ['type','lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','clip_start','clip_end','ortho_scale']}
 if o.type=='LIGHT': d['parameters']={k:(list(getattr(o.data,k)) if k=='color' else getattr(o.data,k)) for k in ['type','energy','color','use_shadow','shadow_soft_size','size','angle'] if hasattr(o.data,k)}
 h.update(json.dumps(d,sort_keys=True).encode());return h.hexdigest()

def mats():
 out={}
 for m in bpy.data.materials:
  nodes=[];links=[]
  if m.use_nodes:
   for n in m.node_tree.nodes:
    props={p.identifier:(list(getattr(n,p.identifier)) if getattr(p,'is_array',False) else getattr(n,p.identifier)) for p in n.bl_rna.properties if p.type not in ['COLLECTION','POINTER'] and p.identifier not in ['select','location','dimensions']}
    inputs=[(i.name,(list(i.default_value) if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else i.default_value)) for i in n.inputs if hasattr(i,'default_value')]
    nodes.append([n.name,props,inputs,n.image.name if hasattr(n,'image') and n.image else None])
   links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]
  out[m.name]=hashlib.sha256(json.dumps([list(m.diffuse_color),m.use_nodes,nodes,links],sort_keys=True,default=str).encode()).hexdigest()
 return out
before={o.name:snapshot(o) for o in bpy.data.objects};mb=mats()
bpy.ops.wm.open_mainfile(filepath=R+'/Terrace_T3_RosetteTips_Candidate.blend')
after={o.name:snapshot(o) for o in bpy.data.objects};ma=mats();removed=set(before)-set(after);changed=[n for n in before.keys()&after.keys() if before[n]!=after[n]];mat_changed=[n for n in mb if n not in ma or mb[n]!=ma[n]]
assert not changed,changed
assert not mat_changed,mat_changed
json.dump({'baseline':'Oct11 original blend','candidate':'Terrace_T3_RosetteTips_Candidate.blend','preserved_object_count':len(before.keys()&after.keys()),'changed_retained_objects':changed,'removed_decorations':sorted(removed),'added_decorations':sorted(set(after)-set(before)),'original_materials_checked':len(mb),'changed_original_materials':mat_changed,'camera_and_light_data_included':True},open(R+'/T3_independent_freeze_check.json','w'),indent=2)
print('VERIFIED_FREEZE',len(before.keys()&after.keys()),len(mb),flush=True)
