import bpy,json,pathlib,hashlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/cyber-roof-cloud-r06-20261105');Q=pathlib.Path(__file__).parent

def snap():
 s=bpy.context.scene
 return {'render':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.pixel_aspect_x,s.render.pixel_aspect_y,s.cycles.samples,s.cycles.use_denoising],'active':s.camera.name if s.camera else None,'world':{n.name:{'type':n.bl_idname,'inputs':{i.name:list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value for i in n.inputs if hasattr(i,'default_value')}}for n in s.world.node_tree.nodes},'links':sorted((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in s.world.node_tree.links),'lights':{o.name:{'matrix':[list(r)for r in o.matrix_world],'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'size':o.data.size,'shape':o.data.shape} for o in s.objects if o.type=='LIGHT'},'cameras':{o.name:{'matrix':[list(r)for r in o.matrix_world],'fit':o.data.sensor_fit,'lens':o.data.lens,'frame':[list(v.normalized())for v in o.data.view_frame(scene=s)]}for o in s.objects if o.type=='CAMERA'}}
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r06b-experiment.blend'));a=snap();bpy.ops.wm.read_factory_settings(use_empty=True)
script=(P/'scripts/restore_r06b_glb.py').read_text().replace("str(P/'qa/restored-r06b-from-glb.blend')",repr(str(Q/'restored-from-glb.blend')))
exec(compile(script,str(P/'scripts/restore_r06b_glb.py'),'exec'),{'__file__':str(P/'scripts/restore_r06b_glb.py')});b=snap()
(Q/'restore-check.json').write_text(json.dumps({'baseline':a,'restored':b,'script_sha':hashlib.sha256((P/'scripts/restore_r06b_glb.py').read_bytes()).hexdigest(),'notes':'Actual factory-empty import, output only redirected. No rendering.'},indent=2));print('DONE')
