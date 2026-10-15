"""Test reversible world-Y adjustments in memory; never save a .blend.
Use with blender -b --python SCRIPT -- source.blend [...].
"""
import bpy,sys,json,hashlib,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
# Import audit definitions, avoiding its CLI loop.
ns={'__file__':str(Path(__file__).with_name('audit_physics.py'))}
exec(Path(ns['__file__']).read_text().split('for s in sys.argv[sys.argv.index')[0],ns)
extract,record_pair,bounds=ns['extract'],ns['record_pair'],ns['bounds']
OUT=Path(__file__).resolve().parent;CN=ns['CURTAIN']

def translated(r,dy):
 v=[p+Vector((0,dy,0)) for p in r['verts']]
 return {**r,'verts':v,'bvh':BVHTree.FromPolygons(v,r['triangles'],all_triangles=True,epsilon=0),'meta':{**r['meta'],'bounds':bounds(v)}}

def audit(path):
 digest=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));dg=bpy.context.evaluated_depsgraph_get()
 rr={o.name:extract(o,dg) for o in bpy.data.objects if o.type=='MESH'};c=rr[CN];blinds={n:r for n,r in rr.items() if n.startswith('Blind')}
 blind_min_y=min(r['meta']['bounds'][0][1] for r in blinds.values());delta=blind_min_y-c['meta']['bounds'][1][1]-.005
 variants=[{'name':'curtain_only_safe_all_blinds_and_cords','deltas':{CN:delta}},{'name':'curtain_only_safe_all_blinds_and_cords_half_margin','deltas':{CN:delta+.0025}},{'name':'all_blinds_and_cords_behind_existing_curtain','deltas':{n:-delta for n in blinds}}]
 report={'file':str(path),'source_fidelity_accepted':False,'units':'arbitrary scene units','maximum_safe_curtain_y_for_005_clearance':blind_min_y-.005,'variants':[]}
 for spec in variants:
  mm={n:translated(rr[n],dy) for n,dy in spec['deltas'].items()};pairs=[];seen=set()
  for n,a in mm.items():
   for other,b0 in rr.items():
    if other==n:continue
    key=tuple(sorted((n,other)))
    if key in seen:continue
    seen.add(key);b=mm.get(other,b0);p=record_pair(a,b)
    if p:pairs.append(p)
  cc=mm.get(CN,c)
  report['variants'].append({**spec,'curtain_bounds':cc['meta']['bounds'],'intersecting_pairs':pairs,'strict_surface_crossing_pairs_count':sum(p['strict_transverse_crossing_pairs']>0 for p in pairs),'curtain_strict_surface_crossing_objects':[p['b'] if p['a']==CN else p['a'] for p in pairs if CN in (p['a'],p['b']) and p['strict_transverse_crossing_pairs']>0]})
 report['rail_attachment_geometry']=[{'name':n,'bounds':r['meta']['bounds'],'curtain_top_to_rail_bottom':r['meta']['bounds'][0][2]-c['meta']['bounds'][1][2]} for n,r in rr.items() if n.startswith('Curtain rail')]
 report['source_unchanged']=digest==hashlib.sha256(path.read_bytes()).hexdigest()
 (OUT/(path.stem+'_clearance_variants.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(path.stem,'safe curtain dy',delta,'results',[(v['name'],v['strict_surface_crossing_pairs_count'],v['curtain_strict_surface_crossing_objects']) for v in report['variants']],flush=True)
for s in sys.argv[sys.argv.index('--')+1:]:audit(Path(s))
