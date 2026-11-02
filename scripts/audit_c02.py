import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1]
def inspect(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));dg=bpy.context.evaluated_depsgraph_get();rows=[];positions={}
 for o in sorted(bpy.context.scene.objects,key=lambda o:o.name):
  if o.type not in {'MESH','CURVE'}:continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me);pts=[tuple(ev.matrix_world@v.co) for v in me.vertices];rows.append({'name':o.name,'verts':len(me.vertices),'triangles':len(me.loop_triangles),'boundary':sum(e.is_boundary for e in bm.edges),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'zero_edges':sum(e.calc_length()<1e-8 for e in bm.edges),'zmin':min(p[2] for p in pts),'zmax':max(p[2] for p in pts),'position_hash':hashlib.sha256(json.dumps(pts).encode()).hexdigest()});positions[o.name]=pts;bm.free();ev.to_mesh_clear()
 return rows,positions
mat,pts=inspect(R/'models/C02_repaired_materials.blend');white,_=inspect(R/'models/C02_repaired_white.blend');s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080
obs={'F1':[[348,681],[648,541]],'F2':[[463,680],[743,544]],'F3':[[467,670],[759,529]],'B1':[[366,484],[758,346]],'B2':[[436,480],[819,342]]};crate=bpy.data.objects['P03_crate'];mi=[min(v.co[i] for v in crate.data.vertices) for i in range(3)];ma=[max(v.co[i] for v in crate.data.vertices) for i in range(3)];P={'F1':bpy.data.objects['B01_lid'].matrix_world@Vector((-.465,-.265,.012)),'F2':bpy.data.objects['B01_lid'].matrix_world@Vector((.465,-.265,.012)),'F3':bpy.data.objects['B01_lid'].matrix_world@Vector((.465,.265,.012)),'B1':crate.matrix_world@Vector((mi[0],mi[1],ma[2])),'B2':crate.matrix_world@Vector((ma[0],mi[1],ma[2])),'apex':Vector((.20156395,10.3,6.14944935))};anchors=[]
for n,p in P.items():
 vals=[]
 for i in [1,2]:
  v=world_to_camera_view(s,bpy.data.objects[f'SOURCE_CONDITIONAL_{i}'],p);xy=[v.x*1920,(1-v.y)*1080];val={'source':i,'projected':xy}
  if n in obs:val['residual_px']=sum((a-b)**2 for a,b in zip(xy,obs[n][i-1]))**.5
  vals.append(val)
 anchors.append({'id':n,'xyz':list(p),'views':vals,'role':'new remade actual nominal geometry, source-pair used in historical working hypothesis; not independent truth'})
q={'stage':'C02 remake actual check','models':mat,'white_same_geometry':mat==white,'objects':len(mat),'triangles':sum(x['triangles'] for x in mat),'anchors':anchors,'limits':'nominal corners before bevel; topology not shape/source acceptance; world units arbitrary'};(R/'qa/C02_actual_audit.json').write_text(json.dumps(q,indent=2));(R/'qa/C02_actual_points.json').write_text(json.dumps({n:list(p) for n,p in P.items()},indent=2));print('AUDIT',len(mat),sum(x['triangles'] for x in mat),'same',mat==white)
for x in mat:
 if x['boundary'] or x['nonmanifold'] or x['degenerate_faces'] or x['zero_edges']:print(x['name'],x['boundary'],x['nonmanifold'],x['degenerate_faces'],x['zero_edges'])
