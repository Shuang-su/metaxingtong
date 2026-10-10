import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];P=R/'models/CastleHall_Shared_White_Candidate.blend';bpy.ops.wm.open_mainfile(filepath=str(P));S=bpy.context.scene;out={'mesh_count':0,'issues':[],'new_meshes':[]};deps=bpy.context.evaluated_depsgraph_get()
for o in S.objects:
 if o.type!='MESH':continue
 out['mesh_count']+=1;bm=bmesh.new();bm.from_mesh(o.data);rec={'name':o.name,'boundary':sum(e.is_boundary for e in bm.edges),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'signed_volume':bm.calc_volume(signed=True),'degenerate':sum(f.calc_area()<1e-10 for f in bm.faces)};bm.free()
 if rec['boundary'] or rec['nonmanifold'] or rec['signed_volume']<=0 or rec['degenerate']:out['issues'].append(rec)
 if o.name.startswith(('RIGHT_','INF_STAIR','ARCH_Side_wall_1')):out['new_meshes'].append(rec)
# Semantic real aperture rays, far/near margins left clear by arch jamb.
h=[]
for y in [.7,1.2,1.76,2.3,2.8]:
 for z in [.3,1,2,2.5,2.8]:
  if z>2.55 and (y-1.76)**2+(z-2.55)**2>1.25**2:continue
  hit,p,n,i,o,m=S.ray_cast(deps,Vector((6.1,y,z)),Vector((1,0,0)),distance=8)
  h.append({'y':y,'z':z,'first':o.name if hit else 'ESCAPE','at':list(p) if hit else None})
out['aperture_rays']=h;(R/'qa/candidate_initial_geometry_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
