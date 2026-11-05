import bpy,os,json,math,hashlib
from mathutils import Vector
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Manually estimated original-source04 pixel coordinates, not exact segmentation.
outline=[(290,162),(296,164),(304,176),(316,188),(330,198),(337,204),(339,215),(337,233),(336,246),(331,252),(322,255),(313,253),(307,246),(297,248),(289,244),(286,236),(284,231),(278,227),(278,218),(283,214),(279,207),(279,199),(283,193),(280,185),(281,174),(285,165)]
patches=[[(282,188),(293,197),(308,204),(329,209),(333,216),(316,217),(299,210),(286,205),(281,199)],[(281,208),(292,215),(308,220),(324,221),(328,228),(312,232),(297,226),(284,222),(280,217)]]
curl=[(328,216),(323,213),(318,214),(316,219),(316,226),(319,230),(326,230),(329,228)]
def smooth(pts,n=2):
 for _ in range(n):pts=[q for i,a in enumerate(pts) for q in [tuple(.75*a[k]+.25*pts[(i+1)%len(pts)][k] for k in range(2)),tuple(.25*a[k]+.75*pts[(i+1)%len(pts)][k] for k in range(2))]]
 return pts
def world(p,side):
 # Width .73, height1.13, root x=-1.50; symmetry is an explicit hypothesis.
 x=-1.50-(339-p[0])*.73/(339-278);z=2.73+(255-p[1])*1.13/(255-162)
 return (x if side=='L' else -x,z)
def material(n,c,emission=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=.38;bs.inputs['Emission Color'].default_value=(*c,1);bs.inputs['Emission Strength'].default_value=emission;return m
def shell(n,coords,side,front,back,mat):
 q=[world(p,side) for p in smooth(coords)];N=len(q);v=[(x,y,z) for y in [front,back] for x,z in q];faces=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];me=bpy.data.meshes.new(n);me.from_pydata(v,[],faces);me.update();o=bpy.data.objects.new(n,me);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);return o
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=r+'/models/'+mode+'.blend');s=bpy.context.scene;before={o.name for o in s.objects};base=material('WING pale pink front',(.9,.30,.62),.35);layer=material('WING layered pink proxy',(.95,.42,.72),.25);line=material('WING curl color mark proxy',(.50,.035,.22),.15);letters=material('SIGN font proxy ivory',(1,.8,.95),.7)
 for side in ['L','R']:
  shell('SIGN_'+side+'_closed_shallow_wing',outline,side,3.16,3.215,base)
  for i,p in enumerate(patches):shell('SIGN_'+side+'_layer_'+str(i),p,side,3.13,3.17,layer)
  cu=bpy.data.curves.new('SIGN_'+side+'_curl_proxy','CURVE');cu.dimensions='3D';cu.resolution_u=16;cu.bevel_depth=.013;cu.bevel_resolution=3;cu.use_fill_caps=True;sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(curl)-1)
  for b,p in zip(sp.bezier_points,curl):
   x,z=world(p,side);b.co=(x,3.15,z);b.handle_left_type='AUTO';b.handle_right_type='AUTO'
  ob=bpy.data.objects.new(cu.name,cu);s.collection.objects.link(ob);ob.data.materials.append(line);bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False)
 font=bpy.data.fonts.load(r+'/fonts/NotoSansCJK-Regular.ttc');cu=bpy.data.curves.new('SIGN_QQ炫舞_font_proxy','FONT');cu.body='QQ炫舞';cu.font=font;cu.size=1;cu.align_x='CENTER';cu.align_y='BOTTOM_BASELINE';cu.extrude=.025;cu.bevel_depth=.003;cu.bevel_resolution=2;cu.resolution_u=8;o=bpy.data.objects.new(cu.name,cu);s.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);o=bpy.context.view_layer.objects.active
 # Font localXY becomes worldXZ. Bounds normalised as proxy, not original font reconstruction.
 vs=[v.co for v in o.data.vertices];mn=[min(v[i] for v in vs) for i in range(3)];mx=[max(v[i] for v in vs) for i in range(3)]
 for v in o.data.vertices:
  x=-1.5+(v.co.x-mn[0])/(mx[0]-mn[0])*3.0;z=2.76+(v.co.y-mn[1])/(mx[1]-mn[1])*.79;y=3.18-v.co.z;v.co=(x,y,z)
 o.data.materials.append(letters)
 new=[o for o in s.objects if o.name not in before and o.type=='MESH']
 if mode=='white':
  w=bpy.data.materials['DIAGNOSTIC shared white']
  for o in new:o.data.materials.clear();o.data.materials.append(w)
 for o in new:
  bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=r+'/models/'+mode+'.blend');bpy.ops.export_scene.gltf(filepath=r+'/models/'+mode+'.glb',export_format='GLB',export_cameras=True,export_lights=False)
 if mode=='material':
  for name in ['SOURCE03 conditional','SOURCE04 conditional']:
   s.camera=bpy.data.objects[name];s.cycles.samples=4;s.cycles.use_denoising=False;s.render.resolution_percentage=100;s.render.filepath=r+'/renders/sign-r00-'+name.split()[0]+'-4s.png';bpy.ops.render.render(write_still=True)
 json.dump({'mode':mode,'new_meshes':[o.name for o in new],'font_loaded_name':font.name,'outline_source04_manual_pixels':outline,'layer_source04_manual_pixels':patches,'curl_source04_manual_pixels':curl,'smoothing':'two Chaikin corner-cutting rounds; generated interpolation, not precise tracing','right_wing':'mirrored template is inferred, lower source04 contour null; source03 partial cross-check only','depths':'back/closed thickness and layers all inferred; no mounting or backing plate','base_read_from':'a65 final four models cloned into independent worktree; add only, no old geometry/camera/light edits'},open(r+'/qa/sign-'+mode+'-construction.json','w'),indent=2)
print('WING_SIGN_BUILD_COMPLETE')
