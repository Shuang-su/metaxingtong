import bpy,pathlib,json,hashlib
p=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104/models/R07_material.blend');q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-source15-qa-20261104');bpy.ops.wm.open_mainfile(filepath=str(p));r={}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 v=[o.matrix_world@p.co for p in o.data.vertices];r[o.name]={'bounds':[[min(p[i] for p in v),max(p[i] for p in v)]for i in range(3)],'vertices':len(v),'faces':len(o.data.polygons)}
(q/'actual-model.json').write_text(json.dumps({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'objects':r},indent=2));print('DONE')
