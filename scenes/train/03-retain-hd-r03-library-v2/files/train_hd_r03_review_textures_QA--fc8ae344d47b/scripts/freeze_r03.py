import bpy,json,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];src=json.loads((R/'trial_r03/freeze_manifest.json').read_text())['blends'][0];p=Path(src['file']);h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==src['sha256'];q=R/'frozen_r03'/p.name;shutil.copy2(p,q);q.chmod(0o444);rows=[{'kind':'material','file':str(q),'sha256':h,'bytes':q.stat().st_size}]
bpy.ops.wm.open_mainfile(filepath=str(q));s=bpy.context.scene;w=bpy.data.materials.new('White matte inspection material r03');w.use_nodes=True;b=w.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.66,.66,.66,1);b.inputs['Roughness'].default_value=.82
for o in s.objects:
 if o.type=='MESH' and not any('glazing' in m.name.lower() for m in o.data.materials if m):o.data.materials.clear();o.data.materials.append(w)
 if o.type=='LIGHT':o.data.color=(1,1,1)
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.1,.1,.1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.12;s.view_settings.exposure=-.15;s['Version']='r03 white, exact same final complete geometry and UV as material';bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
p=R/'frozen_r03/train_hd_r03_white_temp.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);h=hashlib.sha256(p.read_bytes()).hexdigest();q=p.with_name('train_hd_r03_white_'+h[:12]+'.blend');p.rename(q);q.chmod(0o444);rows.append({'kind':'white','file':str(q),'sha256':h,'bytes':q.stat().st_size})
(R/'frozen_r03/freeze_manifest.json').write_text(json.dumps({'status':'immutable final candidate inputs; pending fidelity review','blends':rows},indent=2))
for i in rows:
 dst=R/'deliverables'/('01_train_material.blend' if i['kind']=='material' else '02_train_white.blend');shutil.copyfile(i['file'],dst);assert hashlib.sha256(dst.read_bytes()).hexdigest()==i['sha256']
print(json.dumps(rows,indent=2))
