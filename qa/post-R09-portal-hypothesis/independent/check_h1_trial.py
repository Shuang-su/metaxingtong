import bpy,bmesh,pathlib,hashlib,json
P=pathlib.Path('/workspace/scratch/fa58bfcf0425');Q=P/'independent-observatory-portal-semantic-qa-20261105';f=P/'observatory-candidate-20261104/models/R09_material.blend';bpy.ops.wm.open_mainfile(filepath=str(f))
def snap():return {o.name:([tuple(v.co)for v in o.data.vertices],[tuple(p.vertices)for p in o.data.polygons],[list(r)for r in o.matrix_world])for o in bpy.context.scene.objects if o.type=='MESH'}
def audit(o):
 b=bmesh.new();b.from_mesh(o.data);r={'nonmanifold':sum(not e.is_manifold for e in b.edges),'degenerate':sum(f.calc_area()<1e-12 for f in b.faces),'volume':b.calc_volume(signed=True)};b.free();return r
A=snap();o=bpy.data.objects['DOOR_00_upper'];R={'base_sha':hashlib.sha256(f.read_bytes()).hexdigest(),'before_topology':audit(o),'changes':[]}
for v in o.data.vertices:
 if v.co.z<5.49:
  old=list(v.co);v.co.z+=1.2;R['changes'].append({'index':v.index,'before':old,'after':list(v.co)})
o.data.update();bpy.context.view_layer.update();B=snap();R['changed_mesh']=[n for n in A if A[n]!=B[n]];R['after_topology']=audit(o);R['faces_unchanged']=A[o.name][1]==B[o.name][1];R['matrix_unchanged']=A[o.name][2]==B[o.name][2];R['after_sha']=hashlib.sha256(f.read_bytes()).hexdigest();recs=json.loads((P/'observatory-portal-plane-diagnostic-20261105/trial-records.json').read_text());R['recorded_changes_exact']=R['changes']==recs[1]['changes'];R['images']=[{'path':x['path'],'hash_matches':hashlib.sha256(pathlib.Path(x['path']).read_bytes()).hexdigest()==x['sha256'],'bytes_matches':pathlib.Path(x['path']).stat().st_size==x['bytes'],'base_matches':x['base_model_sha256']==R['base_sha']}for x in recs];(Q/'H1-independent-check.json').write_text(json.dumps(R,indent=2));print({k:v for k,v in R.items()if k!='changes'})
