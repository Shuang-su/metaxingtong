"""Real BLEND and GLB checks; no approval inference. Blender background script."""
import bpy,bmesh,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];stage=sys.argv[-1] if sys.argv[-1].startswith('r') else 'r04';out=ROOT/'qa'/stage;models=ROOT/'models'/stage

def fingerprint(o):
 me=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh();coords=[tuple(round(c,6) for c in o.matrix_world@v.co) for v in me.vertices];faces=[tuple(p.vertices) for p in me.polygons]
 return hashlib.sha256(json.dumps([coords,faces],separators=(',',':')).encode()).hexdigest()
def bounds(o):
 pts=[o.matrix_world@Vector(p) for p in o.bound_box];return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
def mesh_report(o,merge=False):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 if merge:bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-4)
 report={'name':o.name,'id':o.get('evidence_id'),'verts':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True),'bounds':bounds(o)}
 bm.free();ev.to_mesh_clear();return report
bpy.ops.wm.open_mainfile(filepath=str(models/'piano_seaside_material.blend'))
objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];base={o.name:fingerprint(o) for o in objs};basebounds={o.name:bounds(o) for o in objs};reports=[mesh_report(o) for o in objs]
# Dense vertical ray check on modeled deck only. Gaps expected and counted.
deck=[o for o in objs if o.get('evidence_id')=='D01_deck' and 'plank' in o.name]
def hit_deck(x,y):
 for o in deck:
  inv=o.matrix_world.inverted();hit,p,n,idx=o.ray_cast(inv@Vector((x,y,1)),inv.to_3x3()@Vector((0,0,-1)))
  if hit:return float((o.matrix_world@p).z)
 return None
rays=[]
for i in range(51):
 for j in range(51):
  x=-3.55+i*7.1/50;y=-2.10+j*5.8/50;rays.append(hit_deck(x,y))
contacts=[]
for name,pt in [('piano rear caster',(-.31,2.08,0)),('piano front caster L',(-.61,.18,0)),('piano front caster R',(.61,.18,0))]+[(f'bench leg {x} {y}',(x,-1.02+y,0)) for x in [-.42,.42] for y in [-.16,.16]]:
 z=hit_deck(pt[0],pt[1]);contacts.append({'name':name,'point':pt,'deck_hit_z':z,'gap':None if z is None else pt[2]-z,'passes_0.005':z is not None and abs(pt[2]-z)<.005})
# Material topology and textures available in editable model.
materials={m.name:{'uses_nodes':m.use_nodes,'textures':[n.image.name for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m.use_nodes else []} for m in bpy.data.materials}
bpy.ops.wm.open_mainfile(filepath=str(models/'piano_seaside_white.blend'))
white={o.name:fingerprint(o) for o in bpy.context.scene.objects if o.type=='MESH'}
match=base==white
roundtrips={}
for kind in ['material','white']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(models/f'piano_seaside_{kind}.glb'))
 imported=[o for o in bpy.context.scene.objects if o.type=='MESH'];rr=[mesh_report(o,merge=True) for o in imported];bad_bounds=[]
 for o in imported:
  if o.name not in basebounds:bad_bounds.append({'name':o.name,'reason':'unmatched object'});continue
  err=max(abs(a-b) for aa,bb in zip(bounds(o),basebounds[o.name]) for a,b in zip(aa,bb))
  if err>1e-4:bad_bounds.append({'name':o.name,'max_abs_difference':err})
 roundtrips[kind]={'actual_imported':True,'seam_weld_tolerance_model_units':1e-4,'mesh_count':len(imported),'expected_mesh_count':len(base),'bounds_mismatches':bad_bounds,'nonmanifold_after_welding':[r for r in rr if r['nonmanifold_edges']],'zero_area_after_welding':[r for r in rr if r['zero_area_faces']],'negative_volume':[r for r in rr if r['signed_volume']<0],'sample_material_count':len(bpy.data.materials),'report':rr}
 bpy.ops.wm.save_as_mainfile(filepath=str(out/f'reimport_{kind}_diagnostic.blend'))
result={'stage':stage,'mesh_count':len(base),'material_white_evaluated_geometry_identical':match,'source_meshes':reports,'source_nonmanifold':[r for r in reports if r['nonmanifold_edges']],'source_zero_area':[r for r in reports if r['zero_area_faces']],'source_negative_volume':[r for r in reports if r['signed_volume']<0],'dense_deck_rays':{'count':len(rays),'hits':sum(z is not None for z in rays),'misses':sum(z is None for z in rays),'meaning':'sampling modeled planks only; seams and patch edge misses expected; not water/shore engineering validation'},'support_contacts':contacts,'materials':materials,'glb_roundtrips':roundtrips,'limitations':['No global self-intersection solve or structural engineering analysis.','Open sea and finite sand/deck boundaries are modeling extent, not verified real boundaries.','Manual cameras uncalibrated; source and material fidelity not passed.','Procedural shader components may not survive glTF; compare material render before claiming parity.']}
(out/'geometry-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['source_meshes','materials','glb_roundtrips']},indent=2))
print('GLB SUMMARY',json.dumps({k:{x:y for x,y in v.items() if x!='report'} for k,v in roundtrips.items()},indent=2))
