"""Limited technical attachment experiment; not production recovery or source fit."""
import bpy,bmesh,pathlib,json,hashlib,struct,math,sys,datetime
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=pathlib.Path(__file__).resolve().parents[1];P=R/'inputs/leaf-only-r06-nonexact-diagnostic-replay.blend'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='46f45501671a3e768be6d376860b7af7cf6b8f9be1630a7898572b5ef1fa737c'
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene
assert len(s.objects)==20 and all(o.type=='MESH' for o in s.objects)
def gh(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(struct.pack('<3d',*(o.matrix_world@v.co)))
 for f in o.data.polygons:h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
 return h.hexdigest()
def topology(o):
 bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world);bm.normal_update()
 z=dict(boundary=sum(e.is_boundary for e in bm.edges),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_area=sum(f.calc_area()<1e-12 for f in bm.faces),min_face_area=min(f.calc_area() for f in bm.faces),signed_volume=bm.calc_volume(signed=True));bm.free();return z
old={o.name:[v.co.copy() for v in o.data.vertices] for o in s.objects};oldhash={o.name:gh(o) for o in s.objects};oldt={o.name:topology(o) for o in s.objects}
shell=s.objects['LEAF_001_ThinConcaveShell'];m=shell.data;m.calc_loop_triangles();sv=[shell.matrix_world@v.co for v in m.vertices]
tree=BVHTree.FromPolygons(sv,[tuple(t.vertices) for t in m.loop_triangles],all_triangles=True)
def vert(p):
 a,_,_,_=tree.ray_cast(Vector((p.x,p.y,8)),Vector((0,0,-1)),20)
 assert a is not None
 b,_,_,_=tree.ray_cast(a+Vector((0,0,-1e-5)),Vector((0,0,-1)),20)
 assert b is not None
 return p.z-a.z,a.z-b.z
changes=[]
for o in s.objects:
 if o==shell:continue
 sides=9 if o.name.startswith('LEAF_002') else 6;rows=[]
 assert o.matrix_world.to_3x3()==Matrix.Identity(3),'Only pure translation allowed for local z edit'
 for i in range(len(o.data.vertices)//sides):
  inds=list(range(i*sides,(i+1)*sides));vv=[o.matrix_world@o.data.vertices[k].co for k in inds];pp=vv+[(vv[j]+vv[(j+1)%sides])*.5 for j in range(sides)]
  gaps=[vert(p) for p in pp];g=min(x[0] for x in gaps);th=min(x[1] for x in gaps)
  # Apply only when every sampled edge vertex/midpoint is above the uppermost shell hit.
  # Small-gaps ramp avoids a fixed .0005 step near the last unmodified ring.
  embed=min(.0005,g*.5,th*.1) if g>1e-5 else 0.;dz=-(g+embed) if embed>0 else 0.
  assert abs(dz)<.02
  if dz:
   for k in inds:o.data.vertices[k].co.z+=dz
  vv2=[o.matrix_world@o.data.vertices[k].co for k in inds];pp2=vv2+[(vv2[j]+vv2[(j+1)%sides])*.5 for j in range(sides)];gg=[vert(p) for p in pp2]
  rows.append(dict(ring=i,old_min_upper_gap=g,old_min_first_interval=th,dz=dz,embedding_target=embed,new_min_upper_gap=min(x[0] for x in gg),new_min_margin_above_first_lower=min(x[0]+x[1] for x in gg)))
 o.data.update();newt=topology(o)
 assert newt['boundary']==newt['nonmanifold']==newt['zero_area']==0
 xy=max(abs(v.co[k]-q[k]) for v,q in zip(o.data.vertices,old[o.name]) for k in [0,1]);assert xy==0
 # Cross-section translation preserves all pairwise intra-ring distances to float32 roundoff.
 dist_error=0.
 for i in range(len(o.data.vertices)//sides):
  for j in range(sides):
   for k in range(j):
    a,b=i*sides+j,i*sides+k
    dist_error=max(dist_error,abs((o.data.vertices[a].co-o.data.vertices[b].co).length-(old[o.name][a]-old[o.name][b]).length))
 assert dist_error<5e-7
 changed=[r for r in rows if r['dz']]
 assert all(-.000501<=r['new_min_upper_gap']<0 for r in changed)
 assert all(r['new_min_margin_above_first_lower']>0 for r in changed)
 assert max(r['new_min_upper_gap'] for r in rows)<=1e-5
 changes.append(dict(name=o.name,changed_ring_count=len(changed),maximum_downward_shift=max(-r['dz'] for r in rows),all_xy_exact=True,max_intra_ring_pairwise_distance_error=dist_error,old_topology=oldt[o.name],new_topology=newt,old_hash=oldhash[o.name],new_hash=gh(o),rings=rows))
assert gh(shell)==oldhash[shell.name]
# Main far-end rings remain byte-for-byte vertex-coordinate unchanged.
mid=s.objects['LEAF_002_CentralMidrib'];assert all(v.co==q for v,q in zip(list(mid.data.vertices)[22*9:],old[mid.name][22*9:]))
projection=[];cams=json.loads((R/'inputs/archived-r06-cameras.json').read_text())['cameras']
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100
for c in cams:
 if not c['name'].startswith(('SOURCE_','AUX_')):continue
 d=bpy.data.cameras.new(c['name']);o=bpy.data.objects.new(c['name'],d);s.collection.objects.link(o)
 for k,v in c['data'].items():setattr(d,k,v)
 o.matrix_world=Matrix(c['matrix_world']);bpy.context.view_layer.update();deltas=[]
 for name,verts in old.items():
  obj=s.objects[name]
  for q,v in zip(verts,obj.data.vertices):
   a=world_to_camera_view(s,o,obj.matrix_world@q);b=world_to_camera_view(s,o,obj.matrix_world@v.co)
   if a.z>0 and b.z>0 and 0<=a.x<=1 and 0<=a.y<=1 and 0<=b.x<=1 and 0<=b.y<=1:deltas.append(math.hypot((b.x-a.x)*3840,(b.y-a.y)*2160))
 projection.append(dict(camera=c['name'],in_both_frusta_vertex_count=len(deltas),max_displacement_pixels=max(deltas),note='Geometry projection delta only; no source image or fit error measured.'))
 bpy.data.objects.remove(o,do_unlink=True);bpy.data.cameras.remove(d)
assert len(s.objects)==20
s['diagnostic_only']='Nonexact 20-mesh replay; technical vein attachment experiment. No source-fit acceptance, original recovery, whole scene, or Boolean weld.'
s['attachment_method']='Ringwise Z translations of only wholly-above sampled rings; embedding <=0.0005 arbitrary model units; XY and main shell exact.'
(R/'models').mkdir(exist_ok=True);out=R/'models/leaf-only-contact-candidate-v2.blend';assert not out.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(out))
report=dict(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),fixture_sha256=hashlib.sha256(P.read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),main_shell_hash=gh(shell),main_shell_unchanged=True,original_production_not_restored=True,source_accepted=False,boolean_weld=False,changed_meshes=len(changes),changed_rings=sum(r['changed_ring_count'] for r in changes),method=s['attachment_method'],rows=changes,projection_deltas=projection)
(R/'qa/support-candidate-v2.json').write_text(json.dumps(report,indent=2)+'\n')
print('Saved',out,'changed rings',report['changed_rings'],'max downward',max(x['maximum_downward_shift'] for x in changes),'projection',projection,flush=True)
