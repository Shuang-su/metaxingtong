import bpy,numpy as np,json,hashlib
from pathlib import Path
R=Path('/workspace/scratch/fa58bfcf0425/bedroom_hd_revision_20261010')
def digest(a):return hashlib.sha256(a.tobytes()).hexdigest()
def socket(sock):
 if not sock.is_linked:
  try:return {'constant':list(sock.default_value)}
  except:return {'constant':float(sock.default_value)}
 link=sock.links[0];node=link.from_node;channel=link.from_socket.name
 if node.type=='TEX_IMAGE':
  ar=np.empty(len(node.image.pixels),np.float32);node.image.pixels.foreach_get(ar);ar=ar.reshape(-1,4)
  return {'texture_rgb':digest(ar[:,:3].copy()),'red':digest(ar[:,0].copy()),'green':digest(ar[:,1].copy()),'blue':digest(ar[:,2].copy()),'size':list(node.image.size),'colorspace':node.image.colorspace_settings.name}
 return {'node':node.type,'output':channel,'inputs':{i.name:socket(i) for i in node.inputs if i.is_linked or i.name in ['Strength']}}
def snap():
 out={}
 for m in bpy.data.materials:
  if not m.use_nodes:continue
  p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if p:out[m.name]={key:socket(p.inputs[key]) for key in ['Base Color','Metallic','Roughness','Normal','Emission Color','Emission Strength','Transmission Weight']}
 return out
bpy.ops.wm.open_mainfile(filepath=str(R/'models/hd_v2/01_HD_candidate_material.blend'));a=snap();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'models/hd_v2/03_HD_candidate_material.glb'));b=snap();(R/'independent_qa/shader_semantics.json').write_text(json.dumps({'source':a,'import':b},indent=2))
