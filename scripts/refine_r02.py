import bpy,bmesh,pathlib,json,math
P=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'models/R01_material.blend'))
s=bpy.context.scene;s.cycles.use_denoising=False;s.cycles.samples=64
# Remove unsupported procedural texture connections for honest fixed-color GLB parity.
for m in bpy.data.materials:
 if m.use_nodes:
  nt=m.node_tree;p=nt.nodes.get('Principled BSDF')
  if p:
   for link in list(p.inputs['Base Color'].links):nt.links.remove(link)
   p.inputs['Base Color'].default_value=m.diffuse_color
   for n in list(nt.nodes):
    if n.type in ['TEX_NOISE','VALTORGB']:nt.nodes.remove(n)
# The R01 ellipse incorrectly ended before the visible foreground in camera 05.
# Replace it with a finite cropped slab reaching the observed foreground. All unseen
# edges and bottom are explicitly inferred, NOT the stage's real full footprint.
o=bpy.data.objects['STAGE_finite_reflective_oval'];o.name='STAGE_finite_foreground_crop_inferred_boundaries'
vs=[(x,y,z) for z in [.37,.49] for y in [-12,3.1] for x in [-19,19]]
fs=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
d=bpy.data.meshes.new(o.name);d.from_pydata(vs,[],fs);d.update();old=o.data;m=old.materials[0];o.data=d;d.materials.append(m)
o['source_evidence']='report-02/05 reflective foreground continues beyond pale curved band; original full footprint unobserved'
o['inferred']='finite crop extent, all outer boundaries and bottom thickness; not original footprint'
bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
# Save fixed-color originals and fresh GLBs; never overwrite R01.
s['revision']='R02 foreground finite crop and glTF-compatible fixed colors; all source correspondence still FAILED'
def save(tag):
 bpy.ops.wm.save_as_mainfile(filepath=str(P/f'models/R02_{tag}.blend'))
 bpy.ops.export_scene.gltf(filepath=str(P/f'models/R02_{tag}.glb'),export_format='GLB',export_cameras=True,export_lights=True,export_extras=True,export_apply=True)
save('material')
for o in bpy.data.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(bpy.data.materials['M99_neutral_white_clay'])
save('white')
