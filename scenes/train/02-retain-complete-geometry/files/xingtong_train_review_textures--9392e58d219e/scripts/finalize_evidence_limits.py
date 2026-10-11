import bpy,json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'deliverables'
def hashgeom(s):
 h=hashlib.sha256()
 for o in sorted([o for o in s.objects if o.type=='MESH'],key=lambda a:a.name):
  h.update(o.name.encode());h.update(struct.pack('<16f',*[v for row in o.matrix_world for v in row]));h.update(struct.pack('<%df'%(len(o.data.vertices)*3),*[a for v in o.data.vertices for a in v.co]));h.update(str([tuple(p.vertices) for p in o.data.polygons]).encode())
 return h.hexdigest()
checks={}
for bf,gf in [('01_train_material.blend','03_train_material.glb'),('02_train_white.blend','04_train_white.glb')]:
 bpy.ops.wm.open_mainfile(filepath=str(O/bf));s=bpy.context.scene;before=hashgeom(s)
 t=bpy.data.texts.get('README_中文') or bpy.data.texts.new('README_中文');t.clear();t.write((R/'README_中文.txt').read_text())
 s['Delivery_status']='Completed-space geometry version; precise source fitting NOT ACHIEVED.'
 s['Reference_alignment']='Precise source fit not achieved. A/B/D parameters are retained for honest comparison, not as proof of source-geometry correctness.'
 s['D_camera_fit']='Historical five-landmark camera estimate only. Significant seat-back-top, near-occlusion and overall-depth residuals remain; not accepted as a precise source fit.'
 s['Source_fit_status']='Significant residuals remain: D seat-back tops, near occlusion and overall depth; A foreground flowers/occlusion; B window/ceiling alignment. Sparse landmarks and preserved cameras do not establish a precise source fit.'
 s.cycles.use_denoising=False
 assert before==hashgeom(s);checks[bf]=before;bpy.ops.wm.save_as_mainfile(filepath=str(O/bf),compress=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in s.objects:
  if o.type in ['MESH','CAMERA']:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(O/gf),export_format='GLB',use_selection=True,export_apply=True,export_cameras=True,export_extras=True,export_materials='EXPORT')
assert len(set(checks.values()))==1
p=O/'verification.json';d=json.loads(p.read_text());d['delivery_status']='Completed-space geometry version; precise source fit NOT ACHIEVED.';d['geometry_completion_pass']=d['pass'];d['source_fit_pass']=False;d['pass_scope']='Geometry closure/support/circulation only; precise source matching is not achieved.';d['source_fit_residuals']={'D':'Significant seat-back-top, near-occlusion and overall-depth residuals.','A':'Substantial foreground flower and occlusion differences.','B':'Substantial window/ceiling alignment differences.'};d['final_metadata_only_geometry_hashes']=checks;p.write_text(json.dumps(d,indent=2));print('EVIDENCE_LIMITS_EMBEDDED_GEOMETRY_UNCHANGED',flush=True)
