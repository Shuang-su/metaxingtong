import bpy,json,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent.parent;bpy.ops.wm.open_mainfile(filepath=str(P.parent/'cyber-roof-stage-20261105/models/roof-r05.blend'));scan=json.loads((P/'results/taper-only-scan.json').read_text());rows=[]
for h in scan['h_values']:
 out={'h':h,'objects':[]}
 for o in bpy.context.scene.objects:
  if not o.name.startswith('ROOF_MAIN'):continue
  a=np.array([list(o.matrix_world@v.co) for v in o.data.vertices]);t=np.clip(np.abs((a[:,1]-5.5)/3),0,1);b=a.copy();b[:,0]*=(h+(1-h)*t)/(.74+.26*t);delta=np.linalg.norm(b-a,axis=1);ix=int(np.argmax(delta))
  ee=np.array([(e.vertices[0],e.vertices[1]) for e in o.data.edges]);la=np.linalg.norm(a[ee[:,0]]-a[ee[:,1]],axis=1);lb=np.linalg.norm(b[ee[:,0]]-b[ee[:,1]],axis=1)
  q={'object':o.name,'max_vertex_displacement':float(delta[ix]),'max_displacement_vertex':ix,'world_before':a[ix].tolist(),'world_after':b[ix].tolist(),'max_yz_displacement':float(np.abs((b-a)[:,1:]).max()),'t_clamped_range':[float(t.min()),float(t.max())],'edge_length_ratio_range':[float((lb/la).min()),float((lb/la).max())]}
  if o.name=='ROOF_MAIN closed shell':
   N=len(a)//2;da=np.linalg.norm(a[N:]-a[:N],axis=1);db=np.linalg.norm(b[N:]-b[:N],axis=1);q['shell_solidify_index_pair_distances']={'assumption':'first and second halves use preserved solidify vertex pairing; diagnostic, not arbitrary nearest face thickness','count':N,'original_minmax':[float(da.min()),float(da.max())],'new_minmax':[float(db.min()),float(db.max())],'maximum_absolute_length_change':float(np.abs(db-da).max())}
  out['objects'].append(q)
 rows.append(out)
(P/'results/taper-object-displacements.json').write_text(json.dumps({'not_applied':True,'units':'model units, not physical meters','field':scan['hypothesis'],'rows':rows},indent=2))
