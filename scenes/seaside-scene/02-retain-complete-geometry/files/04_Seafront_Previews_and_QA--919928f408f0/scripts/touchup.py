import bpy,bmesh,os,math
R='/workspace/scratch/fa58bfcf0425/seaside_scene_fullscene'
for variant in ['Textured','White']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/Seafront_'+variant+'.blend');S=bpy.context.scene
 o=bpy.data.objects['Inferred_finite_roadbed_core']
 for v in o.data.vertices:
  if v.co.z<-.5:v.co.z=-4.9
 terrain=bpy.data.objects['Undulating_coastal_land_slope']
 for i,v in enumerate(terrain.data.vertices):
  idx=i%2628
  if idx%18==0:
   ss=-85+(idx//18)*3.3;der=-.00044*max(ss-38,0);fac=math.sqrt(1+der*der);v.co.x-=.065/fac;v.co.y+=.065*der/fac
 # Floor bottoms no longer coplanar in intersections; do not remove source surfaces.
 for n in ['Inferred_finite_roadbed_core','Continuous_rocky_seawall_slope','Undulating_coastal_land_slope','Two_way_road_7m20','Promenade_2m25','Inland_walk_1m10','Curb_top','Curb_top.001']:
  o=bpy.data.objects.get(n)
  if not o:continue
  me=o.data;me.update();uv=me.uv_layers.active
  for p in me.polygons:
   if abs(p.normal.z)>.8:continue
   axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
   for li,vi in zip(p.loop_indices,p.vertices):uv.data[li].uv=(me.vertices[vi].co[axes[0]]/3,me.vertices[vi].co[axes[1]]/3)
 S['reconstruction']='Editable relative-unit geometry; no survey scale, no camera-dependent geometry or visibility.'
 S['underside_note']='路基底 -4.9 与岸坡/陆坡底 -4.8 错层，避免共面闪烁；该断面完全推断。'
 bpy.data.orphans_purge(do_recursive=True)
 bpy.ops.wm.save_as_mainfile(filepath=R+'/models/Seafront_'+variant+'.blend',compress=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in S.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=R+'/models/Seafront_'+variant+'.glb',export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
 if variant=='Textured':
  # Re-render ordinary views with neutral proof lights following UV/underside correction.
  nt=S.world.node_tree;nt.nodes.clear();bg=nt.nodes.new('ShaderNodeBackground');bg.inputs[0].default_value=(.38,.44,.52,1);bg.inputs[1].default_value=.65;out=nt.nodes.new('ShaderNodeOutputWorld');nt.links.new(bg.outputs[0],out.inputs[0])
  for o in S.objects:
   if o.type=='LIGHT':
    if o.data.type=='SUN':o.data.energy=2.3;o.data.color=(1,.93,.83);o.rotation_euler=(.55,-.5,-.5)
    else:o.data.energy=0
  for c in sorted([o for o in S.objects if o.type=='CAMERA' and o.name.startswith('QA')],key=lambda o:o.name):
   S.camera=c;S.render.resolution_x=960;S.render.resolution_y=600;S.render.filepath=R+'/renders/'+c.name+'.png';bpy.ops.render.render(write_still=True)
print('TOUCHUP_COMPLETE')
