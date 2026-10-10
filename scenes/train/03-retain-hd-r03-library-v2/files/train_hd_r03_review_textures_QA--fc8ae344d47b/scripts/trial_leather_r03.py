import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];src=next(x for x in json.loads((R/'frozen_r02/freeze_manifest.json').read_text())['blends'] if x['kind']=='material');bpy.ops.wm.open_mainfile(filepath=src['file'])
m=bpy.data.materials['Dark forest green leather | authored UV PBR'];b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Specular IOR Level'].default_value=.35
for n in m.node_tree.nodes:
 if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.08
for o in bpy.context.scene.objects:
 if o.type=='MESH' and 'high back' in o.name:
  for uv in o.data.uv_layers.active.data:uv.uv*=3
  o['HD_r03_UV']='Higher shared leather frequency on newly rebuilt high-back body (3x); tuft panel UV unchanged.'
bpy.context.scene['HD_r03_material']='Normal strength .08; new high-back UV frequency 3x, specular .35. Geometry, camera and global lighting identical to r02.'
p=R/'trial_r03/train_hd_r03_material_trial.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);h=hashlib.sha256(p.read_bytes()).hexdigest();q=p.with_name('train_hd_r03_material_'+h[:12]+'.blend');p.rename(q);q.chmod(0o444);(R/'trial_r03/freeze_manifest.json').write_text(json.dumps({'blends':[{'kind':'material','file':str(q),'sha256':h,'bytes':q.stat().st_size}]},indent=2))
