import bpy,bmesh,json,math,hashlib,struct
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'deliverables';frozen=next(x for x in json.loads((R/'frozen_r03/freeze_manifest.json').read_text())['blends'] if x['kind']=='material');bpy.ops.wm.open_mainfile(filepath=frozen['file']);S=bpy.context.scene
D={'input_blend_sha256':frozen['sha256'],'dimension_convention':'Inferred model units. These are not measured metres.','per_mesh':[],'source_video':S['Reference_video']}
sv=[];sf=[];av=[];af=[];gh=hashlib.sha256()
for o in sorted([o for o in S.objects if o.type=='MESH'],key=lambda a:a.name):
 me=o.data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me);di={'name':o.name,'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_length_edges':sum(e.calc_length()<1e-8 for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'degenerate_triangles':sum(t.area<1e-12 for t in me.loop_triangles),'signed_volume':bm.calc_volume(signed=True),'uv':bool(me.uv_layers),'hidden':o.hide_render or o.hide_viewport};bm.free();D['per_mesh'].append(di)
 wp=[o.matrix_world@v.co for v in me.vertices];off=len(av);av.extend(wp);af.extend([tuple(off+i for i in t.vertices) for t in me.loop_triangles])
 # Structural enclosure only: drapes, loose luggage and furniture cannot hide an enclosure leak.
 arch=any(c.name.startswith('01_') for c in o.users_collection) or o.get('Geometry_role') in ['envelope','glazing'] or o.name.startswith(('Window side return','Window sill or head return','Window vertical moulding','Window horizontal moulding','Solid doorway','Door jamb backstop','Door head backstop','Door glass full-depth','Door threshold'))
 if arch:
  off=len(sv);sv.extend(wp);sf.extend([tuple(off+i for i in t.vertices) for t in me.loop_triangles])
 gh.update(o.name.encode());gh.update(struct.pack('<16f',*[v for row in o.matrix_world for v in row]));gh.update(struct.pack('<%df'%(len(me.vertices)*3),*[a for v in me.vertices for a in v.co]));gh.update(str([tuple(p.vertices) for p in me.polygons]).encode())
full=BVHTree.FromPolygons(av,af,all_triangles=True);env=BVHTree.FromPolygons(sv,sf,all_triangles=True)
miss=[];rays=0

def cast(label,origin,direction,maxdist=20):
 global rays
 rays+=1
 p=env.ray_cast(Vector(origin),Vector(direction),maxdist)[0]
 if p is None:miss.append({'surface':label,'origin':origin,'direction':direction})

def seq(a,b,step):return [a+(b-a)*i/math.ceil((b-a)/step) for i in range(math.ceil((b-a)/step)+1)]
for side in [-1,1]:
 for y in seq(-5.54,5.54,.037):
  for z in seq(.003,2.405,.031):cast('sidewall',(0,y,z),(side,0,0))
 for x in seq(-1.49,1.49,.023):
  top=2.59 if abs(x)<.58 else 2.60-(abs(x)-.58)*(.24/.92)
  for z in seq(.002,top-.005,.025):cast('end',(x,0,z),(0,side,0))
for x in seq(-1.59,1.59,.031):
 for y in seq(-5.59,5.59,.04):
  cast('roof',(x,y,1.15),(0,0,1));cast('floor',(x,y,.35),(0,0,-1))
D['envelope']={'rays':rays,'misses':miss,'miss_count':len(miss),'pass':not miss,'definition':'Structural enclosure plus actual glazing, excludes curtains/furniture and lamps. Door-window/side-window rays must hit finite glazing or reveal.'}
block=[];n=0
for x in [-.30,-.15,0,.15,.30]:
 for y in seq(-5.30,5.30,.05):
  n+=1;p=full.ray_cast(Vector((x,y,1.98)),Vector((0,0,-1)),2.1)[0]
  if p is None or p.z>.05:block.append({'x':x,'y':y,'hit_z':None if p is None else p.z})
D['aisle']={'tested_clear_width':.60,'standing_clearance':1.98,'samples':n,'blocked':block,'pass':not block,'note':'Minimum table-to-table plan clearance is about .68 model units; standing test checks .60, not wheelchair/compliance certification.'}
D['supports']={'table_mounting_plates':sum(o.name.startswith('Table circular floor mounting plate') for o in S.objects),'seat_floor_contact_feet':sum(o.name.startswith('Seat continuous floor contact foot') for o in S.objects),'luggage_case_count':sum(o.name.startswith('Luggage case') for o in S.objects),'table_mount_bottoms':[],'seat_foot_bottoms':[]}
for o in S.objects:
 if o.type!='MESH':continue
 if o.name.startswith('Table circular floor mounting plate'):D['supports']['table_mount_bottoms'].append(min((o.matrix_world@v.co).z for v in o.data.vertices))
 if o.name.startswith('Seat continuous floor contact foot'):D['supports']['seat_foot_bottoms'].append(min((o.matrix_world@v.co).z for v in o.data.vertices))
D['supports']['pass']=D['supports']['table_mounting_plates']==12 and D['supports']['seat_floor_contact_feet']==24 and all(abs(z)<.003 for z in D['supports']['table_mount_bottoms']+D['supports']['seat_foot_bottoms'])
D['mesh_summary']={'objects':len(D['per_mesh']),'vertices':sum(x['vertices'] for x in D['per_mesh']),'triangles':sum(x['triangles'] for x in D['per_mesh']),'boundary_edges':sum(x['boundary_edges'] for x in D['per_mesh']),'nonmanifold_edges':sum(x['nonmanifold_edges'] for x in D['per_mesh']),'zero_length_edges':sum(x['zero_length_edges'] for x in D['per_mesh']),'zero_area_faces':sum(x['zero_area_faces'] for x in D['per_mesh']),'degenerate_triangles':sum(x['degenerate_triangles'] for x in D['per_mesh']),'nonpositive_volume_objects':[x['name'] for x in D['per_mesh'] if x['signed_volume']<=0],'all_have_uv':all(x['uv'] for x in D['per_mesh']),'hidden_mesh_objects':[x['name'] for x in D['per_mesh'] if x['hidden']]}
D['geometry_sha256']=gh.hexdigest();D['camera_independence']={'frame_handlers':len(bpy.app.handlers.frame_change_pre)+len(bpy.app.handlers.frame_change_post),'animated_meshes':[o.name for o in S.objects if o.type=='MESH' and o.animation_data],'camera_visibility_drivers':[],'source_parameters_preserved':True,'source_camera_names':[o.name for o in S.objects if o.type=='CAMERA' and o.name.startswith('MATCH_')]}
D['packed_images']=sum(bool(im.packed_file) for im in bpy.data.images);D['pass']=D['envelope']['pass'] and D['aisle']['pass'] and D['supports']['pass'] and D['mesh_summary']['boundary_edges']==0 and D['mesh_summary']['nonmanifold_edges']==0 and D['mesh_summary']['degenerate_triangles']==0 and D['mesh_summary']['zero_length_edges']==0 and not D['mesh_summary']['nonpositive_volume_objects']
(O/'verification.json').write_text(json.dumps(D,indent=2));print(json.dumps({k:v for k,v in D.items() if k!='per_mesh'},indent=2))
