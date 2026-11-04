import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R=Path('/workspace/scratch/fa58bfcf0425/forest-diagnostic-replay-20261104');O=Path('/workspace/scratch/fa58bfcf0425/independent-forest-replay-qa-20261104')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snap():
 meshes={};cams={}
 for ob in bpy.context.scene.objects:
  if ob.type=='MESH':
   vs=[tuple(ob.matrix_world@v.co) for v in ob.data.vertices];fs=[list(p.vertices) for p in ob.data.polygons]
   meshes[ob.name]={'v':vs,'f':fs,'sha':hashlib.sha256(repr((vs,fs)).encode()).hexdigest(),'hidden':ob.hide_render}
  elif ob.type=='CAMERA':
   cams[ob.name]={'matrix':[list(x) for x in ob.matrix_world],'rays':[[v.x/-v.z,v.y/-v.z] for v in ob.data.view_frame(scene=bpy.context.scene)]}
 return meshes,cams

res={};old={};name='TREE_background_03'
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'models/R13_root-diagnostic_{mode}.blend'));om,oc=snap()
 p=R/f'models/R14_anchor-diagnostic_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(p));mm,cc=snap();changed=[i for i,(a,b) in enumerate(zip(om[name]['v'],mm[name]['v'])) if a!=b];other=[k for k,v in om.items() if k!=name and v['sha']!=mm[k]['sha']]
 grass=mm[name];bed=mm['TERRAIN_finite_working_domain'];bt=BVHTree.FromPolygons(bed['v'],bed['f']);rows=[]
 for i in range(12):
  oldpoint=Vector(om[name]['v'][i]);newpoint=Vector(grass['v'][i]);upper=bt.ray_cast(Vector((newpoint.x,newpoint.y,100)),Vector((0,0,-1)),200)[0];lower=bt.ray_cast(newpoint,Vector((0,0,-1)),2)[0];rows.append({'vertex':i,'old_gap':float(oldpoint.z-upper.z),'z_move':float(newpoint.z-oldpoint.z),'new_z':float(newpoint.z),'terrain_top':float(upper.z),'terrain_bottom_hit':float(lower.z)if lower else None,'between_hits':bool(lower is not None and lower.z<newpoint.z<upper.z)})
 pairs=BVHTree.FromPolygons(grass['v'],grass['f']).overlap(bt)
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);top={'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.calc_area()<1e-12 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True)};bm.free()
 uv={o.name:[[(float(t.uv.x),float(t.uv.y)) for t in l.data]for l in o.data.uv_layers] for o in bpy.context.scene.objects if o.type=='MESH'}
 res[mode]={'blend_sha':sha(p),'changed_vertices':changed,'changed_other_meshes':other,'xy_unchanged':all(om[name]['v'][i][:2]==mm[name]['v'][i][:2]for i in changed),'faces_unchanged':om[name]['f']==mm[name]['f'],'cameras_unchanged':oc==cc,'geometry_hashes':{k:v['sha'] for k,v in mm.items()},'topology':top,'rows':rows,'terrain_intersection_pairs':len(pairs)}
 bpy.ops.wm.read_factory_settings(use_empty=True);g=p.with_suffix('.glb');bpy.ops.import_scene.gltf(filepath=str(g));gm,gc=snap();errs={}
 for n,m in mm.items():
  ta=KDTree(len(m['v']));tb=KDTree(len(gm[n]['v']))
  for i,v in enumerate(m['v']):ta.insert(v,i)
  for i,v in enumerate(gm[n]['v']):tb.insert(v,i)
  ta.balance();tb.balance();errs[n]=max(max(ta.find(v)[2] for v in gm[n]['v']),max(tb.find(v)[2]for v in m['v']))
 res[mode]['glb']={'sha':sha(g),'meshes':len(gm),'cams':len(gc),'world_vertex_error':max(errs.values()),'grass_error':errs[name],'missing':list(set(mm)-set(gm)),'camera_ray_error':max(abs(cc[n]['rays'][i][j]-gc[n]['rays'][i][j]) for n in cc for i in range(4)for j in range(2))}
res['material_white_geometry_equal']=res['material']['geometry_hashes']==res['white']['geometry_hashes']
(O/'R14-independent-check.json').write_text(json.dumps(res,indent=2));print('DONE')
