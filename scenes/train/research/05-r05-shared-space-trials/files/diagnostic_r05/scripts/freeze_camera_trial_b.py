import bpy,json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];m=json.loads((R/'analysis/trial_manifest.json').read_text());p=Path(m['file']);assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256'];bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene
fit=json.loads((R/'analysis/seat_contour_refined_fit.json').read_text())['shared_head_and_rack_height']
def gh():
 h=hashlib.sha256()
 for o in sorted((o for o in s.objects if o.type=='MESH'),key=lambda o:o.name):
  h.update(o.name.encode())
  for v in o.data.vertices:
   p=o.matrix_world@v.co;h.update(struct.pack('<3f',*p))
 return h.hexdigest()
before=gh()
for k in ['A','B','D']:
 c=fit['cameras'][k]['camera'];o=bpy.data.objects['R05_HD_'+k];o.location=c[:3];o.rotation_euler=c[3:6];o.data.lens=c[6]
s['Candidate_status']='r05 trialB; shared geometry same as e5a57046551d; D nearest two seats reindexed one bay nearer; source precision still NOT passed.'
out=R/'trial_b_shared.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out));h=hashlib.sha256(out.read_bytes()).hexdigest();dest=R/f'trial_b_shared_{h[:12]}.blend';out.rename(dest);dest.chmod(0o444);assert before==gh();data={**m,'file':str(dest),'sha256':h,'parent_geometry_trial':m['sha256'],'geometry_vertex_hash':before,'geometry_unchanged_from_trial_a':True,'camera_evidence':'seat_contour_refined_fit.json; source landmarks corrected from original unscaled crops; D near=-3.72 and mid=-1.92 hypothesis','status':'frozen review trial, not final reconstruction'};(R/'analysis/trial_b_manifest.json').write_text(json.dumps(data,indent=2));print(dest,h,before)
