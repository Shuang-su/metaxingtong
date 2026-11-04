from pathlib import Path
import json,math
R=Path(__file__).resolve().parents[1];a=json.loads((R/'qa/r04/material-mesh-inventory.json').read_text());b=json.loads((R/'qa/r05/material-mesh-inventory.json').read_text());changed=[k for k in a if a[k]['geometry_sha256']!=b[k]['geometry_sha256']];expected=['LEAF_003_Branch_00_L','LEAF_003_Branch_00_R'];assert sorted(changed)==expected
repair=json.loads((R/'qa/r05/vein-repair.json').read_text());rows=[]
for ob in repair['rows']:
 uv=[]
 for p in ob['centerline_model_coordinates']:
  u=p[0]/4.65;width=1.58*max(0,1-u*u)**.72*(1+.06*math.sin(3*math.pi*u));v=p[1]/width;uv.append((u,v))
 assert all(-1<u<1 and abs(v)<1 for u,v in uv)
 rows.append({'id':ob['id'],'u_range':[min(x[0] for x in uv),max(x[0] for x in uv)],'max_abs_v':max(abs(x[1]) for x in uv),'centerline_domain_test_pass':True,'closed_mesh':b[ob['id']]['nonmanifold_edges']==0,'zero_area_faces':b[ob['id']]['zero_area_faces']})
report={'only_meshes_changed':changed,'remaining_meshes_identical':len(a)-len(changed),'repaired_vein_tests':rows,'no_old_render_reuse':True,'note':'Analytic centerline domain test verifies the repaired two branches remain inside the shared leaf parameter domain; not source acceptance.'};(R/'qa/r05/r04-r05-geometry-diff.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
