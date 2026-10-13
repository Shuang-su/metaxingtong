"""Preserve a rejected local geometry test. Does not overwrite D; no rendering."""
import bpy,bmesh,json,hashlib,os
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent;BASE=Path(os.environ.get('HOSPITAL_D_BASELINE',str(R.parent/'hospital_d_recovery_20261013b/spatial_fit_d/hospital_spatial_D.blend')));P=R/'rail_vertical_hypothesis_parameters.json';J=json.load(open(P));assert hashlib.sha256(BASE.read_bytes()).hexdigest()==J['baseline_blend_sha256']
bpy.ops.wm.open_mainfile(filepath=str(BASE));s=bpy.context.scene;up=Vector(J['upper_center']);low=Vector(J['baseline_lower_center']);target=Vector(J['candidate_lower_center']);drop=J['fitted_vertical_drop_D_units'];gap=low.x-up.x
lower='Curtain rail • forward overhead beam.001';shorts=[o.name for o in bpy.data.objects if o.name.startswith('Curtain rail • forward connecting bracket')];changed=[lower]+shorts

def fp(exclude):
 q={}
 for o in bpy.data.objects:
  if o.type=='CAMERA' or o.name in exclude:continue
  q[o.name]={'matrix':list(map(list,o.matrix_world)),'hide_render':o.hide_render,'data':{'verts':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'mats':[m.name if m else None for m in o.data.materials]} if o.type=='MESH' else o.type}
 return hashlib.sha256(json.dumps(q,sort_keys=True).encode()).hexdigest()
before=fp(changed);lowerobj=bpy.data.objects[lower]
for v in lowerobj.data.vertices:v.co=lowerobj.matrix_world.inverted()@(lowerobj.matrix_world@v.co+(target-low))
for name in shorts:
 o=bpy.data.objects[name]
 for v in o.data.vertices:
  p=o.matrix_world@v.co;v.co=o.matrix_world.inverted()@Vector((up.x+(p.z-up.z),p.y,up.z-(p.x-up.x)*drop/gap))
assert fp(changed)==before
for k in ['A','B']:
 c=J['cameras'][k];d=bpy.data.cameras.new('DIAGNOSTIC_FREE_'+k);o=bpy.data.objects.new('DIAGNOSTIC_FREE_'+k,d);s.collection.objects.link(o);o.matrix_world=Matrix(c['matrix_world']);d.lens=c['lens_mm'];d.sensor_width=36;d.sensor_fit='HORIZONTAL';d.clip_start=.1;d.clip_end=1000
s.camera=bpy.data.objects['DIAGNOSTIC_FREE_B'];s['candidate_status']='REJECTED as a direct local replacement: B/G lower-bar holdouts regress with cameras fixed. This does not refute a vertical/hanging-frame interpretation with corrected real camera/curtain geometry.';s['scope']='Only lower bar and six short connectors altered. Upper bar, non-rail geometry, material, lighting and visibility preserved. No new render issued for rejected test.'
qa={'status':'REJECTED before rendering, preserved for reproducible diagnosis','baseline_sha256':J['baseline_blend_sha256'],'changed_objects':changed,'unchanged_object_fingerprint_before':before,'unchanged_object_fingerprint_after':fp(changed),'upper_bar_and_nonrail_geometry_unchanged':fp(changed)==before,'mesh_checks':{},'pair_surface_intersections':[],'limits':['Object-level affine transforms preserve original per-object topology; this is not a fresh full-room fidelity pass.','Bracket/bar surface overlaps are expected joining contacts, not watertight boolean union.','No new full-frame render was run because native-point holdouts failed.','Curtain/rail visibility remains conditional on the unaccepted D camera and drape geometry.']}
d=bpy.context.evaluated_depsgraph_get();bvhs={};bounds={}
for name in changed+['Curtain rail • forward overhead beam','Curtain • rebuilt uniform eight-fold drape','ROOM_SHELL__joined_solid__hidden_extents_inferred']:
 o=bpy.data.objects[name];e=o.evaluated_get(d);m=e.to_mesh();bm=bmesh.new();bm.from_mesh(m);bm.transform(e.matrix_world);bm.normal_update();qa['mesh_checks'][name]={'verts':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(x.is_boundary for x in bm.edges),'nonmanifold_edges':sum(not x.is_manifold for x in bm.edges),'zero_area_faces':sum(x.calc_area()<1e-12 for x in bm.faces),'signed_volume':bm.calc_volume(signed=True)};pts=[v.co.copy() for v in bm.verts];bounds[name]={'min':[min(p[k] for p in pts) for k in range(3)],'max':[max(p[k] for p in pts) for k in range(3)]};bvhs[name]=BVHTree.FromBMesh(bm);bm.free();e.to_mesh_clear()
for n in changed:
 for other in ['Curtain • rebuilt uniform eight-fold drape','ROOM_SHELL__joined_solid__hidden_extents_inferred']:
  overlaps=bvhs[n].overlap(bvhs[other]);qa['pair_surface_intersections'].append({'object':n,'other':other,'triangle_overlap_pairs':len(overlaps),'interpretation':'surface crossing test only; does not test containment'})
qa['world_bounds']=bounds
out=R/'hospital_rail_vertical_hypothesis_REJECTED.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out));qa['output_blend_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();(R/'rail_vertical_rejected_geometry_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));print('SAVED_REJECTED',out)
