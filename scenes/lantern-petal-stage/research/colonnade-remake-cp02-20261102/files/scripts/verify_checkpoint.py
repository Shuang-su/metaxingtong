import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=Path(__file__).resolve().parents[1];r={};snaps={}
def snap():
 d={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  v=[o.matrix_world@x.co for x in o.data.vertices];d[o.name]={'geometry':hashlib.sha256(str(([list(x.co) for x in o.data.vertices],[list(x.vertices) for x in o.data.polygons],[list(x) for x in o.matrix_world])).encode()).hexdigest(),'bb':[[min(x[k] for x in v) for k in range(3)],[max(x[k] for x in v) for k in range(3)]]}
 return d
def obb(o):
 vs=[x.co for x in o.data.vertices];lo=Vector([min(v[k] for v in vs) for k in range(3)]);hi=Vector([max(v[k] for v in vs) for k in range(3)]);axes=[Vector(o.matrix_world.to_3x3().col[i]) for i in range(3)];lengths=[x.length for x in axes];return o.matrix_world@((lo+hi)/2),[x.normalized() for x in axes],[(hi[k]-lo[k])/2*lengths[k] for k in range(3)]
def sat(a,b):
 ca,A,ha=obb(a);cb,B,hb=obb(b);dirs=A+B+[x.cross(y).normalized() for x in A for y in B if x.cross(y).length>1e-8];delta=cb-ca;m=[sum(ha[i]*abs(n.dot(A[i])) for i in range(3))+sum(hb[i]*abs(n.dot(B[i])) for i in range(3))-abs(n.dot(delta)) for n in dirs];return {'intersection':min(m)>=-1e-8,'minimum_overlap':float(min(m))}
for typ in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/NOV2_CP01_{typ}.blend'));s=bpy.context.scene;snaps[typ]=a=snap()
 if typ=='material':
  links=[]
  for i in range(7):
   n=f'GRILLE_{i}'
   for x,y in [('_inner_top','_frame1'),('_inner_bottom','_frame3'),('_inner_top','_stem_R'),('_inner_bottom','_stem_L')]:links.append({'a':n+x,'b':n+y,**sat(bpy.data.objects[n+x],bpy.data.objects[n+y])})
  r['selected_28_links']=links;r['all_selected_links_intersect']=all(x['intersection'] for x in links);trees=[];top={}
  for o in s.objects:
   if o.type!='MESH':continue
   edges={}
   for p in o.data.polygons:
    for e in p.edge_keys:edges[e]=edges.get(e,0)+1
   top[o.name]={'boundary':sum(x==1 for x in edges.values()),'nonmanifold':sum(x!=2 for x in edges.values())};trees.append((o.name,BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])))
  def hits(x,z):return [n for n,t in trees if t.ray_cast(Vector((x,2,z)),Vector((0,-1,0)),4)[0] is not None]
  r['mesh_edge_checks']=top;r['grille_holes']=[hits(.2+(i+.5)*2.6/7,3.46) for i in range(7)];r['grille_bars']=[hits(.2+i*2.6/7+.018,3.46) for i in range(7)];r['bracket_holes']=[hits(x,3.1) for x in [.6,2.4]];r['base_floor_gap']={n:a[n]['bb'][0][2]-a['FLOOR_finite_module_cut']['bb'][1][2] for n in ['COL_0_base_0','COL_1_base_0']}
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(D/f'models/NOV2_CP01_{typ}.glb'));b=snap();common=set(a)&set(b);r[typ+'_roundtrip']={'source_count':len(a),'reimport_count':len(b),'missing':sorted(set(a)-set(b)),'extra':sorted(set(b)-set(a)),'max_bbox_delta':max(abs(a[n]['bb'][j][k]-b[n]['bb'][j][k]) for n in common for j in range(2) for k in range(3))}
r['same_white_material_geometry']=snaps['material']==snaps['white'];r['scope']='new Nov2 execution; limited individual-mesh/selected-gap/selected-cuboid-connection/transport checks, not source acceptance or full structural proof';(D/'qa/verification-NOV2_CP01.json').write_text(json.dumps(r,indent=2))
