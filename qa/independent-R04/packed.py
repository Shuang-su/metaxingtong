import bpy,json,hashlib
from pathlib import Path
P=Path('/workspace/scratch/fa58bfcf0425/butterfly-finite-stage-20261105');O=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/R04_material.blend'));rows=[]
for im in bpy.data.images:
 if im.packed_file:
  b=bytes(im.packed_file.data);f=O/'packed-generated-region.png';f.write_bytes(b);rows.append({'name':im.name,'bytes':len(b),'sha':hashlib.sha256(b).hexdigest(),'size':list(im.size),'colorspace':im.colorspace_settings.name})
(O/'packed.json').write_text(json.dumps(rows,indent=2))
