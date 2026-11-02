import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
def snapshot(stage):
 bpy.ops.wm.open_mainfile(filepath=str(R/f'models/ferris_remake_{stage}_material.blend'));s=bpy.context.scene;ds=bpy.context.evaluated_depsgraph_get();rows={};trees={};raw={}
 for o in s.objects:
  if o.type!='MESH':continue
  raw[o.name]=hashlib.sha256(b''.join(struct.pack('<3d',*(o.matrix_world@v.co)) for v in o.data.vertices)).hexdigest();eo=o.evaluated_get(ds);me=eo.to_mesh();vv=[o.matrix_world@v.co for v in me.vertices];ff=[tuple(p.vertices) for p in me.polygons];rows[o.name]=[[min(v[i] for v in vv),max(v[i] for v in vv)] for i in range(3)];trees[o.name]=BVHTree.FromPolygons(vv,ff);eo.to_mesh_clear()
 cameras={o.name:([list(r) for r in o.matrix_world],o.data.lens) for o in s.objects if o.type=='CAMERA'};return rows,trees,raw,cameras
old,_,h0,c0=snapshot('R03');b,t,h1,c1=snapshot('R04');contacts=[]
def zcontact(a,side,target,targetside):
 box=b[a];xy=[(box[i][0]+box[i][1])/2 for i in range(2)];z=box[2][side];direction=1 if side else -1;origin=Vector((*xy,z-direction*.03));q,_,_,dist=t[target].ray_cast(origin,Vector((0,0,direction)),.20);gap=None if q is None else direction*(q.z-z);contacts.append({'from':a,'target':target,'from_surface':'top' if side else 'bottom','target_surface':'top' if targetside else 'bottom','model_bounds_signed_gap':direction*(b[target][2][targetside]-z),'actual_target_only_ray_origin':list(origin),'direction':[0,0,direction],'target_intersection':list(q) if q else None,'actual_surface_gap_or_overlap':gap,'definition':'positive separation; zero touch; negative penetration. Target-only ray at XY center; not bbox-only.'})
for side in [-1,1]:
 for y in [-.95,.95]:
  n=f'bench_{side}_support_{y}';zcontact(n,0,'floor_slab',1);zcontact(n,1,f'bench_{side}_apron',0)
 zcontact(f'bench_{side}_seat',0,f'bench_{side}_apron',1)
for name in ['ceiling_cross_beam_-0.8','ceiling_cross_beam_0.8']+[f'ceiling_cream_edge_{i}' for i in range(8)]:zcontact(name,1,'ceiling_slab',0)
zcontact('ceiling_lamp_diffuser',1,'ceiling_lamp_mount',0);zcontact('ceiling_lamp_mount',1,'ceiling_slab',0)
# Back/seat contacts are overlap rectangles, with bevel margins much smaller than overlap.
back=[]
for side in [-1,1]:
 a=b[f'bench_{side}_back'];bb=b[f'bench_{side}_seat'];back.append({'side':side,'overlap_xyz':[min(a[k][1],bb[k][1])-max(a[k][0],bb[k][0]) for k in range(3)],'limits':'AABB overlap is not exact intersection volume; rounded-edge inset .055 must be considered'})
changes=[n for n in h0 if h0[n]!=h1.get(n)];assert set(changes)=={f'bench_{s}_support_{y}' for s in [-1,1] for y in [-.95,.95]};assert c0==c1
j={'R03_R04_worldvertex_changed_objects':changes,'new_objects':sorted(set(h1)-set(h0)),'all_other_worldvertex_sha_equal':True,'camera_parameters_exact':True,'contacts':contacts,'back_seat_overlap_bounds':back,'door_leaf_shell':{'rear_leaf_fixed_jamb_nominal_shared_boundaries':[-.505,.505],'front_leaf_pivot':[-.505,-1.85],'front_fixed_jamb_inner_x':-.505,'status':'finite shared hinge-line/pivot and closed rear boundary; hinge hardware and swept clearance NOT source-proven, not claiming dynamic assembly test'},'frame_wall':{'wall_depth':[-.04,.10],'cream_sleeve_depth':[-.095,.125],'window_opening_rect_boundary':'shared outer cream straight extents; geometric sleeves cross full wall thickness','cream_gasket':'overlap in depth and width, actual aperture rays test all front/back inner loops','limits':'Sub-grid .001-model-unit rounded outer corner mismatch to rectangular cut has not been separately welded or topology-unioned; finite tests do not prove mathematical shell watertightness'},'limits':['Z contacts test actual evaluated target rays plus bounds, not load-bearing physics','Support shape/count remains inferred','Does not prove real source dimensions, hidden hardware, full swept door clearance or all intersections']}
(R/'qa/assembly-contacts-R04.json').write_text(json.dumps(j,indent=2));print('contacts',len(contacts),'positive_gap',[(r['from'],r['target'],r['actual_surface_gap_or_overlap']) for r in contacts if r['actual_surface_gap_or_overlap'] is None or r['actual_surface_gap_or_overlap']>1e-5])
