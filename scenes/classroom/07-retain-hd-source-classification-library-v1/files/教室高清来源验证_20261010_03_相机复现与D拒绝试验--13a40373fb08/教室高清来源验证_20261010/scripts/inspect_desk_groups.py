import bpy,json
from pathlib import Path
names=['R2C1 rounded oak desktop','R3C2 rounded oak desktop'];r=[]
for n in names:
 o=bpy.data.objects[n];chain=[]
 while o:
  chain.append({'name':o.name,'type':o.type,'location':list(o.location),'children':len(o.children)});o=o.parent
 r.append(chain)
Path('/workspace/scratch/fa58bfcf0425/classroom_hd_alignment_20261010/qa/desk_parent_groups.json').write_text(json.dumps(r,indent=2))
