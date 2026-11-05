import bpy,bmesh,os,json,math
from mathutils import Vector
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));N=24;out={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=r+'/models/'+mode+'.blend');s=bpy.context.scene
 front=bpy.data.materials.new('UMBRELLA band proxy');front.use_nodes=True;bs=front.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.62;tex=front.node_tree.nodes.new('ShaderNodeTexImage');img=bpy.data.images.load(r+'/textures/umbrella-band-proxy.png',check_existing=True);img.pack();img.filepath='//../textures/umbrella-band-proxy.png';tex.image=img;tex.interpolation='Closest';tex.extension='EXTEND';uv=front.node_tree.nodes.new('ShaderNodeUVMap');uv.uv_map='UVMap';front.node_tree.links.new(uv.outputs['UV'],tex.inputs['Vector']);front.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);dark=bpy.data.materials.new('UMBRELLA dark underside proxy');dark.diffuse_color=(.015,.025,.055,1);dark.use_nodes=True;dark.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.015,.025,.055,1);dark.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.7
 records=[]
 for k in range(8):
  o=bpy.data.objects['U02 canopy segment '+str(k)];old=[v.co.copy() for v in o.data.vertices];assert len(old)==10;vs=[old[0],old[5]];rows={}
  for label,a,b in [('TO',1,2),('TI',6,7),('BO',4,3),('BI',9,8)]:
   ids=[]
   for j in range(N+1):
    t=j/N;q=old[a].lerp(old[b],t)
    if label in ['BO','BI']:q.z=old[1].z-(.035+.185*math.sin(math.pi*t)**2)
    ids.append(len(vs));vs.append(q)
   rows[label]=ids
  TO,TI,BO,BI=[rows[x] for x in ['TO','TI','BO','BI']];faces=[];slots=[]
  def face(v,mat):faces.append(tuple(v));slots.append(mat)
  for j in range(N):
   face([0,TO[j],TO[j+1]],0);face([1,TI[j+1],TI[j]],1);face([TO[j],BO[j],BO[j+1],TO[j+1]],0);face([TI[j],TI[j+1],BI[j+1],BI[j]],1);face([BO[j+1],BO[j],BI[j],BI[j+1]],1)
  face([TO[0],0,1,TI[0]],1);face([0,TO[-1],TI[-1],1],1);face([BO[0],TO[0],TI[0],BI[0]],1);face([TO[-1],BO[-1],BI[-1],TI[-1]],1)
  me=bpy.data.meshes.new(o.name+' scalloped skirt');me.from_pydata(vs,[],faces);me.update();o.data=me
  if mode=='white':
   w=bpy.data.materials['DIAGNOSTIC shared white'];me.materials.append(w);me.materials.append(w)
  else:me.materials.append(front);me.materials.append(dark)
  uvlay=me.uv_layers.new(name='UVMap')
  for poly,slot in zip(me.polygons,slots):
   poly.material_index=slot
   for li in poly.loop_indices:
    q=me.vertices[me.loops[li].vertex_index].co
    v=.8*(old[0].z-q.z)/(old[0].z-old[1].z) if q.z>=old[1].z-1e-6 else .8+(old[1].z-q.z)/.22*.2
    uvlay.data[li].uv=(.5,max(0,min(1,v)))
  b=bmesh.new();b.from_mesh(me);bmesh.ops.recalc_face_normals(b,faces=list(b.faces));b.to_mesh(me);b.free();me.calc_loop_triangles();areas=[((me.vertices[t.vertices[1]].co-me.vertices[t.vertices[0]].co).cross(me.vertices[t.vertices[2]].co-me.vertices[t.vertices[0]].co)).length/2 for t in me.loop_triangles];b=bmesh.new();b.from_mesh(me);rec={'object':o.name,'segments':N,'vertices':len(me.vertices),'faces':len(me.polygons),'nonmanifold':sum(not e.is_manifold for e in b.edges),'zero_triangles':sum(a<1e-12 for a in areas),'volume':b.calc_volume(signed=True),'six_original_roof_anchor_max_distance':max(min((v.co-old[i]).length for v in me.vertices) for i in [0,1,2,5,6,7]),'skirt_drop':{'at_seams':.035,'at_segment_midpoint':.22,'formula':'.035+.185*sin(pi*t)^2; inferred periodic extension, not source-measured'},'uv_layers':[x.name for x in me.uv_layers]};b.free();records.append(rec)
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=r+'/models/'+mode+'.blend');bpy.ops.export_scene.gltf(filepath=r+'/models/'+mode+'.glb',export_format='GLB',export_cameras=True,export_lights=False,export_image_format='AUTO');out[mode]=records
json.dump(out,open(r+'/qa/umbrella-r00-build.json','w'),indent=2);print('UMBRELLA_BUILD_COMPLETE')
