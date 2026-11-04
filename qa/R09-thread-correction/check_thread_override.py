import bpy,pathlib,json,sys
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-mannequin-qa-20261104')
def snap_rna(ob):
 out={}
 for p in ob.bl_rna.properties:
  n=p.identifier
  if n in ['rna_type','filepath','file_extension']:continue
  if p.type in ['BOOLEAN','INT','FLOAT','STRING','ENUM']:
   v=getattr(ob,n)
   if isinstance(v,set):v=sorted(v)
   elif getattr(p,'is_array',False):v=list(v)
   out[n]=v
 return out
R={}
for mode in ['material','white']:
 D={}
 for ver in ['R06','R07']:
  bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'{ver}_{mode}.blend'));s=bpy.context.scene
  if ver=='R06':
   s.camera=bpy.data.objects['MANNEQUIN_local'];s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=False;s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=6
  D[ver]={'render':snap_rna(s.render),'image_settings':snap_rna(s.render.image_settings),'cycles':snap_rna(s.cycles),'view_settings':snap_rna(s.view_settings),'display_settings':snap_rna(s.display_settings),'world_name':s.world.name,'camera':s.camera.name,'frame':[s.frame_current,s.frame_subframe],'use_nodes':s.use_nodes}
 R[mode]={'states':D,'equal':D['R06']==D['R07'],'differences':{k:{x:[D['R06'][k].get(x),D['R07'][k].get(x)] for x in set(D['R06'][k])|set(D['R07'][k]) if D['R06'][k].get(x)!=D['R07'][k].get(x)}for k in D['R06'] if isinstance(D['R06'][k],dict) and D['R06'][k]!=D['R07'][k]}}
(Q/('R07-thread-override-'+sys.argv[-1]+'.json')).write_text(json.dumps(R,indent=2));print({k: {'equal':v['equal'],'differences':v['differences']} for k,v in R.items()})
