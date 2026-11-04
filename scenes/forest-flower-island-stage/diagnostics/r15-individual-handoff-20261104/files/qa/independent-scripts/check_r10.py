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
res={'models':{},'roundtrip':{},'contact':[]}
for mode in ['material','white']:
 p=R/f'models/R10_support-diagnostic_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(p));meshes,cams=snap();res['models'][mode]={'sha256':sha(p),'mesh_count':len(meshes),'camera_count':len(cams),'geometry':{k:v['sha'] for k,v in meshes.items()},'cameras':cams}
 if mode=='material':
  bt=meshes['ISLAND_moss_bedding_inferred'];bed=BVHTree.FromPolygons(bt['v'],bt['f'])
  for name,m in meshes.items():
   if not name.endswith('_inferred_stems'):continue
   ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);bad=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-12 for f in bm.faces);vol=bm.calc_volume(signed=True);bm.free()
   head=meshes[name.removesuffix('_inferred_stems')];rows=[]
   for i in range(len(m['v'])//16):
    a=i*16;b=i*30
    sf=[[v-a for v in f] for f in m['f'] if all(a<=v<a+16 for v in f)];hf=[[v-b for v in f] for f in head['f'] if all(b<=v<b+30 for v in f)]
    st=BVHTree.FromPolygons(m['v'][a:a+16],sf);ht=BVHTree.FromPolygons(head['v'][b:b+30],hf)
    rows.append({'stem':i,'stem_faces':len(sf),'head_faces':len(hf),'head_intersects':bool(st.overlap(ht)),'bed_intersects':bool(st.overlap(bed))})
   res['contact'].append({'name':name,'nonmanifold_edges':bad,'degenerate_faces':deg,'signed_volume':vol,'stems':len(rows),'rows':rows})
 bpy.ops.wm.read_factory_settings(use_empty=True);g=p.with_suffix('.glb');bpy.ops.import_scene.gltf(filepath=str(g));gm,gc=snap();errors={}
 for name,m in meshes.items():
  if name not in gm:continue
  a=m['v'];b=gm[name]['v'];ta=KDTree(len(a));tb=KDTree(len(b))
  for i,v in enumerate(a):ta.insert(v,i)
  for i,v in enumerate(b):tb.insert(v,i)
  ta.balance();tb.balance();errors[name]=max(max(ta.find(v)[2] for v in b),max(tb.find(v)[2] for v in a))
 ce={}
 for n,c in cams.items():
  if n in gc:ce[n]={'matrix_max':max(abs(c['matrix'][i][j]-gc[n]['matrix'][i][j]) for i in range(4) for j in range(4)),'ray_slope_max':max(abs(c['rays'][i][j]-gc[n]['rays'][i][j]) for i in range(4) for j in range(2))}
 res['roundtrip'][mode]={'glb_sha256':sha(g),'meshes':len(gm),'cameras':len(gc),'missing':sorted(set(meshes)-set(gm)),'extra':sorted(set(gm)-set(meshes)),'world_vertex_bidirectional_max':max(errors.values()),'stem_vertex_errors':{k:v for k,v in errors.items() if k.endswith('_inferred_stems')},'camera_errors':ce}
res['material_white_geometry_equal']=res['models']['material']['geometry']==res['models']['white']['geometry'];res['material_white_cameras_equal']=res['models']['material']['cameras']==res['models']['white']['cameras']
bpy.ops.wm.open_mainfile(filepath=str(R/'models/R09_material.blend'));old,_=snap();new=res['models']['material']['geometry'];res['old625_changed']=[k for k,v in old.items() if new.get(k)!=v['sha']]
(O/'R10-independent-check.json').write_text(json.dumps(res,indent=2));print('DONE',sum(x['stems'] for x in res['contact']),res['material_white_geometry_equal'],res['old625_changed'])
