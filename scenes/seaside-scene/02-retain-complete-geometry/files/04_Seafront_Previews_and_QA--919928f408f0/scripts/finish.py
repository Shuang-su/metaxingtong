import bpy,bmesh,math,os,json
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/seaside_scene_fullscene'
bpy.ops.wm.open_mainfile(filepath=R+'/source/models/Seafront_Textured.blend')
lights={o.name:{'rotation':tuple(o.rotation_euler),'energy':o.data.energy,'color':tuple(o.data.color)} for o in bpy.data.objects if o.type=='LIGHT'}
bpy.ops.wm.open_mainfile(filepath=R+'/models/Seafront_Textured.blend');S=bpy.context.scene
with bpy.data.libraries.load(R+'/source/models/Seafront_Textured.blend',link=False) as (src,dst):dst.worlds=src.worlds
sunset=dst.worlds[0]
for o in list(S.objects):
 if o.type!='MESH':continue
 if o.name.startswith('Chain_'):
  old=o.data;points=[sum((old.vertices[i*5+j].co for j in range(5)),Vector())/5 for i in range(12)];plane=(points[1]-points[0]).cross(points[2]-points[1]).normalized();vs=[];fs=[]
  for i,p in enumerate(points):
   tangent=(points[(i+1)%12]-points[(i-1)%12]).normalized();rad=tangent.cross(plane).normalized()
   for j in range(5):vs.append(tuple(p+.013*(math.cos(j*2*math.pi/5)*rad+math.sin(j*2*math.pi/5)*plane)))
  for i in range(12):
   for j in range(5):fs.append((i*5+j,i*5+(j+1)%5,((i+1)%12)*5+(j+1)%5,((i+1)%12)*5+j))
  me=bpy.data.meshes.new(o.name+'_periodic');me.from_pydata(vs,[],fs);me.materials.clear()
  for m in old.materials:me.materials.append(m)
  o.data=me;me.uv_layers.new(name='UVMap')
  for p in me.polygons:
   p.use_smooth=True
   for li,vi in zip(p.loop_indices,p.vertices):me.uv_layers.active.data[li].uv=(vi%5/5,vi//5/12)
  o['completion']='周期闭合管环替换旧端部错位开缝；链条相对布置未改'
 if o.name.startswith('Shore_side_yellow_stripe'):
  mod=o.modifiers.new('Paint thickness','SOLIDIFY');mod.thickness=.005;mod.offset=-1;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 bm=bmesh.new();bm.from_mesh(o.data)
 if 'emissive_diffuser' in o.name:
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
# Exact curving roadbed edges, using same longitudinal parameter as original ribbons.
o=bpy.data.objects['Inferred_finite_roadbed_core'];N=1292
for i,v in enumerate(o.data.vertices):
 idx=i%N;s=-95+idx//2;off=-6 if idx%2==0 else 4.85;d=-.00044*max(s-38,0);norm=Vector((1,-d,0)).normalized();v.co=(-.00022*max(s-38,0)**2+off*norm.x,s+off*norm.y,-.45 if i<N else -4.8)
# Thin vertical seams between exact neighboring regions are filled by slab intersections, not camera masks.
core=[o for o in S.objects if o.type=='MESH']
def export(name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in core:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=R+'/models/'+name+'.glb',export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
S.cycles.samples=16;S.cycles.use_denoising=False;S.render.threads_mode='FIXED';S.render.threads=2
# Ordinary views use neutral proof lighting, same mesh set as final sunset model.
for c in sorted([o for o in S.objects if o.type=='CAMERA' and o.name.startswith('QA')],key=lambda o:o.name):
 S.camera=c;S.render.resolution_x=960;S.render.resolution_y=600;S.render.filepath=R+'/renders/'+c.name+'.png';bpy.ops.render.render(write_still=True)
S.world=sunset
for n,v in lights.items():
 o=bpy.data.objects.get(n)
 if o:o.rotation_euler=v['rotation'];o.data.energy=v['energy'];o.data.color=v['color']
S['quality_note']='源图仅360p播放截图；保留原创程序夕阳。10张普通几何检查使用中性照明，几何和可见集合完全一致。'
S['format_difference']='GLB包含所有核心网格/贴图；不包含Blender程序环境与照明，相同拓扑。'
S.camera=bpy.data.objects['Camera_B_reference_6435'];S.render.resolution_x=1188;S.render.resolution_y=668
bpy.ops.wm.save_as_mainfile(filepath=R+'/models/Seafront_Textured.blend',compress=True);export('Seafront_Textured')
for n in ['Camera_A_reference_6170','Camera_B_reference_6435','Camera_C_side_6310']:
 S.camera=bpy.data.objects[n];S.render.filepath=R+'/renders/Textured_'+n+'.png';bpy.ops.render.render(write_still=True)
white=bpy.data.materials.get('QA_白模') or bpy.data.materials.new('QA_白模');white.diffuse_color=(.7,.7,.7,1);white.use_nodes=True;white.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.7,.7,.7,1)
for o in core:o.data.materials.clear();o.data.materials.append(white)
w=bpy.data.worlds.new('Neutral_white_QA');w.use_nodes=True;w.node_tree.nodes.get('Background').inputs[0].default_value=(.45,.45,.45,1);w.node_tree.nodes.get('Background').inputs[1].default_value=.65;S.world=w
for o in S.objects:
 if o.type=='LIGHT':
  if o.data.type=='SUN':o.rotation_euler=(.55,-.5,-.5);o.data.energy=2.3;o.data.color=(1,1,1)
  else:o.data.energy=0
S.camera=bpy.data.objects['Camera_B_reference_6435'];bpy.ops.wm.save_as_mainfile(filepath=R+'/models/Seafront_White.blend',compress=True);export('Seafront_White')
for n in ['Camera_A_reference_6170','Camera_B_reference_6435','Camera_C_side_6310']:
 S.camera=bpy.data.objects[n];S.render.filepath=R+'/renders/White_'+n+'.png';bpy.ops.render.render(write_still=True)
print('FINAL_RENDER_COMPLETE')
