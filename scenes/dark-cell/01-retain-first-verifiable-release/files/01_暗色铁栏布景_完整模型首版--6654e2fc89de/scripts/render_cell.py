import bpy,sys,json
R='/workspace/scratch/fa58bfcf0425/dark_cell_v1';typ,view=sys.argv[sys.argv.index('--')+1:];bpy.ops.wm.open_mainfile(filepath=R+'/models/dark_cell_'+typ+'.blend');S=bpy.context.scene;S.camera=bpy.data.objects[view];S.cycles.use_denoising=False;S.cycles.samples=32
if view=='12_剖切诊断':
 # Diagnostic cut only. Exported deliverables remain complete.
 for o in list(S.objects):
  if o.type=='MESH' and o.name in ['推定_厚顶板','推定_右墙','推定_前墙左','推定_前墙右','推定_入口过梁']:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.wm.save_as_mainfile(filepath=R+'/qa/剖切诊断_不作完整模型.blend')
if view in ['09_外部前右','10_外部背面','11_底面','12_剖切诊断']:
 S.world.use_nodes=True;S.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.45,.5,.6,1);S.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.7
S.render.filepath=R+'/renders/'+view+'_'+typ+'.png';bpy.ops.render.render(write_still=True)
