import bpy,math,json
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/seaside_scene_fullscene'
changes=[]
for variant in ['Textured','White']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/Seafront_'+variant+'.blend');S=bpy.context.scene;S.view_layers[0].update()
 for span,j,block in [(69,15,70)]+[(i,j,b) for i in range(70,74) for j,b in [(0,i),(15,i+1)]]:
  o=bpy.data.objects[f'Chain_span_{span:02d}_link_{j:02d}'];b=bpy.data.objects[f'Coastal_block_{block:02d}'];center=sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices);bc=sum((b.matrix_world@v.co for v in b.data.vertices),Vector())/len(b.data.vertices);delta=(bc-center).normalized()*.005
  if not o.get('final_anchor_contact_fix'):
   o.location+=delta;o['final_anchor_contact_fix']='end ring translated0.005 toward block';changes.append({'variant':variant,'object':o.name,'delta':list(delta)})
 terrain=bpy.data.objects['Undulating_coastal_land_slope']
 for i,v in enumerate(terrain.data.vertices):
  idx=i%2628
  if idx%18==0:
   ss=-85+(idx//18)*3.3;der=-.00044*max(ss-38,0);fac=math.sqrt(1+der*der);v.co.x=-.00022*max(ss-38,0)**2+4.835/fac;v.co.y=ss-4.835*der/fac
 cam=bpy.data.objects['QA10_地形背侧'];cam.location=(90,34,16);cam.rotation_euler=(Vector((42,60,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=32
 S['chain_note']='Static interlocking rings; tiny surface penetrations permitted; not a mechanical simulation.'
 S['reconstruction']='Editable relative-unit geometry, no measured meter scale or camera-dependent geometry.'
 S.camera=bpy.data.objects['Camera_B_reference_6435'];S.render.resolution_x=1188;S.render.resolution_y=668;S.cycles.samples=16;S.cycles.use_denoising=False;S.render.threads_mode='FIXED';S.render.threads=2
 bpy.ops.wm.save_as_mainfile(filepath=R+'/models/Seafront_'+variant+'.blend',compress=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in S.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=R+'/models/Seafront_'+variant+'.glb',export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
 for n in ['Camera_A_reference_6170','Camera_B_reference_6435','Camera_C_side_6310']:
  S.camera=bpy.data.objects[n];S.render.filepath=R+'/renders/'+variant+'_Camera_'+n.removeprefix('Camera_')+'.png';bpy.ops.render.render(write_still=True)
 if variant=='Textured':
  nt=S.world.node_tree;nt.nodes.clear();bg=nt.nodes.new('ShaderNodeBackground');bg.inputs[0].default_value=(.38,.44,.52,1);bg.inputs[1].default_value=.65;out=nt.nodes.new('ShaderNodeOutputWorld');nt.links.new(bg.outputs[0],out.inputs[0])
  for o in S.objects:
   if o.type=='LIGHT':
    if o.data.type=='SUN':o.data.energy=2.3;o.data.color=(1,.93,.83);o.rotation_euler=(.55,-.5,-.5)
    else:o.data.energy=0
  for c in sorted([o for o in S.objects if o.type=='CAMERA' and o.name.startswith('QA')],key=lambda o:o.name):
   S.camera=c;S.render.resolution_x=960;S.render.resolution_y=600;S.render.filepath=R+'/renders/'+c.name+'.png';bpy.ops.render.render(write_still=True)
json.dump(changes,open(R+'/qa/end_anchor_corrections.json','w'),indent=2)
print('ANCHOR_FINAL_COMPLETE')
