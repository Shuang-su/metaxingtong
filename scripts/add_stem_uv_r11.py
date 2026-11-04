import bpy,pathlib,math,json,hashlib
R=pathlib.Path(__file__).resolve().parents[1];records=[]
for mode in ['material','white']:
 src=R/('models/R10_support-diagnostic_'+mode+'.blend');bpy.ops.wm.open_mainfile(filepath=str(src));rows=[]
 for ob in bpy.context.scene.objects:
  if not ob.name.endswith('_inferred_stems'):continue
  m=ob.data;uv=m.uv_layers.new(name='StemUV')
  for face in m.polygons:
   indices=list(face.vertices);group=indices[0]//16
   if any(i//16!=group for i in indices):raise RuntimeError('face crossed stem grouping')
   coords=[m.vertices[i].co for i in range(group*16,group*16+16)];cx=sum(v.x for v in coords)/16;cy=sum(v.y for v in coords)/16;z0=min(v.z for v in coords);z1=max(v.z for v in coords)
   if len(indices)==4:
    us=[(i%8)/8 for i in indices];seam=max(us)-min(us)>.5
    values=[((u+1 if seam and u<.5 else u),(m.vertices[i].co.z-z0)/(z1-z0)) for u,i in zip(us,indices)]
   else:values=[((m.vertices[i].co.x-cx)/.018+.5,(m.vertices[i].co.y-cy)/.018+.5) for i in indices]
   for loop,coord in zip(face.loop_indices,values):uv.data[loop].uv=coord
  if not all(math.isfinite(x) for t in uv.data for x in t.uv):raise RuntimeError('nonfinite UV')
  rows.append({'object':ob.name,'loops':len(uv.data),'uv_name':uv.name})
 dest=R/('models/R11_support-diagnostic_'+mode+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dest));bpy.ops.export_scene.gltf(filepath=str(dest.with_suffix('.glb')),export_format='GLB',export_apply=True,export_cameras=True)
 records.append({'mode':mode,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'meshes':rows})
(R/'qa/R11-stem-uv-addition.json').write_text(json.dumps({'change':'UV only on nine new inferred-stem groups; R10 raw geometry preserved; source acceptance still failed','records':records},indent=2))
