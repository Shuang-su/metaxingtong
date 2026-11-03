import bpy,json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parents[1];out=[]
for mode in ['material','white']:
 p=D/f'models/R08_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(p))
 out.append({'model':str(p.relative_to(D)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'images':[{'name':i.name,'source':i.source,'filepath':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images],'libraries':[l.filepath for l in bpy.data.libraries],'fonts':[{'name':f.name,'filepath':f.filepath,'packed':bool(f.packed_file)} for f in bpy.data.fonts]})
(D/'qa/R08-external-dependencies.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
