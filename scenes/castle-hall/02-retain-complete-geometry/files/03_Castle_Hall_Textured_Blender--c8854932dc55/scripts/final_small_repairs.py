import bpy,bmesh
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/Xingtong_Castle_Hall_FullRoom.blend'));S=bpy.context.scene
# Concealed mounting spacers physically bridge each observed wall sconce to the completed wall.
col=bpy.data.collections['12_Physical_Support_Repairs'];ma=bpy.data.materials['AntiqueGold | original UV PBR']
for side in (-1,1):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(side*4.8,21.975,4.45));o=bpy.context.object;o.name='Candelabra concealed wall mounting spacer';o.dimensions=(.14,.20,.48);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.data.materials.append(ma);o['evidence']='Inferred mechanical support behind source-visible wall sconce.'
# One real weight per tether cluster, remove exact duplicated overlapping weights.
seen=set()
for o in list(S.objects):
 if o.type=='MESH' and o.name.startswith('Balloon anchor weight'):
  key=tuple(round(sum(v.co[i] for v in o.data.vertices)/len(o.data.vertices),4) for i in range(3))
  if key in seen:bpy.data.objects.remove(o,do_unlink=True)
  else:seen.add(key)
S['GeometryCompletion']='Bounded 14 x 34 x 8.8 model-unit interior, solid floor/wall/roof, physical window and entry apertures with returns. All camera-independent. Proportions inferred, not measured.'
S['Scale']='Arbitrary model units with inferred scale; Blender and glTF nominal unit conventions do not establish physical measurements.'
for t in bpy.data.texts:
 if t.name.startswith('READ_ME_'):t.write('\nScale clarification: all dimension values are model units with inferred proportions, not measured metres.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/Xingtong_Castle_Hall_FullRoom.blend'),compress=True)
