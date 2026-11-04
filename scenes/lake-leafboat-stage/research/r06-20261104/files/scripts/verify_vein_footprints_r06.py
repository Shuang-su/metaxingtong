import bpy,pathlib,json,math
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/lakeleaf-r06-material.blend'));rows=[]
def test(p):
 u=p.x/4.65
 if abs(u)>=1:return u,None,False
 w=1.58*(1-u*u)**.72*(1+.06*math.sin(3*math.pi*u));v=p.y/w;return u,v,abs(v)<1
for o in bpy.context.scene.objects:
 if not o.name.startswith(('LEAF_002','LEAF_003')):continue
 m=o.data;points=[o.matrix_world@v.co for v in m.vertices];samples=points+[(points[e.vertices[0]]+points[e.vertices[1]])*.5 for e in m.edges]+[sum((points[j] for j in f.vertices),Vector())/len(f.vertices) for f in m.polygons];vals=[test(p) for p in samples];bad=[{'sample':i,'u':x[0],'v':x[1]} for i,x in enumerate(vals) if not x[2]]
 rows.append({'id':o.name,'mesh_vertices':len(points),'sample_count_vertices_edge_mids_face_centers':len(samples),'u_range':[min(v[0] for v in vals),max(v[0] for v in vals)],'max_abs_v':max(abs(v[1]) for v in vals if v[1] is not None),'outside_samples':bad})
report={'method':'Actual finite-radius vein mesh vertices plus edge midpoints and face centers tested against analytic leaf XY parameter domain. This is a discrete footprint test, not a continuous collision proof or source acceptance.','all_sampled_footprints_inside':all(not x['outside_samples'] for x in rows),'rows':rows};(R/'qa/r06/finite-vein-footprint-tests.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_sampled_footprints_inside'];print('All finite vein footprint samples are inside the shell XY domain.')
