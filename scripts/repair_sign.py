import bpy,bmesh,os,json
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));report={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=r+'/models/'+mode+'.blend');items=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or not o.name.startswith('SIGN_'):continue
  b=bmesh.new();b.from_mesh(o.data);before=[len(b.verts),len(b.faces),sum(not e.is_manifold for e in b.edges)];bmesh.ops.remove_doubles(b,verts=list(b.verts),dist=.00001);bmesh.ops.dissolve_degenerate(b,dist=.000001,edges=list(b.edges));bmesh.ops.recalc_face_normals(b,faces=list(b.faces));items.append({'name':o.name,'before_v_f_nonmanifold':before,'after_v_f_nonmanifold':[len(b.verts),len(b.faces),sum(not e.is_manifold for e in b.edges)],'zeroarea':sum(f.calc_area()<1e-12 for f in b.faces),'volume':b.calc_volume(signed=True)});b.to_mesh(o.data);b.free()
 bpy.ops.wm.save_as_mainfile(filepath=r+'/models/'+mode+'.blend');bpy.ops.export_scene.gltf(filepath=r+'/models/'+mode+'.glb',export_format='GLB',export_cameras=True,export_lights=False);report[mode]=items
json.dump(report,open(r+'/qa/sign-repair-r01.json','w'),indent=2);print(report)
