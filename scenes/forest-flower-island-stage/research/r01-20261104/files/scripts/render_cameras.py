"""Render explicit cameras using the saved shared scene; never changes visibility or geometry."""
import bpy,sys,argparse,pathlib,json,hashlib,datetime
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--cameras',nargs='+',required=True);p.add_argument('--samples',type=int,default=16);p.add_argument('--threads',type=int,default=4);p.add_argument('--percentage',type=int,default=100)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=bpy.context.scene
out=pathlib.Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
s.render.engine='CYCLES';s.cycles.samples=a.samples;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=a.threads;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.resolution_percentage=a.percentage
for name in a.cameras:
 c=bpy.data.objects[name];assert c.type=='CAMERA';s.camera=c
 s.render.resolution_x=int(c.get('source_width',1280));s.render.resolution_y=int(c.get('source_height',720))
 dest=out/(name+'.png');s.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
 data=dest.read_bytes();meta=dict(camera=name,model=bpy.data.filepath,model_sha256=hashlib.sha256(pathlib.Path(bpy.data.filepath).read_bytes()).hexdigest(),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),denoising=False,samples=a.samples,resolution_percentage=a.percentage,rendered_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),camera_matrix=[list(row) for row in c.matrix_world],lens=c.data.lens,sensor_width=c.data.sensor_width)
 dest.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
