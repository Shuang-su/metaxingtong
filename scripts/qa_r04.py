import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'stages/r04-review-candidate';Q=O/'qa';Q.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(O/'harbor-r04-white.blend'));sc=bpy.context.scene
obs=[o for o in sc.objects if o.type=='MESH'];rows=[];bvhs={};points={};bounds={}
for ob in obs:
    bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world)
    rows.append({'id':ob.name,'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'signed_world_volume':bm.calc_volume(signed=True)})
    points[ob.name]=[v.co.copy() for v in bm.verts];bounds[ob.name]=[[min(v[k] for v in points[ob.name]) for k in range(3)],[max(v[k] for v in points[ob.name]) for k in range(3)]];bvhs[ob.name]=BVHTree.FromBMesh(bm,epsilon=1e-7);bm.free()
(Q/'all-object-topology.json').write_text(json.dumps(rows,indent=2))
# Dense floor coverage with real triangle rays. Fixtures intentionally excluded from floor-only mesh set.
floor=[bvhs[n] for n in ['PLATFORM_MAIN','PLATFORM_OUTER_APRON']];floor_rays=[]
for ix in range(81):
 for iy in range(81):
    x=-6.6+13.2*ix/80;y=-6.6+13.2*iy/80
    if x*x+y*y>6.6**2:continue
    hits=[b.ray_cast(Vector((x,y,2)),Vector((0,0,-1)),3)[0] for b in floor];zs=[p.z for p in hits if p is not None]
    floor_rays.append({'x':x,'y':y,'hit':bool(zs),'z':max(zs) if zs else None})
feet={}
for n in ['FRAME_L','FRAME_R']:
    low=min(v.z for v in points[n]);bottom=[v for v in points[n] if abs(v.z-low)<1e-6];dist=[]
    for v in bottom:
        hits=[b.ray_cast(v+Vector((0,0,.01)),Vector((0,0,-1)),.1)[0] for b in floor];zs=[p.z for p in hits if p is not None];dist.append(v.z-max(zs) if zs else None)
    feet[n]={'min_z':low,'bottom_vertices':len(bottom),'gaps_to_floor':dist,'interpretation':'current inferred flush construction, not source-measured root design'}
(Q/'dense-floor-rays-and-feet.json').write_text(json.dumps({'floor_ray_count':len(floor_rays),'edge_hit_height_residuals':[r for r in floor_rays if r['hit'] and abs(r['z']-.75)>1e-5],'misses':[r for r in floor_rays if not r['hit']],'max_abs_floor_height_error':max(abs(r['z']-.75) for r in floor_rays if r['hit']),'feet':feet,'units':'model units only, no physical avatar clearance claim'},indent=2))
# A portal clearance diagnostic, not a human accessibility certification.
portal=[]
for ix in range(49):
 for iz in range(37):
    x=-2.4+4.8*ix/48;z=.85+2.4*iz/36;origin=Vector((x,-2,z));d=Vector((0,1,0));hit=[]
    for n in ['FRAME_L','FRAME_R','CROWN_SAUCER']:
        p,normal,idx,t=bvhs[n].ray_cast(origin,d,5)
        if p is not None:hit.append(n)
    portal.append({'x':x,'z':z,'blocked_by':hit})
(Q/'portal-rays.json').write_text(json.dumps({'ray_count':len(portal),'meaning':'5 model-unit forward rays through visible opening; blocked samples are geometry, not automatically defects','rays':portal},indent=2))
# Actual world-space core surface contacts. Keep broad overlaps as candidates, not blanket failures.
exclude=('ENV_','PALM_','LIGHTHOUSE_','YACHT_','SAILBOAT_','UMBRELLA_','SURFBOARD_','NEON_PROP_')
core=[o for o in obs if not o.name.startswith(exclude)];pairs=[]
for i,a in enumerate(core):
 for b in core[i+1:]:
    aa,bb=bounds[a.name],bounds[b.name]
    if any(aa[1][k]<bb[0][k]-1e-5 or bb[1][k]<aa[0][k]-1e-5 for k in range(3)):continue
    overlaps=bvhs[a.name].overlap(bvhs[b.name])
    if overlaps:pairs.append({'a':a.name,'b':b.name,'triangle_pairs':len(overlaps),'classification':'reviewed as contact/embedded connection candidate; not a zero-collision proof'})
(Q/'core-assembly-contacts.json').write_text(json.dumps({'method':'actual world triangle BVH overlap after AABB broad phase; no OBB-only acceptance','core_objects':len(core),'candidate_pairs':pairs,'limitations':'Containment/hidden hardware and physical stability not fully proven; natural-ground/vegetation/background intentionally separated from core assembly check'},indent=2))
base_bounds=bounds;imports=[]
for state in ['white','material']:
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(O/('harbor-r04-'+state+'.glb')));obs2=[o for o in bpy.context.scene.objects if o.type=='MESH'];out={};top=[]
    for ob in obs2:
        vs=[ob.matrix_world@v.co for v in ob.data.vertices];out[ob.name]=[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]]
        # glTF UV seams split vertices: merge coincident positions only for manifold diagnostics.
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);top.append({'id':ob.name,'seam_weld_tolerance_model_units':1e-5,'welded_nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces)});bm.free()
    deltas=[{'id':n,'max_bbox_delta':max(abs(base_bounds[n][j][k]-out[n][j][k]) for j in range(2) for k in range(3))} for n in base_bounds.keys()&out.keys()]
    imports.append({'state':state,'actual_import':True,'input_mesh_count':len(base_bounds),'import_mesh_count':len(out),'missing':sorted(base_bounds.keys()-out.keys()),'extra':sorted(out.keys()-base_bounds.keys()),'max_bbox_delta':max(d['max_bbox_delta'] for d in deltas),'bbox_deltas':deltas,'welded_topology':top,'embedded_images':[{'name':im.name,'dimensions':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images if im.type=='IMAGE'],'scope':'geometry/material-image survival only; no source acceptance or identical renderer claim'})
(Q/'actual-glb-reimports.json').write_text(json.dumps(imports,indent=2))
print('QA_READY',len(rows),len(floor_rays),len(portal),len(pairs))
