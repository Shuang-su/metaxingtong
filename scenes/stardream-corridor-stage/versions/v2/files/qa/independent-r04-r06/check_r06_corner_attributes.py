import bpy,pathlib,json,math
from mathutils.kdtree import KDTree
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/stardream-corridor-20261105/models');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-corridor-qa-20261105')
def snap():
 out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  me=o.data;nm=o.matrix_world.to_3x3().inverted().transposed();uv=me.uv_layers.active
  out[o.name]=[(o.matrix_world@me.vertices[l.vertex_index].co,(nm@me.corner_normals[l.index].vector).normalized(),tuple(uv.data[l.index].uv) if uv else None) for l in me.loops]
 return out
def compare(a,b):
 kd=KDTree(len(b))
 for i,x in enumerate(b):kd.insert(x[0],i)
 kd.balance();worst=[0.,0.,0.];missing=0
 for pos,n,uv in a:
  candidates=kd.find_range(pos,2e-5)
  if not candidates:missing+=1;continue
  vals=[]
  for _,i,d in candidates:
   q,m,v=b[i];ne=(n-m).length;ue=max(abs(x-y) for x,y in zip(uv,v)) if uv is not None and v is not None else (0 if uv==v else 999)
   vals.append((max(ne,ue),d,ne,ue))
  _,d,ne,ue=min(vals)
  for k,x in enumerate([d,ne,ue]):worst[k]=max(worst[k],x)
 return {'missing_position_candidates':missing,'max_position':worst[0],'max_corner_normal_vector':worst[1],'max_corner_uv':worst[2]}
out={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/f'R06_{mode}.blend'));a=snap();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(P/f'R06_{mode}.glb'));b=snap();out[mode]={n:{'forward':compare(x,b[n]),'reverse':compare(b[n],x)} for n,x in a.items()}
(Q/'R06-corner-attributes.json').write_text(json.dumps(out,indent=2));print('DONE')
