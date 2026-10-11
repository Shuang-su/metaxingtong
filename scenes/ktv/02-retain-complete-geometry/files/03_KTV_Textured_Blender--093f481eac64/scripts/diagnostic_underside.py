import bpy
R='/workspace/scratch/fa58bfcf0425/ktv_fullroom/delivery'
bpy.ops.wm.open_mainfile(filepath=R+'/models/KTV_Complete_Open_Stage_White.blend');sc=bpy.context.scene
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.6,.6,.6,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.8
sc.camera=bpy.data.objects['10_underside'];sc.render.filepath=R+'/renders/14_DIAGNOSTIC_UNDERSIDE_white.png';bpy.ops.render.render(write_still=True)
# Lighting-only diagnostic. Geometry unchanged, source-fit renders untouched, native files not overwritten.
