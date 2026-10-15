"""Read-only in-memory test of proposed inferred D pillar / short rail connector.
Never saves .blend. All shapes and synthetic changes are explicitly hypotheses.
"""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent
ns={'__file__':str(OUT/'audit_physics.py')}
exec(Path(ns['__file__']).read_text().split('for s in sys.argv[sys.argv.index')[0],ns)
extract,record_pair,bounds=ns['extract'],ns['record_pair'],ns['bounds'];CN=ns['CURTAIN']
path=Path('/workspace/scratch/fa58bfcf0425/hospital_anchor_preparation_20261014/restored/hospital_D_before_J1_cameras.blend');digest=hashlib.sha256(path.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(path));dg=bpy.context.evaluated_depsgraph_get();rr={o.name:extract(o,dg) for o in bpy.data.objects if o.type=='MESH'}

def record(name,verts,tri):
 return {'meta':{'name':name,'bounds':bounds(verts)},'verts':verts,'triangles':tri,'bvh':BVHTree.FromPolygons(verts,tri,all_triangles=True,epsilon=0)}
def box(name,lo,hi):
 verts=[Vector((x,y,z)) for z in (lo[2],hi[2]) for y in (lo[1],hi[1]) for x in (lo[0],hi[0])]
 f=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)];tri=[t for a,b,c,d in f for t in ((a,b,c),(a,c,d))];return record(name,verts,tri)
def transform(r,fn):return record(r['meta']['name'],[Vector(fn(v)) for v in r['verts']],r['triangles'])
curtain=rr[CN];delta=-.04011060774326324;rr[CN]=transform(curtain,lambda v:(v.x,v.y+delta,v.z))
pillar=box('PROPOSED inferred beige pillar',(1.521875,-.36,0),(1.6446596,0,2.7146654))
connector=box('PROPOSED inferred short rail connector',(1.46,-.360307946,2.674999714),(1.70,-.330307946,2.708749771))
report={'source':str(path),'source_fidelity_accepted':False,'units':'arbitrary D scene units','curtain_shift_y':delta,'hypothesis_bounds':{r['meta']['name']:r['meta']['bounds'] for r in (pillar,connector)},'connector_note':'Y/Z extents not supplied by requester; tested an explicit .03 Y-depth hypothesis centered at original rail endpoint Y=-.345307946, with original rail Z span.','unmodified_proposal_pairs':[]}
for proposed in (pillar,connector):
 for n,r in rr.items():
  p=record_pair(proposed,r)
  if p:report['unmodified_proposal_pairs'].append(p)
p=record_pair(pillar,connector)
if p:report['unmodified_proposal_pairs'].append(p)
newmin=1.6446596384048462+.005
trim=[]
for n,r in rr.items():
 if not n.startswith('Blind bank 3'):continue
 oldmin=r['meta']['bounds'][0][0];oldmax=r['meta']['bounds'][1][0]
 moved=transform(r,lambda v:(newmin+(v.x-oldmin)*(oldmax-newmin)/(oldmax-oldmin),v.y,v.z))
 pp=[]
 for other,b in [(k,v) for k,v in rr.items() if k!=n]+[(pillar['meta']['name'],pillar),(connector['meta']['name'],connector)]:
  q=record_pair(moved,b)
  if q:pp.append(q)
 trim.append({'name':n,'old_bounds':r['meta']['bounds'],'new_bounds':moved['meta']['bounds'],'x_affine_scale':(oldmax-newmin)/(oldmax-oldmin),'intersecting_pairs':pp})
report['bank3_left_end_affine_trim_variant']={'left_x_target':newmin,'right_x_unchanged':True,'changes_only_bank3_slats':True,'slats':trim,'strict_surface_crossing_pair_count':sum(q['strict_transverse_crossing_pairs']>0 for r in trim for q in r['intersecting_pairs'])}
report['source_unchanged']=digest==hashlib.sha256(path.read_bytes()).hexdigest()
(OUT/'D_proposed_pillar_connector_audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
for p in report['unmodified_proposal_pairs']:print(p['a'],'vs',p['b'],'strict=',p['strict_transverse_crossing_pairs'],flush=True)
print('TRIM STRICT COUNT',report['bank3_left_end_affine_trim_variant']['strict_surface_crossing_pair_count'],flush=True)
