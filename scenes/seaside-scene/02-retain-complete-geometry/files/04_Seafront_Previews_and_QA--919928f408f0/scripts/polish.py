import bpy,math
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/seaside_scene_fullscene'
for v in ['Textured','White']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/Seafront_'+v+'.blend');S=bpy.context.scene;cam=bpy.data.objects['QA10_地形背侧'];cam.location=(90,34,16);cam.rotation_euler=(Vector((42,60,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=32
 terrain=bpy.data.objects['Undulating_coastal_land_slope']
 for i,vtx in enumerate(terrain.data.vertices):
  idx=i%2628
  if idx%18==0:
   ss=-85+(idx//18)*3.3;der=-.00044*max(ss-38,0);fac=math.sqrt(1+der*der);vtx.co.x=-.00022*max(ss-38,0)**2+4.835/fac;vtx.co.y=ss-4.835*der/fac
 S['reconstruction']='Editable relative-unit geometry; no survey scale; no camera-dependent geometry or visibility.'
 bpy.ops.wm.save_as_mainfile(filepath=R+'/models/Seafront_'+v+'.blend',compress=True)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in S.objects:
  if ob.type=='MESH':ob.select_set(True)
 bpy.ops.export_scene.gltf(filepath=R+'/models/Seafront_'+v+'.glb',export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
 if v=='Textured':
  nt=S.world.node_tree;nt.nodes.clear();bg=nt.nodes.new('ShaderNodeBackground');bg.inputs[0].default_value=(.38,.44,.52,1);bg.inputs[1].default_value=.65;out=nt.nodes.new('ShaderNodeOutputWorld');nt.links.new(bg.outputs[0],out.inputs[0])
  for o in S.objects:
   if o.type=='LIGHT':
    if o.data.type=='SUN':o.data.energy=2.3;o.data.color=(1,.93,.83);o.rotation_euler=(.55,-.5,-.5)
    else:o.data.energy=0
  for cam in sorted([ob for ob in S.objects if ob.type=='CAMERA' and ob.name.startswith('QA')],key=lambda ob:ob.name):
   S.camera=cam;S.render.resolution_x=960;S.render.resolution_y=600;S.render.filepath=R+'/renders/'+cam.name+'.png';bpy.ops.render.render(write_still=True)
print('POLISH_COMPLETE')
