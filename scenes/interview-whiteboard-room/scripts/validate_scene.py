"""Independent reopen/evaluated mesh check and actual GLB import, no visual acceptance inferred.
Run after build: blender -b -t 8 -P scripts/validate_scene.py
"""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'models/r05';QA=ROOT/'qa/r05'
report={'status':'candidate; geometry/file checks separate from source fidelity','checks':{},'limitations':[]}

def stats():
    s=bpy.context.scene;dep=bpy.context.evaluated_depsgraph_get();rows=[]
    for o in sorted([x for x in s.objects if x.type=='MESH'],key=lambda x:x.name):
        ev=o.evaluated_get(dep);me=ev.to_mesh();me.calc_loop_triangles()
        verts=[o.matrix_world@v.co for v in me.vertices]
        triangles=sorted(tuple(sorted(tuple(round(float(c),6) for c in verts[vi]) for vi in tri.vertices)) for tri in me.loop_triangles)
        geometry_hash=hashlib.sha256(json.dumps(triangles,separators=(',',':')).encode()).hexdigest()
        bm=bmesh.new();bm.from_mesh(me)
        boundaries=sum(e.is_boundary for e in bm.edges);nonman=sum(not e.is_manifold for e in bm.edges)
        area_zero=sum(f.calc_area()<1e-11 for f in bm.faces)
        volume=bm.calc_volume(signed=True);bm.free()
        rows.append({'name':o.name,'stable_id':o.get('stable_id'),'vertices':len(me.vertices),'triangles':len(me.loop_triangles),
          'boundary_edges':boundaries,'nonmanifold_edges':nonman,'zero_area_faces':area_zero,'signed_volume':volume,
          'bounds_min':[min(v[i] for v in verts) for i in range(3)],'bounds_max':[max(v[i] for v in verts) for i in range(3)],
          'materials':[m.name for m in me.materials if m],'world_triangle_coordinates_sha256_round6':geometry_hash})
        ev.to_mesh_clear()
    return rows

bpy.ops.wm.open_mainfile(filepath=str(OUT/'interview-room-material.blend'))
original=stats();report['original_evaluated_objects']=original
report['checks']['solid_manifold_except_explicit_decal']=all(r['nonmanifold_edges']==0 for r in original if r['stable_id']!='BOARD-TEXT')
report['checks']['no_zero_area_faces']=all(r['zero_area_faces']==0 for r in original)
report['checks']['positive_solid_volume']=all(r['signed_volume']>0 for r in original if r['stable_id']!='BOARD-TEXT')
report['checks']['all_objects_have_provenance']=all(r['stable_id'] for r in original)
report['explicit_non_solid_exception']='BOARD-TEXT single bounded UV decal plane backed by solid sandwich;4 boundary edges expected'

# Dense shell rays: shell only, directions cover full sphere from three interior samples.
dep=bpy.context.evaluated_depsgraph_get();vv=[];ff=[]
for o in bpy.context.scene.objects:
    if o.type=='MESH' and o.name.startswith('ROOM.'):
        me=o.evaluated_get(dep).to_mesh();offset=len(vv)
        vv.extend([o.matrix_world@v.co for v in me.vertices]);ff.extend([tuple(offset+i for i in p.vertices) for p in me.polygons])
        o.evaluated_get(dep).to_mesh_clear()
tree=BVHTree.FromPolygons(vv,ff)
points=[(0,-2,1.2),(0,-5.5,1.3),(0,.12,1.0)]
miss=[];samples=2048
for pi,pt in enumerate(points):
    for i in range(samples):
        z=1-2*(i+.5)/samples;a=i*math.pi*(3-math.sqrt(5));rr=math.sqrt(1-z*z)
        direction=Vector((rr*math.cos(a),rr*math.sin(a),z))
        loc,n,idx,dist=tree.ray_cast(Vector(pt),direction,100)
        if loc is None:miss.append([pi,i])
report['shell_rays']={'origins':points,'rays_per_origin':samples,'total':len(points)*samples,'misses':miss}
report['checks']['dense_shell_rays_closed']=not miss

