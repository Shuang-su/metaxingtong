import bpy,bmesh,json,math,hashlib
from pathlib import Path
r=Path(__file__).parent;base=r.parent/'candidate_b/hospital_endboard_shape_B.blend'
bpy.ops.wm.open_mainfile(filepath=str(base))
NAMES=['Bed end • moulded central recess','Bed end • cream inset face']
report={'candidate':'C outline only, inherited relief sign unverified','base_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'method':'Rounded capsule YZ outline, original X thickness circular bevel retained; object matrices and XYZ bounds preserved','source_evidence':'F continuous rounded top contour; G visible left semicircular end with short upper/lower edges; exact radius unmeasured','objects':[]}
for name in NAMES:
 o=bpy.data.objects[name];old=o.data
 lo=[min(v.co[i] for v in old.vertices) for i in range(3)];hi=[max(v.co[i] for v in old.vertices) for i in range(3)];center=[(a+b)/2 for a,b in zip(lo,hi)];a,w,h=[(b-a)/2 for a,b in zip(lo,hi)]
 verts=[];faces=[];n_arc=32;n_bevel=6
 for j in range(n_bevel+1):
  t=-math.pi/2+math.pi*j/n_bevel;x=center[0]+a*math.sin(t);radius=h-a*(1-math.cos(t));yc=w-h
  for side,start in [(1,-math.pi/2),(-1,math.pi/2)]:
   for k in range(n_arc+1):
    ang=start+math.pi*k/n_arc;verts.append((x,center[1]+side*yc+radius*math.cos(ang),center[2]+radius*math.sin(ang)))
 L=2*(n_arc+1)
 for j in range(n_bevel):
  for i in range(L):faces.append((j*L+i,j*L+(i+1)%L,(j+1)*L+(i+1)%L,(j+1)*L+i))
 faces+=[tuple(range(L-1,-1,-1)),tuple(n_bevel*L+i for i in range(L))]
 mesh=bpy.data.meshes.new(old.name+' C capsule contour');mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);q={'name':name,'local_bounds_before':[lo,hi],'local_bounds_after':[[min(v.co[i] for v in mesh.vertices) for i in range(3)],[max(v.co[i] for v in mesh.vertices) for i in range(3)]],'world_radius_candidate':h*o.scale.z,'world_thickness_preserved':2*a*o.scale.x,'arc_segments_per_semicircle':n_arc,'bevel_intervals_front_to_back':n_bevel,'vertex_count':len(bm.verts),'face_count':len(bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'signed_local_volume':bm.calc_volume(signed=True),'mesh_validate_modified':mesh.validate(verbose=True)};bm.free()
 assert q['nonmanifold_edges']==0 and q['degenerate_faces']==0 and q['signed_local_volume']>0 and not q['mesh_validate_modified']
 assert max(abs(x-y) for A,B in zip(q['local_bounds_before'],q['local_bounds_after']) for x,y in zip(A,B))<1e-7
 for mat in old.materials:mesh.materials.append(mat)
 # Retain old UV field through the topology change instead of silently dropping the layer.
 donor=bpy.data.objects.new('Temporary original UV donor',old);bpy.context.scene.collection.objects.link(donor);donor.matrix_world=o.matrix_world.copy();o.data=mesh
 for uv in old.uv_layers:mesh.uv_layers.new(name=uv.name)
 before=[tuple(v.co) for v in mesh.vertices]
 if old.uv_layers:
  bpy.context.view_layer.objects.active=o;o.select_set(True);mod=o.modifiers.new('Transfer original UV surface field','DATA_TRANSFER');mod.object=donor;mod.use_loop_data=True;mod.data_types_loops={'UV'};mod.loop_mapping='POLYINTERP_NEAREST';mod.layers_uv_select_src='ALL';mod.layers_uv_select_dst='NAME';bpy.ops.object.modifier_apply(modifier=mod.name)
 assert before==[tuple(v.co) for v in o.data.vertices]
 q['uv_layers_before']=list(old.uv_layers.keys());q['uv_layers_after']=list(o.data.uv_layers.keys());q['uv_transfer']='Blender DATA_TRANSFER POLYINTERP_NEAREST, per-corner interpolation from original B surface';q['uv_transfer_changes_geometry']=False
 q['uv_ranges']={uv.name:[[min(d.uv[i] for d in uv.data),max(d.uv[i] for d in uv.data)] for i in range(2)] for uv in o.data.uv_layers}
 assert q['uv_layers_before']==q['uv_layers_after'] and all(b>a for ranges in q['uv_ranges'].values() for a,b in ranges)
 bpy.data.objects.remove(donor,do_unlink=True);report['objects'].append(q)
# Save scene at original B camera/render settings, with no new cameras, lights, materials or changes to other objects.
bpy.ops.wm.save_as_mainfile(filepath=str(r/'hospital_recess_outline_C.blend'))
bpy.ops.export_scene.gltf(filepath=str(r/'hospital_recess_outline_C.glb'),export_format='GLB',use_selection=False)
# White is a material-only derivative of C, same as existing B white convention.
m=bpy.data.materials.new('Diagnostic white - shared C outline geometry');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.74,.74,.74,1);p.inputs['Roughness'].default_value=.8
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(m)
bpy.ops.wm.save_as_mainfile(filepath=str(r/'hospital_recess_outline_C_white.blend'))
bpy.ops.export_scene.gltf(filepath=str(r/'hospital_recess_outline_C_white.glb'),export_format='GLB',use_selection=False)
(r/'geometry_construction_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
