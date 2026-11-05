import bpy,sys,os,json,hashlib,time
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mode=sys.argv[sys.argv.index('--')+1];p=root+'/models/'+mode+'.blend';bpy.ops.wm.open_mainfile(filepath=p)
s=bpy.context.scene;s.cycles.samples=32;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=6;s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100
sha=hashlib.sha256(open(p,'rb').read()).hexdigest();results=[]
for o in sorted((o for o in s.objects if o.type=='CAMERA'),key=lambda o:o.name):
 s.camera=o;out=root+'/renders/'+mode+'-'+o.name.split()[0]+'.png';s.render.filepath=out;start=time.time();bpy.ops.render.render(write_still=True);results.append({'camera':o.name,'path':os.path.relpath(out,root),'model_sha256':sha,'samples':32,'denoising':False,'resolution':[1192,671],'bytes':os.path.getsize(out),'sha256':hashlib.sha256(open(out,'rb').read()).hexdigest(),'seconds':time.time()-start})
 json.dump(results,open(root+'/qa/render-'+mode+'.json','w'),indent=2)
