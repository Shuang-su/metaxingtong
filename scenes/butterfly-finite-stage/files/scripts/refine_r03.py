import bpy,bmesh,pathlib,json,math,ast
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
P=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'models/R02_material.blend'))
s=bpy.context.scene;s.cycles.use_denoising=False;s.cycles.samples=96
# Load only documented geometry helpers, never rerun/reset the R01 builder.
tree=ast.parse((P/'scripts/build_r01.py').read_text())
needed={'register','mesh','smooth','bow','unproj','uvpoint','shell','tube'}
mod=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in needed],type_ignores=[])
inventory=[];F=1500;W=1192;H=671
exec(compile(mod,'R01-geometry-functions-only','exec'))
# R01 hook outline locally crossed itself near (243,458). Rebuild the complete
# lower shells from a simple finite contour. This is a local silhouette revision,
# not deleting bad edges or silently changing source identity.
LL=[(590,410),(555,401),(519,389),(464,376),(408,374),(352,377),(300,390),(253,408),(225,430),(213,453),(216,469),(237,462),(249,449),(250,469),(231,489),(218,511),(221,542),(247,558),(283,570),(315,588),(346,613),(354,581),(387,585),(425,570),(460,551),(490,522),(520,488),(546,453),(568,425)]
for side,mir in [('L',False),('R',True)]:
 n=f'WING_{side}_LOWER_finite_outer_shell';o=bpy.data.objects[n];m=o.data.materials[0];bpy.data.objects.remove(o,do_unlink=True)
 old=bpy.data.objects[f'VEIN_{side}_LOWER_outer_boundary'];rm=old.data.materials[0];bpy.data.objects.remove(old,do_unlink=True)
 o,pts=shell(n,LL,m,0,.07,mir);tube(f'VEIN_{side}_LOWER_outer_boundary',[uvpoint(p,-.04) for p in pts],.035,rm,True)
 o['revision']='R03 local non-self-crossing hook contour; source silhouette still approximate'
# Retain a standalone clay datablock explicitly through save/load.
clay=bpy.data.materials.get('M99_neutral_white_clay')
if not clay:
 clay=bpy.data.materials.new('M99_neutral_white_clay');clay.diffuse_color=(.56,.56,.56,1);clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.56,.56,.56,1);bs.inputs['Roughness'].default_value=.6
clay.use_fake_user=True
s['revision']='R03 lower-hook topology repair; fixed-color PBR downgrade; finite foreground crop; source FAILED'
# Preflight must finish before any formal rendering.
qa=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  bm=bmesh.new();bm.from_mesh(o.data);bad=[e.index for e in bm.edges if not e.is_manifold];vol=bm.calc_volume(signed=True);qa.append({'object':o.name,'nonmanifold_edges':len(bad),'signed_volume':vol,'faces':len(bm.faces)});bm.free()
(P/'qa/R03-preflight.json').write_text(json.dumps(qa,indent=2))
assert not [r for r in qa if r['nonmanifold_edges'] or r['signed_volume']<=0], 'R03 preflight failed; do not export or render'
def save(tag):
 bpy.ops.wm.save_as_mainfile(filepath=str(P/f'models/R03_{tag}.blend'))
 bpy.ops.export_scene.gltf(filepath=str(P/f'models/R03_{tag}.glb'),export_format='GLB',export_cameras=True,export_lights=True,export_extras=True,export_apply=True)
save('material')
for o in bpy.data.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(clay)
save('white')
print('R03_PREFLIGHT_PASS',len(qa))
