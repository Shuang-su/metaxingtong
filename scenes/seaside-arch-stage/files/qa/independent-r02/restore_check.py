import bpy,json,pathlib,hashlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-seaside-r02-qa-20261105/frozen');Q=pathlib.Path(__file__).parent

def snap():
 s=bpy.context.scene
 return {'render':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.pixel_aspect_x,s.render.pixel_aspect_y,s.cycles.samples,s.cycles.use_denoising],'active':s.camera.name if s.camera else None,'world':{n.name:{'type':n.bl_idname,'inputs':{i.name:list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value for i in n.inputs if hasattr(i,'default_value')}}for n in s.world.node_tree.nodes},'links':sorted((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in s.world.node_tree.links),'lights':{o.name:{'matrix':[list(r)for r in o.matrix_world],'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'size':o.data.size,'shape':o.data.shape} for o in s.objects if o.type=='LIGHT'},'cameras':{o.name:{'matrix':[list(r)for r in o.matrix_world],'fit':o.data.sensor_fit,'lens':o.data.lens,'frame':[list(v.normalized())for v in o.data.view_frame(scene=s)]}for o in s.objects if o.type=='CAMERA'}}

for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/('models/'+mode+'.blend')));a=snap()
 script=(P/'scripts/restore.py').read_text().split("s.render.resolution_percentage=50;")[0]
 script=script.replace("mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'material'",'mode='+repr(mode)).replace("root+'/qa/restore-'+mode+'.json'",repr(str(Q))+"+'/producer-restore-'+mode+'.json'")
 exec(compile(script,str(P/'scripts/restore.py'),'exec'),{'__file__':str(P/'scripts/restore.py')});b=snap()
 bpy.ops.wm.save_as_mainfile(filepath=str(Q/('restored-'+mode+'.blend')))
 (Q/('restore-'+mode+'-check.json')).write_text(json.dumps({'baseline':a,'restored':b,'script_sha':hashlib.sha256((P/'scripts/restore.py').read_bytes()).hexdigest(),'notes':'Actual factory-empty import. Production output redirected; final low-render section excluded, snapshot before preview mutation. No rendering.'},indent=2))
print('DONE')
