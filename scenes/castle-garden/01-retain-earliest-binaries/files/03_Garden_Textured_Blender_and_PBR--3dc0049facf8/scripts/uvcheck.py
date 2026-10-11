import bpy,os,hashlib,json
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));d={}
for k in ['White','Textured']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/Xingtong_Castle_Garden_'+k+'.blend');h=hashlib.sha256();count=0
 for o in sorted(bpy.context.scene.objects,key=lambda o:o.name):
  if o.type!='MESH':continue
  h.update(o.name.encode());count+=1
  for v in o.data.vertices:h.update(repr(tuple(v.co)).encode())
  for uv in o.data.uv_layers:
   for x in uv.data:h.update(repr(tuple(x.uv)).encode())
 d[k]={'mesh_count':count,'geometry_and_uv_sha256':h.hexdigest()}
d['PASS']=d['White']==d['Textured'];json.dump(d,open(R+'/qa/variant_uv_validation.json','w'),indent=2)
