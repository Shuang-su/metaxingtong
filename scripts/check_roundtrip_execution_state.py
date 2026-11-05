import bpy,json,pathlib
P=pathlib.Path(__file__).resolve().parents[1]
def props(x):
 out={}
 for p in x.bl_rna.properties:
  if p.identifier in ['rna_type'] or p.type not in ['BOOLEAN','INT','FLOAT','STRING','ENUM']:continue
  try:
   v=getattr(x,p.identifier)
   if isinstance(v,(bool,int,float,str)):out[p.identifier]=v
   else:out[p.identifier]=list(v)
  except:pass
 return out
states={}
for tag,path in [('original','models/R04_material.blend'),('roundtrip','qa/independent-R04D/restored/R04D_material_restored.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(P/path));s=bpy.context.scene
 # Apply only the recorded execution overrides shared by the two render scripts.
 s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.samples=96;s.cycles.use_denoising=False;s.render.resolution_percentage=100
 if tag=='original':s.camera=bpy.data.objects['SOURCE02_conditional_front']
 b=s.world.node_tree.nodes.get('Background')
 states[tag]={'cycles':props(s.cycles),'render':props(s.render),'image_settings':props(s.render.image_settings),'view_settings':props(s.view_settings),'display':props(s.display),'camera':props(s.camera.data),'camera_matrix':[list(r) for r in s.camera.matrix_world],'world_background':{'color':list(b.inputs['Color'].default_value),'strength':b.inputs['Strength'].default_value},'compositing_use_nodes':s.use_nodes,'film_transparent':s.render.film_transparent}
diff=[]
for group in states['original']:
 a=states['original'][group];b=states['roundtrip'][group]
 if isinstance(a,dict):
  for k in set(a)|set(b):
   if a.get(k)!=b.get(k):diff.append({'group':group,'property':k,'original':a.get(k),'roundtrip':b.get(k)})
 elif a!=b:diff.append({'group':group,'original':a,'roundtrip':b})
out={'timing':'Post-hoc read of frozen input scenes with their recorded identical execution overrides, NOT fabricated runtime instrumentation','states':states,'differences':diff,'interpretation':'Differences are image-level roundtrip behavior, not isolated material error. Exact relevant state and remaining float/name/structural differences must be considered. SOURCE FAILED remains unchanged.'}
(P/'qa/R04D-roundtrip-render/execution-state-posthoc.json').write_text(json.dumps(out,indent=2));print(json.dumps(diff,indent=2))
