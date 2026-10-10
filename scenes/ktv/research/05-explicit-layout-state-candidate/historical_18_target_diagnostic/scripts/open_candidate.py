"""Open shared blend and apply an explicit or supported timeline state; never saves over the model.
blender --python open_candidate.py -- --workspace PATH --state furnished
blender --python open_candidate.py -- --workspace PATH --source-time 6630
"""
import bpy,sys,json,argparse,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from layout_states import choose_state,apply_layout
p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True);p.add_argument('--state',choices=['furnished','unfurnished']);p.add_argument('--source-time',type=float);p.add_argument('--log',type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);m=json.loads((root/'layout_state_manifest.json').read_text())
sid,selection=choose_state(m,a.state,a.source_time)
base=a.workspace/m['base_blend']['workspace_relative_path'];assert hashlib.sha256(base.read_bytes()).hexdigest()==m['base_blend']['sha256']
bpy.ops.wm.open_mainfile(filepath=str(base));log=apply_layout(bpy.context.scene,m,sid,selection)
log.update(base_blend_sha256=m['base_blend']['sha256'],model_saved=False,camera_selected_or_modified=False)
if a.log:a.log.write_text(json.dumps(log,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
print(json.dumps(log,ensure_ascii=False,allow_nan=False))
