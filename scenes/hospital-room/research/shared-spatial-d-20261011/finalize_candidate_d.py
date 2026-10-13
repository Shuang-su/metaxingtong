import bpy,bmesh,json,math,hashlib,numpy as np
from pathlib import Path
r=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath=str(r/'D2_screening.blend'));s=bpy.context.scene
# UV-only repair for inherited collapsed caps/edge UVs. Exact vertex and polygon arrays are invariant.
def geom_digest():
 return hashlib.sha256(repr([(o.name,[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons]) for o in s.objects if o.type=='MESH']).encode()).hexdigest()
before=geom_digest();records=[]
for o in s.objects:
 if o.type!='MESH':continue
 me=o.data;me.calc_loop_triangles()
 for uv in me.uv_layers:
  bad=set();density=[];zero=0
  for t in me.loop_triangles:
   xyz=np.array([o.matrix_world@me.vertices[i].co for i in t.vertices]);a=np.linalg.norm(np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]))/2
   u=np.array([uv.data[i].uv for i in t.loops]);b=abs(np.linalg.det(np.array([u[1]-u[0],u[2]-u[0]])))/2
   if a<1e-14:zero+=1;continue
   if b<1e-12:bad.add(t.polygon_index)
   else:density.append(math.sqrt(b/a))
  if not bad:continue
  scale=float(np.median(density)) if density else 1.;scale=max(.05,min(20.,scale));polys=[]
  for idx in sorted(bad):
   face=me.polygons[idx];loops=list(face.loop_indices);coords=np.array([o.matrix_world@me.vertices[me.loops[i].vertex_index].co for i in loops]);old=np.array([uv.data[i].uv for i in loops]);lut={li:i for i,li in enumerate(loops)};tris=[t for t in me.loop_triangles if t.polygon_index==idx]
   options=[]
   for ax in [(0,1),(0,2),(1,2)]:
    pp=coords[:,ax];areas=[]
    for t in tris:
     a=pp[[lut[i] for i in t.loops]];xyz=np.array([o.matrix_world@me.vertices[i].co for i in t.vertices])
     if np.linalg.norm(np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]))/2>1e-14:areas.append(abs(np.linalg.det(np.array([a[1]-a[0],a[2]-a[0]])))/2)
    options.append((min(areas) if areas else 0,pp))
   merit,proj=max(options,key=lambda a:a[0]);assert merit>1e-16,(o.name,idx,merit)
   out=(proj-proj.mean(0))*scale+old.mean(0)
   for i,co in zip(loops,out):uv.data[i].uv=co
   polys.append(idx)
  remaining=[]
  for t in me.loop_triangles:
   xyz=np.array([o.matrix_world@me.vertices[i].co for i in t.vertices]);a=np.linalg.norm(np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]))/2
   u=np.array([uv.data[i].uv for i in t.loops]);b=abs(np.linalg.det(np.array([u[1]-u[0],u[2]-u[0]])))/2
   if a>1e-14 and b<1e-12:remaining.append(t.polygon_index)
  records.append({'object':o.name,'layer':uv.name,'changed_polygons':polys,'uv_density':scale,'positive_area_triangles_with_collapsed_uv_after':len(remaining),'preexisting_zero_area_geometric_triangles_retained':zero});assert not remaining,(o.name,remaining)
after=geom_digest();assert before==after
(r/'uv_repair_qa.json').write_text(json.dumps({'method':'Only faces containing inherited positive-area 3D triangles with collapsed UV were reprojected on their best non-degenerate world planar axes; valid faces and all geometry preserved. Local UV centroid preserved; density inferred from existing valid triangles.','geometry_hash_before':before,'geometry_hash_after':after,'geometry_exactly_unchanged':True,'changed_meshes':len(set(x['object'] for x in records)),'records':records,'zero_area_geometry_policy':'Pre-existing zero-area geometric triangles retained to avoid opening closed mesh topology; separately counted, never treated as recovered surface area.'},ensure_ascii=False,indent=2))
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=16;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False;s.cycles.seed=0;s.render.threads_mode='FIXED';s.render.threads=2
for vl in s.view_layers:vl.cycles.use_denoising=False
s.camera=bpy.data.objects['MATCH_G_Sofa_And_Bed'];s['candidate_status']='D shared spatial candidate, source fidelity NOT accepted; H original camera unchanged';s['render_reference']='16 samples exactly, no adaptive sampling, no in-render denoising'
bpy.ops.wm.save_as_mainfile(filepath=str(r/'hospital_spatial_D.blend'));bpy.ops.export_scene.gltf(filepath=str(r/'hospital_spatial_D.glb'),export_format='GLB',use_selection=False)
m=bpy.data.materials.new('Diagnostic white - shared spatial D geometry');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.74,.74,.74,1);p.inputs['Roughness'].default_value=.8
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(m)
bpy.ops.wm.save_as_mainfile(filepath=str(r/'hospital_spatial_D_white.blend'));bpy.ops.export_scene.gltf(filepath=str(r/'hospital_spatial_D_white.glb'),export_format='GLB',use_selection=False)
print('UV repairs',len(records),'geometry invariant',before==after)
