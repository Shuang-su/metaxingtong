"""Save sky-only R10 from R09; verify all scene geometry/materials/lights/cameras.
Arguments: antialias or rollback. No mesh edits, camera tuning or external writes.
"""
import bpy,json,hashlib,array,ast,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];Q=R/'qa/r10';O=R/'models/r10';O.mkdir(parents=True,exist_ok=True);mode=sys.argv[-1];assert mode in ['antialias','rollback']
# Reuse the already reviewed read-only snapshot functions, not the mutation code.
module=ast.parse((R/'scripts/apply_n6766_camera.py').read_text());defs=[n for n in module.body if isinstance(n,ast.FunctionDef)];exec(compile(ast.Module(body=defs,type_ignores=[]),'snapshot_functions','exec'),globals())
fields=['geometry_hash','material_hash','light_hash','texture_hash','mesh_count','geometry_objects','other_cameras','N6766','active_camera','render_engine','eevee_samples'];report={}
for kind in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'models/r09/piano_seaside_{kind}.blend'));sc=bpy.context.scene;before=snapshot()
 if mode=='antialias':
  for state in ['S40_sunset','S105_bluehour']:
   w=bpy.data.worlds['R09 '+state+' global environment'];node=next(n for n in w.node_tree.nodes if n.type=='TEX_ENVIRONMENT');im=bpy.data.images.load(str(R/'textures/r10_trial'/f'{state}.hdr'),check_existing=False);node.image=im;node.interpolation='Cubic'
  sc['source_state']='R09 global S40/S105 fields retained; R10 anti-aliased texture sampling; no camera binding'
 else:
  with bpy.data.libraries.load(str(R/'models/r08/piano_seaside_material.blend'),link=False) as (src,dst):
   assert 'Approximate sunset environment' in src.worlds,src.worlds;dst.worlds=['Approximate sunset environment']
  sc.world=dst.worlds[0];sc.world.name='R10 explicit R08 sky rollback';sc['source_state']='Only sky rolled back to R08 shared gradient; R09 paper/deck/sea/shore and lighting retained; not a recovered real sky'
 sc['stage']='r10 sky-only '+mode+'; all R09 geometry/materials/lights/cameras retained'
 bpy.ops.file.pack_all();dest=O/f'piano_seaside_{kind}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest));bpy.ops.wm.open_mainfile(filepath=str(dest));after=snapshot();bad=[k for k in fields if before[k]!=after[k]];assert not bad,bad
 w=bpy.context.scene.world;wi=[]
 for n in w.node_tree.nodes:
  if n.type=='TEX_ENVIRONMENT':wi.append({'name':n.image.name,'pixels':list(n.image.size),'interpolation':n.interpolation,'packed_sha256':hashlib.sha256(n.image.packed_file.data).hexdigest() if n.image.packed_file else None})
 report[kind]={'actual_saved_file_reopened':True,'mode':mode,'mesh_count':after['mesh_count'],'verified_unchanged_snapshot_sections':fields,'geometry_hash':after['geometry_hash'],'assigned_material_hash':after['material_hash'],'light_hash':after['light_hash'],'source_camera_count':5,'all_camera_count':len(after['other_cameras'])+1,'world_before':before['world_hash'],'world_after':after['world_hash'],'world_name':w.name,'active_world_images':wi,'GLB':'retain R09 validated GLB unchanged; world/cameras/lights excluded from that export'}
(Q/'sky-only-saved-invariants.json').write_text(json.dumps(report,indent=2)+'\n');print('R10_SKY_ONLY_SAVED',mode)
