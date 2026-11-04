import bpy,math,json,pathlib
from mathutils import Vector
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-qa-20261105');bpy.ops.wm.open_mainfile(filepath=str(P/'models/R02_material.blend'));c=Vector((2,1.5,2.35));axis=Vector((0,-.85,-.3)).normalized();u=Vector((1,0,0));v=axis.cross(u).normalized();r={};limit=1.05*math.cos(math.pi/8)
for o in bpy.context.scene.objects:
 if not o.name.startswith('UMBRELLA_rib_'):continue
 vals=[]
 for p in o.data.vertices:
  q=o.matrix_world@p.co-c;x,y=q.dot(u),q.dot(v);vals.append(max(x*math.cos((j+.5)*math.pi/4)+y*math.sin((j+.5)*math.pi/4)-limit for j in range(8)))
 r[o.name]={'vertices_outside_octagon_1e6':sum(a>1e-6 for a in vals),'max_projected_excess':max(vals)}
(Q/'R02-rib-planar-perimeter.json').write_text(json.dumps({'method':'All actual rod vertices projected to canopy radial plane; signed halfspace outside ideal 8 edge outer footprint. Not 3D shell thickness containment or source silhouette acceptance.','ribs':r},indent=2));print([(n,x) for n,x in r.items() if x['vertices_outside_octagon_1e6']])
