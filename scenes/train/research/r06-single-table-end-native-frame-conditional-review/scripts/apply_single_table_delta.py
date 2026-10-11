"""Rebuild this diagnostic geometry from the verified r05C material or white BLEND.
Usage: blender -b --python apply_single_table_delta.py -- BASE.blend OUTPUT.blend
This rebuild does not claim binary identity with any historical model.
"""
import bpy,sys,json,hashlib
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];base=Path(args[0]).resolve();out=Path(args[1]).resolve();root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'candidate_manifest.json').read_text());ids=json.loads((root/'recovered_baseline_identity.json').read_text())['files'];allowed={x['sha256'] for x in ids if x['file'].endswith('.blend')};assert hashlib.sha256(base.read_bytes()).hexdigest() in allowed,'Base is not the recovered r05C source'
bpy.ops.wm.open_mainfile(filepath=str(base));obj=bpy.data.objects['Booth -1 1 rounded wood table'];assert len(obj.data.vertices)==len(manifest['before_vertices'])
for v,old in zip(obj.data.vertices,manifest['before_vertices']):assert max(abs(v.co[k]-old[k]) for k in range(3))<1e-6
for v,new in zip(obj.data.vertices,manifest['after_vertices']):v.co=new
obj.data.update();bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
