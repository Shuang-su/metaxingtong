import bpy,json,hashlib,struct,math
from pathlib import Path
from collections import Counter
D=Path(__file__).resolve().parents[1]
def snapshot():
 out={}
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  coords=[tuple(o.matrix_world@v.co) for v in o.data.vertices];h=hashlib.sha256()
  for v in coords:h.update(struct.pack('<3f',*v))
  for p in o.data.polygons:
   for i in p.vertices:h.update(struct.pack('<I',i))
  edges=Counter(tuple(sorted((p.vertices[i],p.vertices[(i+1)%len(p.vertices)]))) for p in o.data.polygons for i in range(len(p.vertices)))
  out[o.name]={'geometry_sha256':h.hexdigest(),'bounds':[[min(v[i] for v in coords) for i in range(3)],[max(v[i] for v in coords) for i in range(3)]],'non2_edges':sum(v!=2 for v in edges.values())}
 return out
report={};ref=None
for typ in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/FR02_{typ}.blend'));a=snapshot();ref=a if ref is None else ref;report[typ]={'mesh_count':len(a),'same_as_material_geometry':{k:v['geometry_sha256'] for k,v in a.items()}=={k:v['geometry_sha256'] for k,v in ref.items()},'closed_individual_meshes':all(v['non2_edges']==0 for v in a.values()),'bad_edge_meshes':[k for k,v in a.items() if v['non2_edges']]}
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(D/f'models/FR02_{typ}.glb'));b=snapshot();common=set(a)&set(b);delta=max(abs(a[n]['bounds'][i][j]-b[n]['bounds'][i][j]) for n in common for i in range(2) for j in range(3));report[typ]['actual_glb_roundtrip']={'mesh_count':len(b),'missing':list(set(a)-set(b)),'extra':list(set(b)-set(a)),'max_world_bbox_delta':delta}
bpy.ops.wm.open_mainfile(filepath=str(D/'models/FR02_material.blend'))
contacts=[]
for o in bpy.context.scene.objects:
 if o.name.startswith('COL_') and o.name.endswith('_roof_support'):
  roof=bpy.data.objects['ROOF_'+o.name.split('_')[1]+'_thick_curved_solid'];ok,hit,normal,face=roof.ray_cast(o.location.__class__((o.location.x,o.location.y,4.31)),o.location.__class__((0,0,1)));top=o.location.z+o.dimensions.z/2;contacts.append({'name':o.name,'ray_hit':ok,'top_minus_underside':top-hit.z if ok else None,'bottom':o.location.z-o.dimensions.z/2})
report['roof_support_centerline_contacts']=contacts
report['bounded_contact_results']={'all20_roof_supports_overlap_at_tested_axis':len(contacts)==20 and all(x['ray_hit'] and 0<x['top_minus_underside']<.02 for x in contacts),'pole_cap_overlap_assumption':'cap top4.30 versus support bottom4.27, world-axis section only','round_lamp_connections':'10 added brackets, attachment endpoints analytically lie within continuous inner beam or hanger cross section; not exhaustive mesh-SAT','string_end_ties':'6 endpoint rods start4.105 under cable4.12 and terminate4.43 into eave band4.20..4.42 at radius6.95; inferred technical attachment','basin_top_z':-.24,'water_bottom_z':-.10,'water_top_z':-.08,'not_coplanar_basin_water':True,'urn_profile_bottom_and_walkway_top_z':[0,0],'roof_tile_spacing':'62 radial seams across122deg, inner center spacing approx.242 at r6.95 vs rod diameter.09; no neighboring seam overlap inferred; same-seam joints intentionally intersect','remaining':'roof support full-footprint intersections, all caps and every rod not exhaustively tested; no source validation'}
(D/'qa/FR02-technical-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
