import bpy,bmesh,sys,pathlib,json,hashlib,struct,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=pathlib.Path(__file__).resolve().parents[1];stage=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'r03';Q=R/'qa'/stage;Q.mkdir(exist_ok=True,parents=True)
def inventory(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));dg=bpy.context.evaluated_depsgraph_get();out={};cams={}
 for o in bpy.context.scene.objects:
  if o.type=='MESH':
   e=o.evaluated_get(dg);m=e.to_mesh();v=[tuple(o.matrix_world@q.co) for q in m.vertices];f=[tuple(q.vertices) for q in m.polygons];blob=b''.join(struct.pack('<3d',*q) for q in v)+b''.join(struct.pack('<I',len(q))+struct.pack('<'+'I'*len(q),*q) for q in f)
   bm=bmesh.new();bm.from_mesh(m);bm.transform(o.matrix_world);bm.normal_update()
   out[o.name]={'geometry_sha256':hashlib.sha256(blob).hexdigest(),'vertices':len(v),'faces':len(f),'bounds':[[min(q[i] for q in v),max(q[i] for q in v)] for i in range(3)],'boundary_edges':sum(q.is_boundary for q in bm.edges),'nonmanifold_edges':sum(not q.is_manifold for q in bm.edges),'zero_length_edges':sum(q.calc_length()<1e-8 for q in bm.edges),'zero_area_faces':sum(q.calc_area()<1e-12 for q in bm.faces),'volume':bm.calc_volume(signed=True),'visible':not o.hide_render,'inference':o.get('inference','not recorded')};bm.free();e.to_mesh_clear()
  elif o.type=='CAMERA':cams[o.name]={'matrix':[list(row) for row in o.matrix_world],'lens':o.data.lens}
 deps=[]
 for im in bpy.data.images:
  p=pathlib.Path(bpy.path.abspath(im.filepath));deps.append({'image':im.name,'declared':im.filepath,'resolved':str(p),'exists':p.exists(),'packed':bool(im.packed_file),'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None})
 return out,cams,deps
material,cams,deps=inventory(R/'models'/('lakeleaf-'+stage+'-material.blend'))
# Dense ray thickness through the one closed thin-shell mesh, not through reflected water.
o=bpy.data.objects['LEAF_001_ThinConcaveShell'];dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);m=e.to_mesh();verts=[o.matrix_world@v.co for v in m.vertices];tree=BVHTree.FromPolygons(verts,[list(p.vertices) for p in m.polygons]);tests=[]
for i in range(101):
 x=-4.5+9*i/100;u=x/4.65;wid=1.58*max(0,1-u*u)**.72*(1+.06*math.sin(3*math.pi*u))
 for j in range(17):
  y=wid*(-.92+1.84*j/16);loc,n,idx,dist=tree.ray_cast(Vector((x,y,8)),Vector((0,0,-1)),20)
  if loc is not None:
   loc2,n2,idx2,d2=tree.ray_cast(loc+Vector((0,0,-1e-5)),Vector((0,0,-1)),20)
   tests.append({'x':x,'y':y,'first_hit':list(loc),'second_hit':list(loc2) if loc2 else None,'vertical_thickness':d2+1e-5 if loc2 else None})
e.to_mesh_clear();ts=[r['vertical_thickness'] for r in tests if r['vertical_thickness'] is not None]
(Q/'shell-ray-probes.json').write_text(json.dumps({'definition':'Vertical ray distance between first and second shell intersections, not material-normal thickness; not source metric scale','attempted':1717,'first_hits':len(tests),'double_hits':len(ts),'min':min(ts),'max':max(ts),'tests':tests},indent=2)+'\n')
landmarks={
'SOURCE_092142973_SIDE':[('left_apex',(-4.65,0,2.34),(501,1048)),('right_base',(4.65,0,1.69),(3261,1378))],
'SOURCE_100762992_TOP':[('left_apex',(-4.65,0,2.34),(1880,683)),('right_base',(4.65,0,1.69),(2010,1303))]}
repro=[];s=bpy.context.scene;s.render.resolution_x=3840;s.render.resolution_y=2160
for cn,rows in landmarks.items():
 for label,pt,src in rows:
  uv=world_to_camera_view(s,bpy.data.objects[cn],Vector(pt));pix=(uv.x*3840,(1-uv.y)*2160);repro.append({'camera':cn,'point':label,'source_manual_approx_px':src,'source_click_uncertainty_px':16,'render_predicted_px':pix,'residual_px':math.dist(src,pix)})
(Q/'conditional-landmarks.json').write_text(json.dumps({'warning':'Manual approximate tip correspondence only, not camera calibration or source acceptance. No image warp. World tip positions refer to actual shared model.','rows':repro},indent=2)+'\n')
white,wcams,wdeps=inventory(R/'models'/('lakeleaf-'+stage+'-white.blend'))
geom_equal=material.keys()==white.keys() and all(material[k]['geometry_sha256']==white[k]['geometry_sha256'] for k in material)
# Real new scene import of the actual GLB, not a copy of original Blender objects.
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'models'/('lakeleaf-'+stage+'.glb')))
reimport={};icam=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  v=[o.matrix_world@q.co for q in o.data.vertices];reimport[o.name]={'vertices':len(v),'faces':len(o.data.polygons),'bounds':[[min(q[i] for q in v),max(q[i] for q in v)] for i in range(3)]}
 elif o.type=='CAMERA':icam.append(o.name)
missing=sorted(set(material)-set(reimport));bounds_errors=[]
for name in set(material)&set(reimport):
 d=max(abs(material[name]['bounds'][i][j]-reimport[name]['bounds'][i][j]) for i in range(3) for j in range(2))
 if d>1e-4:bounds_errors.append({'object':name,'max_abs_bound_error':d})
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models'/('lakeleaf-'+stage+'-glb-reimport-check.blend')))
report={'stage':stage,'source_accepted':False,'material_mesh_count':len(material),'material_camera_count':len(cams),'camera_roles':'3 source-fit hypotheses + 1 auxiliary close rear + 1 hero + 8 real inspection cameras','material_white_geometry_identical':geom_equal,'camera_sets_identical':cams==wcams,'all_external_images_exist':all(x['exists'] or x['packed'] for x in deps),'dependencies':deps,'all_model_visibility_stable':all(x['visible'] for x in material.values()),'main_shell':material['LEAF_001_ThinConcaveShell'],'glb_reimport_mesh_count':len(reimport),'glb_reimport_camera_count':len(icam),'glb_missing_meshes':missing,'glb_bound_errors_gt_1e4':bounds_errors,'glb_embedded_image_count':len(bpy.data.images),'shell_ray_first_hits':len(tests),'shell_ray_double_hits':len(ts),'intentional_open_surfaces':['lake surface','finite shore surface','individual foliage sheets'],'unsupported_export':['AREA light absent from GLB; colour/view transform and render engine not portable'],'not_tested':['full-scene triangle-triangle collision sweep','all vegetation supports and contacts','true metric thickness','source photometric acceptance','independent later replay','dynamic drift/water/birds/performer']}
(Q/'delivery-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(Q/'material-mesh-inventory.json').write_text(json.dumps(material,ensure_ascii=False,indent=2)+'\n');(Q/'glb-reimport-inventory.json').write_text(json.dumps(reimport,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
