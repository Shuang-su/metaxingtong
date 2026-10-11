import bpy,sys,json,pathlib,numpy as np,subprocess,hashlib,time,os
P=pathlib.Path(__file__).resolve().parent
a=sys.argv[sys.argv.index('--')+1:];key=a[0]
sc=bpy.context.scene
cam={'main':'SOURCE_5586__01h33m06s','low':'SOURCE_2727__00h45m27s'}[key]
out=P/'renders'/key;out.mkdir(parents=True,exist_ok=True)
original={'engine':sc.render.engine,'samples':sc.cycles.samples,'use_denoising':sc.cycles.use_denoising,'use_compositing':sc.render.use_compositing,'use_nodes':sc.use_nodes,'resolution':[sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage]}
sc.camera=bpy.data.objects[cam]
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=32;sc.cycles.use_denoising=False;sc.cycles.use_adaptive_sampling=False;sc.cycles.seed=0
sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=1920;sc.render.resolution_y=1080;sc.render.resolution_percentage=100
sc.render.use_compositing=False;sc.render.use_sequencer=False
sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.image_settings.color_depth='8'
sc.render.filepath=str(out/'render_raw.png')
record={'view':key,'camera_name':cam,'camera_location':list(sc.camera.location),'camera_rotation_euler':list(sc.camera.rotation_euler),'camera_matrix_world':[list(r) for r in sc.camera.matrix_world],'lens_mm':sc.camera.data.lens,'sensor_width_mm':sc.camera.data.sensor_width,'sensor_fit':sc.camera.data.sensor_fit,'shift_x':sc.camera.data.shift_x,'shift_y':sc.camera.data.shift_y,'render_resolution':[1920,1080],'source_blend_sha256':hashlib.sha256(pathlib.Path(bpy.data.filepath).read_bytes()).hexdigest(),'geometry_material_lighting_changed':False,'original_settings':original,'run_settings':{'engine':'CYCLES','samples':32,'adaptive_sampling':False,'seed':0,'render_threads':2,'denoising':False,'compositing':False},'view_transform':sc.view_settings.view_transform,'look':sc.view_settings.look,'exposure':sc.view_settings.exposure,'gamma':sc.view_settings.gamma,'oidn':'OIDN2.5.1 RT HDR high CPU 2 threads; separate copy only; no image warp or camera refit','blender_version':bpy.app.version_string}
(out/'camera_render_manifest.json').write_text(json.dumps(record,indent=2))
bpy.ops.render.render(write_still=True)
sc.render.image_settings.file_format='OPEN_EXR';sc.render.image_settings.color_depth='32';sc.render.image_settings.exr_codec='ZIP';bpy.data.images['Render Result'].save_render(str(out/'render_raw_linear.exr'),scene=sc)
im=bpy.data.images.load(str(out/'render_raw_linear.exr'));w,h=im.size;pixels=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(pixels);pixels=pixels.reshape(h,w,4)[:,:,:3]
with open(out/'render_raw_linear.pfm','wb') as f:f.write(f'PF\n{w} {h}\n-1.0\n'.encode());f.write(np.asarray(pixels,dtype='<f4').tobytes())
subprocess.run([os.environ.get('OIDN_BIN',str(P.parent/'teahouse_v2/oidn/bin/oidnDenoise')),'--device','cpu','--filter','RT','--hdr',str(out/'render_raw_linear.pfm'),'--output',str(out/'render_oidn_linear.pfm'),'--quality','high','--threads','2'],check=True)
with open(out/'render_oidn_linear.pfm','rb') as f:
 assert f.readline().strip()==b'PF';dims=f.readline().split();scale=float(f.readline());arr=np.frombuffer(f.read(),dtype='<f4' if scale<0 else '>f4').reshape(h,w,3)
rgba=np.ones((h,w,4),dtype=np.float32);rgba[:,:,:3]=arr
den=bpy.data.images.new('OIDN_separate_copy',width=w,height=h,alpha=True,float_buffer=True);den.colorspace_settings.name='Linear Rec.709';den.pixels.foreach_set(rgba.ravel());den.update()
sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.image_settings.color_depth='8';den.save_render(str(out/'render_oidn.png'),scene=sc)
record['outputs']={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in out.glob('*') if p.suffix in ['.png','.exr','.pfm']};(out/'camera_render_manifest.json').write_text(json.dumps(record,indent=2));print('DONE',key)
