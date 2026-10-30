"""Actual GLB imports, unchanged white geometry, lamp rays, diagnostic renders."""
import bpy,bmesh,json,hashlib,sys,math,ast
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];Q=R/'qa/r11';M=R/'models/r11'
module=ast.parse((R/'scripts/validate_scene.py').read_text());exec(compile(ast.Module(body=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name in ['bounds','mesh_report']],type_ignores=[]),'read_only_geometry_functions','exec'),globals())
def geometry_fingerprint():
 out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  me=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh();out[o.name]=hashlib.sha256(json.dumps({'v':[list(o.matrix_world@v.co) for v in me.vertices],'p':[list(p.vertices) for p in me.polygons]},separators=(',',':')).encode()).hexdigest();o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
 return out
bpy.ops.wm.open_mainfile(filepath=str(M/'piano_seaside_material.blend'));s=bpy.context.scene;base=geometry_fingerprint();bb={o.name:bounds(o) for o in s.objects if o.type=='MESH'};rays=[];dg=bpy.context.evaluated_depsgraph_get()
for o in s.objects:
 if o.type!='LIGHT' or o.data.type!='POINT' or o.get('evidence_id') not in ['L01_lantern','L02_lantern']:continue
 for direction in [(0,0,1),(1,0,0),(0,-1,0)]:
  hit,p,n,i,obj,mat=s.ray_cast(dg,o.location,Vector(direction),distance=2);rays.append({'light':o.name,'direction':direction,'first_hit':obj.name if hit else None,'not_inside_bulb':not hit or 'internal emitter' not in obj.name})
assert all(a['not_inside_bulb'] for a in rays)
bpy.ops.wm.open_mainfile(filepath=str(M/'piano_seaside_white.blend'));white=geometry_fingerprint();assert base==white
roundtrips={}
for kind in ['material','white']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(M/f'piano_seaside_{kind}.glb'));objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objs)==len(base)==614;rr=[mesh_report(o,merge=True) for o in objs];mismatches=[]
 for o in objs:
  if o.name not in bb:mismatches.append({'name':o.name,'unmatched':True});continue
  err=max(abs(x-y) for a,b in zip(bounds(o),bb[o.name]) for x,y in zip(a,b))
  if err>1e-4:mismatches.append({'name':o.name,'error':err})
 bad={'bounds':mismatches,'nonmanifold':[r['name'] for r in rr if r['nonmanifold_edges']],'zero_area':[r['name'] for r in rr if r['zero_area_faces']],'negative_volume':[r['name'] for r in rr if r['signed_volume']<0]};assert not any(bad.values()),bad
 roundtrips[kind]={'actual_imported':True,'mesh_count':len(objs),'weld_tolerance':1e-4,'failures':bad,'material_count':len(bpy.data.materials)}
(Q/'glb-and-lamp-checks.json').write_text(json.dumps({'geometry_identical_material_white':base==white,'mesh_count':len(base),'point_rays':rays,'GLB':roundtrips,'limitation':'numeric candidate checks only. No source acceptance. Area lamps and World are BLEND-only; retained for the following export material render.'},indent=2)+'\n')
# Actual material roundtrip render in the original lighting and world, explicitly.
bpy.ops.wm.open_mainfile(filepath=str(M/'piano_seaside_material.blend'));s=bpy.context.scene
for o in list(s.objects):
 if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(M/'piano_seaside_material.glb'));s.camera=bpy.data.objects['main'];s.render.filepath=str(Q/'glb_reimport_main.png');bpy.ops.render.render(write_still=True)
# Fresh R10 diagnostic was already completed and committed during B review.
# Reuse that identical frozen baseline, never relabel it as a new render.
assert (Q/'diagnosis/R10_diagnostic_lantern.png').is_file()
print('R11_GLB_ACTUAL_IMPORTS_AND_DIAGNOSTICS_COMPLETE')