# Floor-contact checks are evaluated bounds, no unverified global collision pass.
ground=[r for r in original if r['stable_id'].startswith(('TABLE-PAD','BOARD-PAD','CHAIR-PAD'))]
report['ground_contact']=[{'id':r['stable_id'],'min_z':r['bounds_min'][2],'max_abs_gap_limit':1e-6} for r in ground]
report['checks']['support_pads_touch_floor_1e6']=all(abs(r['bounds_min'][2])<1e-6 for r in ground)
cfg=json.loads((ROOT/'docs/camera-fit-r03.json').read_text());g=cfg['geometry']
ob={r['stable_id']:r for r in original}
report['clearances']={'board_back_to_wall':g['wall_y']-max(r['bounds_max'][1] for r in original if r['stable_id'].startswith('BOARD-')),
 'table_left_to_wall':min(r['bounds_min'][0] for r in original if r['stable_id'].startswith('TABLE-'))-(-g['wall_half']),
 'table_right_to_wall':g['wall_half']-max(r['bounds_max'][0] for r in original if r['stable_id'].startswith('TABLE-')),
 'chair_seat_to_apron_z':min(r['bounds_min'][2] for r in original if r['stable_id'].startswith('TABLE-APRON'))-ob['CHAIR-SEAT']['bounds_max'][2]}
report['checks']['positive_listed_clearances']=all(v>0 for v in report['clearances'].values())
cam=[]
for o in bpy.context.scene.objects:
    if o.type=='CAMERA':
        x,y,z=o.location
        inside=(-g['wall_half']<x<g['wall_half'] and -7<y<g['wall_y'] and 0<z<2.8)
        cam.append({'name':o.name,'location':list(o.location),'inside_conservative_inner_box':inside})
report['cameras']=cam;report['checks']['all_cameras_inside_shell']=all(c['inside_conservative_inner_box'] for c in cam)
report['limitations']+=['Dense shell rays are samples, not exhaustive topology proof of room union.',
 'No hidden opening or metric dimensions confirmed by these checks.',
 'Contact uses evaluated bounds and listed clearances; joined frame overlaps intentional. Not a complete all-pairs collision proof.']

def actual_reimport(name):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(OUT/name))
    rows=stats();orig={r['name']:r for r in original};deltas=[]
    for r in rows:
        o=orig.get(r['name'])
        if o:deltas.append(max(abs(a-b) for key in ['bounds_min','bounds_max'] for a,b in zip(r[key],o[key])))
    data={'file':name,'imported_meshes':len(rows),'triangles':sum(r['triangles'] for r in rows),
      'original_evaluated_triangles':sum(r['triangles'] for r in original),'matched_names':len(deltas),'max_bounds_delta':max(deltas) if deltas else None,
      'material_count':len(bpy.data.materials),'image_count':len(bpy.data.images),
      'mesh_objects':rows,'source_geometry_signature_status':'bounds/triangles independently checked; not merely header validation'}
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(QA/(name.replace('.glb','-reimport.blend'))))
    return data
report['material_glb_reimport']=actual_reimport('interview-room-material.glb')
report['white_glb_reimport']=actual_reimport('interview-room-white.glb')
for role in ['material','white']:
    r=report[role+'_glb_reimport'];report['checks'][role+'_glb_reimport_geometry']=r['matched_names']==len(original) and r['triangles']==r['original_evaluated_triangles'] and r['max_bounds_delta']<1e-5
report['checks']['material_glb_includes_textures']=report['material_glb_reimport']['image_count']>=2
report['checks']['white_glb_single_material']=report['white_glb_reimport']['material_count']==1
matgeo={r['name']:r['world_triangle_coordinates_sha256_round6'] for r in report['material_glb_reimport']['mesh_objects']}
whitegeo={r['name']:r['world_triangle_coordinates_sha256_round6'] for r in report['white_glb_reimport']['mesh_objects']}
report['checks']['actual_material_white_glb_triangle_coordinates_identical']=matgeo==whitegeo
report['all_listed_checks_pass']=all(report['checks'].values())
(QA/'geometry-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'checks':report['checks'],'clearances':report['clearances'],'all_listed_checks_pass':report['all_listed_checks_pass']},indent=2))
