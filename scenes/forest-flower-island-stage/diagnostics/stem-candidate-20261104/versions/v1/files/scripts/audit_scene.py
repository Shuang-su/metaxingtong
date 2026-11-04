"""Technical inventory, not source-geometry acceptance. Run inside Blender."""
import bpy,bmesh,sys,pathlib,argparse,json,hashlib,struct,math
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]); dg=bpy.context.evaluated_depsgraph_get()
report={'file':bpy.data.filepath,'sha256':hashlib.sha256(pathlib.Path(bpy.data.filepath).read_bytes()).hexdigest(),'meshes':[],'cameras':[],'images':[],'source_acceptance':False,'limits':['per-mesh topology is not scene intersection, contact, airtightness or source agreement proof','evaluated geometry includes active modifiers','signed volume only meaningful for closed consistently wound mesh']}
for ob in sorted(bpy.context.scene.objects,key=lambda x:x.name):
 if ob.type=='MESH':
  ev=ob.evaluated_get(dg);m=ev.to_mesh();world=[tuple(ob.matrix_world@v.co) for v in m.vertices];faces=[tuple(p.vertices) for p in m.polygons]
  blob=b''.join(struct.pack('<3d',*v) for v in world)+b''.join(struct.pack('<I',len(f))+struct.pack('<'+'I'*len(f),*f) for f in faces)
  bm=bmesh.new();bm.from_mesh(m);bm.transform(ob.matrix_world);bm.normal_update()
  report['meshes'].append(dict(name=ob.name,vertices=len(world),faces=len(faces),world_geometry_sha256=hashlib.sha256(blob).hexdigest(),boundary_edges=sum(e.is_boundary for e in bm.edges),nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),degenerate_faces=sum(f.calc_area()<1e-12 for f in bm.faces),signed_volume=bm.calc_volume(signed=True),bounds=[[min(v[i] for v in world),max(v[i] for v in world)] for i in range(3)] if world else None,hide_render=ob.hide_render,hide_viewport=ob.hide_viewport,materials=[s.material.name if s.material else None for s in ob.material_slots],inference=ob.get('inference','not recorded')))
  bm.free();ev.to_mesh_clear()
 elif ob.type=='CAMERA':report['cameras'].append(dict(name=ob.name,matrix=[list(r) for r in ob.matrix_world],lens=ob.data.lens,sensor_width=ob.data.sensor_width,sensor_height=ob.data.sensor_height,sensor_fit=ob.data.sensor_fit,shift=[ob.data.shift_x,ob.data.shift_y]))
for im in bpy.data.images:report['images'].append(dict(name=im.name,source=im.source,path=im.filepath,packed=bool(im.packed_file),size=list(im.size),has_data=im.has_data))
report['mesh_count']=len(report['meshes']);report['camera_count']=len(report['cameras'])
pathlib.Path(a.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('AUDIT',report['mesh_count'],report['camera_count'])
