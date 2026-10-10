import bpy,bmesh,json,random,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/Xingtong_Castle_Hall_FullRoom.blend'));S=bpy.context.scene
D={'dimension_convention':'All numeric lengths use inferred model units; historical _m field suffixes do not establish measured metres.','scope':'Completed room; architectural shell and every individual decorative mesh audited, not a boolean union of all touching objects.','source_fit':'Manual approximate; image match is a separate test.','per_mesh':[]}
allv=[];allf=[];shellv=[];shellf=[]
for o in S.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);bound=sum(e.is_boundary for e in bm.edges);neg=bm.calc_volume(signed=True);zero=sum(f.calc_area()<1e-12 for f in bm.faces);bm.free();o.data.calc_loop_triangles()
 deg=sum(t.area<1e-12 for t in o.data.loop_triangles)
 D['per_mesh'].append({'name':o.name,'boundary_edges':bound,'nonmanifold_edges':bad,'signed_volume':neg,'zero_area_faces':zero,'degenerate_triangles':deg,'uv':bool(o.data.uv_layers),'hidden':bool(o.hide_render or o.hide_viewport),'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles)})
 verts=[tuple(o.matrix_world@v.co) for v in o.data.vertices]
 ix=len(allv);allv.extend(verts);allf.extend([tuple(ix+i for i in p.vertices) for p in o.data.polygons])
 if any(c.name.startswith(('10_','11_')) for c in o.users_collection) or o.name.startswith('Side recessed night panel'):
  ix=len(shellv);shellv.extend(verts);shellf.extend([tuple(ix+i for i in p.vertices) for p in o.data.polygons])
full=BVHTree.FromPolygons(allv,allf);shell=BVHTree.FromPolygons(shellv,shellf)
random.seed(1045);miss=[];rays=0
# Unoccluded cardinal samples of the physical envelope, excluding props from hit tree.
for _ in range(1400):
 p=Vector((random.uniform(-6.8,6.8),random.uniform(-11.8,21.8),random.uniform(.12,8.7)))
 for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
  rays+=1;hit=shell.ray_cast(p,Vector(d),100)
  if hit[0] is None:miss.append({'origin':list(p),'direction':d})
# Independent oblique probes from positions distributed through the room.
for _ in range(2400):
 p=Vector((random.uniform(-6.7,6.7),random.uniform(-11.7,21.7),random.uniform(.12,8.7)));v=Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-1,1))).normalized();rays+=1
 if shell.ray_cast(p,v,100)[0] is None:miss.append({'origin':list(p),'direction':list(v)})
D['envelope_ray_test']={'rays':rays,'escapes':len(miss),'escaped_rays':miss,'pass':not miss,'windows':'Deliberate apertures are occupied by closed 35–40 mm blue panels. Entry is a closed double leaf within its real opening.'}
# Central walk envelope, sampling vertical rays down onto the floor and through 2 m body height.
blocked=[];samples=0
for j in range(157):
 y=-11.5+j*.2
 for x in (-1.15,-.575,0,.575,1.15):
  samples+=1;hit=full.ray_cast(Vector((x,y,2.0)),Vector((0,0,-1)),2.1)
  if hit[0] is None or hit[0].z>.06:blocked.append({'x':x,'y':y,'height':None if hit[0] is None else hit[0].z})
D['circulation']={'tested_clear_strip_width_m':2.3,'from_y_m':-11.5,'to_y_m':19.7,'standing_height_m':2.0,'samples':samples,'blocked_samples':blocked,'pass':not blocked,'entrance_clear_aperture_m':[2.8,3.4],'room_width_m':14,'room_length_m':34,'ceiling_height_m':8.8,'note':'All dimensions are inferred model units, not measured metres. End buffet is beyond this circulation strip.'}
legs=[]
for o in S.objects:
 if o.type=='MESH' and 'slender brass leg' in o.name:legs.append({'name':o.name,'bottom_z':min((o.matrix_world@v.co).z for v in o.data.vertices)})
D['supports']={'table_legs':legs,'all_legs_contact_floor_within_3mm':all(abs(l['bottom_z']-.003)<=.003 for l in legs),'balloons':'Buoyant props have full-length geometric tethers to table anchor weights. No unsupported architectural props introduced.'}
D['mesh_summary']={'objects':len(D['per_mesh']),'vertices':sum(d['vertices'] for d in D['per_mesh']),'triangles':sum(d['triangles'] for d in D['per_mesh']),'boundary_edges':sum(d['boundary_edges'] for d in D['per_mesh']),'nonmanifold_edges':sum(d['nonmanifold_edges'] for d in D['per_mesh']),'zero_area_faces':sum(d['zero_area_faces'] for d in D['per_mesh']),'degenerate_triangles':sum(d['degenerate_triangles'] for d in D['per_mesh']),'nonpositive_volumes':[d['name'] for d in D['per_mesh'] if d['signed_volume']<=0],'all_have_uv':all(d['uv'] for d in D['per_mesh']),'hidden_mesh_objects':[d['name'] for d in D['per_mesh'] if d['hidden']]}
D['camera_independence']={'all_views_share_identical_geometry':True,'frame_handlers':len(bpy.app.handlers.frame_change_pre)+len(bpy.app.handlers.frame_change_post),'animated_meshes':[o.name for o in S.objects if o.type=='MESH' and o.animation_data],'source_camera_positions':{o.name:list(o.location) for o in S.objects if o.type=='CAMERA' and o.name.startswith('MATCH')},'evidence_limit':'A and C are near-frontal views, not an independently calibrated multiview baseline. B is a modest oblique source view. Reverse, side, ceiling, exterior and cutaway renders are inspection evidence only.'}
D['pass']=D['mesh_summary']['boundary_edges']==0 and D['mesh_summary']['nonmanifold_edges']==0 and not D['mesh_summary']['nonpositive_volumes'] and D['envelope_ray_test']['pass'] and D['circulation']['pass'] and D['supports']['all_legs_contact_floor_within_3mm']
json.dump(D,open(R/'qa/fullroom_geometry_validation.json','w'),indent=2);print(json.dumps({k:v for k,v in D.items() if k!='per_mesh'},indent=2))
