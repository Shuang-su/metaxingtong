import bpy,json,hashlib
from pathlib import Path
P=Path('/workspace/scratch/fa58bfcf0425/cyber-ring-emissive-band-study-20261105');O=Path(__file__).resolve().parent;f=P/'export/roof-led-surface-v2.blend';bpy.ops.wm.open_mainfile(filepath=str(f));o=bpy.data.objects['STAGE_OUTER LED front full circumference inferred'];m=o.data.materials[1];b=m.node_tree.nodes.get('Principled BSDF');d={'input_sha':hashlib.sha256(f.read_bytes()).hexdigest(),'strength':b.inputs['Emission Strength'].default_value,'images':[]}
for n in m.node_tree.nodes:
 if n.type=='TEX_IMAGE':d['images'].append({'name':n.image.name,'packed':bool(n.image.packed_file),'packed_sha':hashlib.sha256(n.image.packed_file.data).hexdigest(),'size':list(n.image.size)})
(O/'saved-v2-check.json').write_text(json.dumps(d,indent=2));print(d)
