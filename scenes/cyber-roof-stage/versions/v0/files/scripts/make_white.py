import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r02.blend'))
s=bpy.context.scene
w=bpy.data.materials.new('White diagnostic');w.use_nodes=True;w.diffuse_color=(.66,.66,.66,1);b=w.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(.66,.66,.66,1);b.inputs['Roughness'].default_value=.7
geom={o.name:[len(o.data.vertices),len(o.data.polygons)] for o in s.objects if o.type=='MESH'}
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(w)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models/roof-r02-white.blend'))
assert geom=={o.name:[len(o.data.vertices),len(o.data.polygons)] for o in s.objects if o.type=='MESH'}
(P/'qa/material-white-mesh-counts.json').write_text(json.dumps(geom,indent=2))
