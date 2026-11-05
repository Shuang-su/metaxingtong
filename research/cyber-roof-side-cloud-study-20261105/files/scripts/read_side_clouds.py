import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent.parent;src=P.parent/'cyber-roof-cloud-r06-20261105/models/roof-r06b-experiment.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;out={'input':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'read_only':True,'no_model_saved':True,'groups':[]}
for prefix in ['CLOUD_0','CLOUD_1']:
 obs=[o for o in s.objects if o.name.startswith(prefix)];vs=[o.matrix_world@v.co for o in obs for v in o.data.vertices];g={'group':prefix,'world_bounds':[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)],'objects':[],'screen_bounds':{}}
 for o in obs:
  bm=bmesh.new();bm.from_mesh(o.data);g['objects'].append({'name':o.name,'world_matrix':[list(r) for r in o.matrix_world],'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'boundary_edges':sum(e.is_boundary for e in bm.edges),'signed_volume':bm.calc_volume(signed=True),'evidence_status':o.get('evidence_status','')});bm.free()
 for n in ['SOURCE11 conditional camera','SOURCE10 auxiliary different state']:
  c=bpy.data.objects[n];pp=[world_to_camera_view(s,c,v) for v in vs];g['screen_bounds'][n]=[min(p.x for p in pp)*1192,(1-max(p.y for p in pp))*671,max(p.x for p in pp)*1192,(1-min(p.y for p in pp))*671]
 out['groups'].append(g)
(P/'results/r06b-side-cloud-geometry.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
