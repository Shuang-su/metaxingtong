"""02 cold-state finite butterfly hypothesis, built in local Blender 4.3.2.
Source-pixel contours -> explicit closed 3-D shells; no source-image billboard.
Depth, rear closure and exact dimensions are inference, not photogrammetry.
"""
import bpy, bmesh, math, json, pathlib, hashlib
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
P=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for x in list(bpy.data.materials): bpy.data.materials.remove(x)
S=bpy.context.scene
S.render.engine='CYCLES'; S.cycles.samples=32; S.cycles.use_denoising=True
S.render.threads_mode='FIXED'; S.render.threads=1
S.render.resolution_x=1192;S.render.resolution_y=671;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGBA'
S.view_settings.view_transform='AgX';S.render.film_transparent=False
S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.006,.012,.033,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.4
inventory=[]
def mat(n,col,metal=0,rough=.4,em=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if em:p.inputs['Emission Color'].default_value=(*col,1);p.inputs['Emission Strength'].default_value=em
 return m
rim=mat('M01_silver_violet_visible_veins',(.26,.32,.48),.85,.2)
outer=mat('M02_cold_outer_membrane_proxy',(.2,.35,.66),.48,.27,.18)
inner=mat('M03_pale_blue_inner_panel_proxy',(.57,.79,.94),.25,.23,.36)
azure=mat('M04_cyan_pendant_proxy',(.25,.72,.88),.5,.23,.22)
white=mat('M05_white_luminous_rail_proxy',(.82,.91,1),.12,.25,1)
floor=mat('M06_reflective_floor_no_baked_source',(.07,.09,.18),.75,.16)
black=mat('M07_dark_ground_fixture_proxy',(.009,.012,.022),.6,.32)
tower=mat('M08_visible_tower_arc_proxy',(.11,.15,.27),.8,.25)
clay=mat('M99_neutral_white_clay',(.56,.56,.56),0,.6)
# A restrained procedural surface is explicitly appearance approximation, NOT recovered texture.
for m in [outer,inner,azure]:
 nt=m.node_tree;p=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5;tex.inputs['Detail'].default_value=2
 ramp=nt.nodes.new('ShaderNodeValToRGB');base=list(m.diffuse_color[:3]);ramp.color_ramp.elements[0].color=tuple(c*.55 for c in base)+(1,);ramp.color_ramp.elements[1].color=tuple(min(1,c*1.15) for c in base)+(1,)
 nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],p.inputs['Base Color'])
def register(o,n,m,group,evidence,inferred):
 o.name=n;o.data.materials.clear();o.data.materials.append(m)
 o['scope']='FINITE_COLD_STATE_CANDIDATE_SOURCE_FAILED';o['group']=group;o['source_evidence']=evidence;o['inferred']=inferred
 inventory.append({'object':n,'group':group,'evidence':evidence,'inferred':inferred})
 return o
def mesh(n,vs,fs,m,group='wing',evidence='report-02 visible front contour',inferred='depth, rear closure, thickness and surface topology'):
 d=bpy.data.meshes.new(n);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o)
 bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
 for f in d.polygons:f.use_smooth=True
 return register(o,n,m,group,evidence,inferred)
def smooth(points,closed=False,steps=5):
 p=[Vector(x) for x in points];out=[];N=len(p)
 for i in range(N if closed else N-1):
  p0=p[(i-1)%N] if closed or i else p[i];p1=p[i];p2=p[(i+1)%N];p3=p[(i+2)%N] if closed or i+2<N else p[-1]
  for j in range(steps):
   t=j/steps;out.append(tuple(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)))
 if not closed:out.append(tuple(p[-1]))
 return out
F=1500;W=1192;H=671
def bow(u,v):return .12+.75*(abs(u-596)/596)**1.25+.3*math.sin(math.pi*max(0,min(1,(v-25)/590)))
def unproj(u,v,y):return ((u-596)*(36+y)/F,y,7+(335.5-v)*(36+y)/F)
def uvpoint(uv,front=0):
 u,v=uv;return unproj(u,v,bow(u,v)+front)
def shell(n,outline,m,offset=0,thick=.075,mirror=False):
 pts=smooth(outline,True,4)
 if mirror:pts=[(1192-u,v) for u,v in pts]
 vectors=[Vector((u,v,0)) for u,v in pts]
 tris=tessellate_polygon([vectors]);verts2=[];index={};faces=[]
 def ix(q):
  key=(round(q[0],6),round(q[1],6))
  if key not in index:index[key]=len(verts2);verts2.append(key)
  return index[key]
 def subdiv(a,b,c,depth):
  if depth:
   ab=(a+b)*.5;bc=(b+c)*.5;ca=(c+a)*.5
   for t in [(a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca)]:subdiv(*t,depth-1)
  else:faces.append((ix(a),ix(b),ix(c)))
 for t in tris:subdiv(*[vectors[q] if isinstance(q,int) else q for q in t],1)
 vs=[uvpoint(q,offset) for q in verts2];N=len(vs);vs+= [(x,y+thick,z) for x,y,z in vs]
 fs=list(faces)+[tuple(i+N for i in reversed(f)) for f in faces]
 edges={}
 for f in faces:
  for a,b in zip(f,f[1:]+f[:1]):
   key=tuple(sorted((a,b)));edges.setdefault(key,[]).append((a,b))
 for edge,uses in edges.items():
  if len(uses)==1:
   a,b=uses[0];fs.append((b,a,a+N,b+N))
 return mesh(n,vs,fs,m),pts
def tube(n,points,r,m,closed=False,group='wing_vein',evidence='report-02 visible curve; report-05 local cross-check',inferred='circular cross-section, thickness and depth'):
 pts=[Vector(p) for p in points];vs=[];sides=10
 for j,p in enumerate(pts):
  a=pts[(j-1)%len(pts)] if closed or j else p;b=pts[(j+1)%len(pts)] if closed or j+1<len(pts) else p
  tangent=(b-a).normalized();axis=Vector((0,1,0))
  if abs(axis.dot(tangent))>.95:axis=Vector((1,0,0))
  u=tangent.cross(axis).normalized();v=tangent.cross(u).normalized()
  for k in range(sides):vs.append(tuple(p+r*(u*math.cos(2*math.pi*k/sides)+v*math.sin(2*math.pi*k/sides))))
 fs=[]
 for j in range(len(pts) if closed else len(pts)-1):
  for k in range(sides):a=j*sides+k;b=j*sides+(k+1)%sides;c=((j+1)%len(pts))*sides+(k+1)%sides;d=((j+1)%len(pts))*sides+k;fs.append((a,b,c,d))
 if not closed:fs +=[tuple(reversed(range(sides))),tuple((len(pts)-1)*sides+k for k in range(sides))]
 return mesh(n,vs,fs,m,group,evidence,inferred)
def uvtube(n,pts,r,m,offset=-.08,mirror=False,closed=False):
 pts=smooth(pts,closed,6)
 if mirror:pts=[(1192-u,v) for u,v in pts]
 return tube(n,[uvpoint(q,offset) for q in pts],r,m,closed)
def box(n,loc,scale,m,group,evidence,inferred):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 bevel=o.modifiers.new('finite_edge_bevel','BEVEL');bevel.width=.025;bevel.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=bevel.name)
 return register(o,n,m,group,evidence,inferred)
UL=[(589,410),(550,383),(527,349),(500,297),(469,237),(434,179),(381,128),(323,85),(248,54),(170,32),(100,26),(42,29),(16,40),(43,76),(74,120),(100,169),(126,202),(168,218),(215,224),(224,253),(244,282),(258,319),(284,342),(329,360),(381,372),(441,376),(501,386),(555,406)]
UI=[(521,359),(491,347),(458,362),(409,373),(359,369),(314,356),(290,335),(289,310),(305,293),(276,291),(254,279),(242,255),(235,220),(228,182),(229,141),(245,116),(276,115),(318,129),(361,151),(400,174),(438,211),(468,251),(494,296)]
LL=[(590,410),(555,401),(519,389),(464,376),(408,374),(352,377),(300,390),(253,408),(225,430),(213,453),(216,469),(241,459),(248,449),(226,479),(214,511),(221,542),(247,558),(283,570),(315,588),(346,613),(354,581),(387,585),(425,570),(460,551),(490,522),(520,488),(546,453),(568,425)]
LI=[(550,413),(514,404),(477,400),(444,402),(405,416),(372,438),(347,462),(332,483),(332,498),(351,501),(391,491),(380,507),(361,522),(355,538),(365,547),(382,541),(390,558),(413,551),(442,534),(466,509),(489,478),(514,447)]
PEND=[(549,432),(528,462),(506,502),(485,548),(473,581),(472,604),(484,610),(495,594),(501,605),(511,591),(519,569),(528,548),(535,520),(541,492),(550,457)]
INNERUP=[(568,395),(552,334),(532,275),(503,218),(465,168),(433,140),(420,135),(420,151),(445,190),(466,235),(491,289),(512,338),(539,379)]
wing_specs=[('UPPER',UL,UI),('LOWER',LL,LI)]
for side,mir in [('L',False),('R',True)]:
 for label,outline,inside in wing_specs:
  o,pts=shell(f'WING_{side}_{label}_finite_outer_shell',outline,outer,0,.07,mir)
  tube(f'VEIN_{side}_{label}_outer_boundary',[uvpoint(p,-.04) for p in pts],.035,rim,True)
  o,pts=shell(f'WING_{side}_{label}_visible_pale_panel',inside,inner,-.10,.045,mir)
  tube(f'VEIN_{side}_{label}_pale_boundary',[uvpoint(p,-.14) for p in pts],.04,rim,True)
 for label,poly in [('PENDANT',PEND),('INNER_UPPER',INNERUP)]:
  o,pts=shell(f'WING_{side}_{label}_finite_shell',poly,azure,-.06,.04,mir)
  tube(f'VEIN_{side}_{label}_boundary',[uvpoint(p,-.09) for p in pts],.035,rim,True)
 # Major source-visible curves, not random decorative triangulation.
 paths=[
  [(588,408),(556,390),(530,364),(514,327),(502,290),(488,266),(480,261),(475,275),(482,300),(498,330),(514,354)],
  [(514,350),(487,313),(449,284),(401,255),(377,234),(372,211),(384,199),(405,199),(433,213),(459,241),(479,274)],
  [(491,334),(463,319),(435,300),(411,292),(389,288)],
  [(539,380),(508,332),(482,282),(454,229),(423,186),(393,161)],
  [(532,361),(511,277),(475,208),(443,169)],
  [(352,130),(313,117),(273,109),(233,106),(197,101),(181,82),(163,63),(140,49),(116,42)],
  [(229,214),(196,188),(162,164),(137,146),(112,140)],
  [(589,410),(557,417),(530,432),(506,449),(480,461),(458,465)],
  [(551,415),(523,411),(494,410),(470,414),(449,421),(427,422),(411,421)],
  [(514,414),(487,421),(468,431),(450,439),(427,444)],
  [(533,429),(509,471),(486,510),(467,545),(455,581)],
  [(507,461),(488,483),(465,493),(445,504),(426,517)],
  [(490,489),(467,516),(443,539),(417,553),(391,564),(370,564)],
  [(469,417),(435,433),(409,449),(381,457),(359,460)],
  [(545,453),(531,497),(520,541),(506,581),(489,606)],
  [(533,470),(518,503),(503,539),(487,578),(478,598)],
 ]
 for i,p in enumerate(paths):uvtube(f'VEIN_{side}_major_{i:02d}',p,.025 if i in [5,6,14,15] else .045,rim,mirror=mir)
 # Small source-supported center lozenge/eye form, closed finite shell.
 poly=[(555,414),(534,421),(515,430),(508,444),(521,455),(540,451),(553,439)]
 o,pts=shell(f'WING_{side}_central_eye',poly,azure,-.27,.06,mir)
 tube(f'VEIN_{side}_central_eye_border',[uvpoint(p,-.3) for p in pts],.055,rim,True)
# Midline decorative body and upper slender forks, only visible extent.
for side in [-1,1]:
 def flip(p):return [(596+side*(u-596),v) for u,v in p]
 uvtube(f'BODY_spine_{side}',flip([(596,469),(583,447),(576,422),(583,398),(577,363),(584,334),(578,287),(563,240),(541,191),(514,151),(480,110),(462,76),(459,47),(461,27)]),.048,white,offset=-.25)
 uvtube(f'BODY_lower_loop_{side}',flip([(596,417),(575,440),(565,461),(573,476),(584,466),(586,441),(596,424)]),.027,rim,offset=-.17)
 uvtube(f'BODY_lower_diamond_{side}',flip([(596,423),(582,462),(590,493),(596,505)]),.04,rim,offset=-.08)
 # Central 05 S-profile: this is a visible decorative rail, NOT asserted stair handrail.
 uvtube(f'CENTRAL_S_visible_{side}',flip([(583,519),(571,536),(558,553),(555,570),(560,585),(571,592)]),.07,white,offset=-1.05)
 uvtube(f'CENTRAL_outer_arc_{side}',flip([(582,522),(574,550),(552,571),(527,580),(492,585),(454,590)]),.045,white,offset=-.88)
 for k in range(5):
  u=492+k*14;v=585-(k*1.6);uvtube(f'CENTRAL_visible_vertical_{side}_{k}',flip([(u,v),(u-3,v-20)]),.029,white,offset=-.9)
# Tower front-visible helical ribbon segments. Rear arcs are deliberately absent.
# The visible strips are finite ribbons capped at their observed crop boundaries.
def ribbon(n,uvs,width=.18):
 pts=[Vector(unproj(u,v,2.9)) for u,v in smooth(uvs,False,10)];vs=[]
 for i,p in enumerate(pts):
  t=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();v=t.cross(Vector((0,1,0))).normalized()*width
  for yy,sgn in [(0,-1),(0,1),(.09,-1),(.09,1)]:vs.append(tuple(p+sgn*v+Vector((0,yy,0))))
 fs=[]
 for i in range(len(pts)-1):
  a=i*4;b=(i+1)*4;fs +=[(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)]
 fs +=[(0,1,3,2),tuple((len(pts)-1)*4+j for j in [0,2,3,1])]
 return mesh(n,vs,fs,tower,'tower_visible_fragment','report-02 visible tower arc segment; cropped above frame','rear absent; ribbon width/thickness/depth inferred')
for i,p in enumerate([
 [(514,251),(556,254),(621,240),(680,211),(707,179)],
 [(492,197),(529,174),(582,143),(640,115),(701,100),(734,110),(747,132),(743,157)],
 [(504,116),(523,90),(554,80),(606,81),(653,91),(681,115)],
 [(537,91),(515,62),(514,35),(530,12),(557,1)],
 [(531,0),(578,6),(628,26),(659,50),(677,82)],
 [(565,34),(611,41),(643,27),(663,4)]
]):ribbon(f'TOWER_visible_arc_fragment_{i:02d}',p,.09 if i in [3,4,5] else .17)
for i,p in enumerate([[(558,0),(568,104),(577,203),(582,354)],[(625,0),(620,125),(611,237),(603,364)],[(650,70),(640,167),(625,281),(613,375)]]):
 tube(f'TOWER_visible_vertical_{i}',[unproj(u,v,3.25) for u,v in p],.09,tower,False,'tower_visible_fragment','report-02 visible vertical fragment','depth, cross section, rear omitted')
# Finite reflective stage slab, deliberately no under-stage architectural recovery.
N=160;rx=11.1;ry=3.0;cy=.1;z=.49;vs=[]
for zz in [z,z-.12]:
 for i in range(N):a=2*math.pi*i/N;vs.append((rx*math.cos(a),cy+ry*math.sin(a),zz))
fs=[tuple(range(N)),tuple(reversed(range(N,2*N)))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
mesh('STAGE_finite_reflective_oval',vs,fs,floor,'stage','report-02/05 visible reflective top and front curved border','full ellipse, thickness and unseen bottom closure inferred; not original construction')
# Flat finite bands sit ON slab, never a coplanar duplicate plane.
def ringband(n,rx,ry,cy,z,width,matl):
 vs=[]
 for zz in [z,z+.015]:
  for r in [0,1]:
   for i in range(N):a=2*math.pi*i/N;vs.append(((rx-r*width)*math.cos(a),cy+(ry-r*width*.3)*math.sin(a),zz))
 fs=[]
 for i in range(N):
  j=(i+1)%N;fs +=[(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)]
 return mesh(n,vs,fs,matl,'stage','report-02/05 curved pale floor band','ellipse path, width and rear extent inferred')
ringband('STAGE_finite_front_pale_band',10.6,2.7,.1,.49,.24,white)
# Few observed floor fixtures, counts and exact footprint remain proxies.
for side in [-1,1]:
 for i,(x,y) in enumerate([(7.5,-1.5),(8.5,-1.2),(9.6,-1.1),(4.1,1.4),(3.6,1.8)]):
  box(f'FIXTURE_{side}_{i}_base',(side*x,y,.58),(.36,.32,.18),black,'ground_fixture','report-02/05 dark floor fixtures visible','count/location/shape approximate')
  box(f'FIXTURE_{side}_{i}_head',(side*x,y,.82),(.22,.22,.32),black,'ground_fixture','report-02/05 dark floor fixtures visible','internal lamp and mounting unmeasured')
# Side low wave forms limited to visible scalloped front profile, no city background.
for side,mir in [('L',False),('R',True)]:
 poly=[(0,565),(27,545),(48,548),(72,575),(97,563),(121,576),(145,570),(171,586),(195,572),(225,580),(247,599),(263,620),(0,622)]
 o,pts=shell(f'SIDE_{side}_finite_scallop_front',poly,outer,.8,.12,mir)
 tube(f'SIDE_{side}_visible_scallop_rim',[uvpoint(p,.75) for p in pts],.025,white,True,'side_visible_fragment','report-02 low scalloped luminous silhouette','depth, bottom and rear closure inferred')
 for j,p in enumerate([[(0,448),(57,471),(123,483),(184,496),(231,529)],[(0,367),(63,402),(123,407),(173,381),(219,370),(263,374)],[(0,514),(69,522),(132,525),(196,523)]]):
  uvtube(f'SIDE_{side}_visible_branch_{j}',p,.07,rim,offset=.55,mirror=mir)
# Cameras: one shared geometry. No source05-specific shape changes allowed.
def camera(n,loc,target,lens=45.3020134):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.sensor_width=36;d.clip_end=300;return o
camera('SOURCE02_conditional_front',(0,-36,7),(0,0,7))
camera('SOURCE05_conditional_close',(0,-13.6,1.1),(0,0,1.1))
checks=[('CHECK01_left_front',(-22,-30,12),(0,0,6)),('CHECK02_right_front',(22,-30,12),(0,0,6)),('CHECK03_left_profile',(-32,-3,9),(0,0,6)),('CHECK04_right_profile',(32,3,9),(0,0,6)),('CHECK05_rear_left',(-23,27,13),(0,0,6)),('CHECK06_rear_right',(23,27,13),(0,0,6)),('CHECK07_high_front',(0,-24,29),(0,0,5)),('CHECK08_low_front',(-9,-31,1),(0,0,6))]
for n,loc,target in checks:camera(n,loc,target,39)
S.camera=bpy.data.objects['SOURCE02_conditional_front']
def area(n,loc,target,power,size,col):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=col;o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('DIAGNOSTIC_key',(-9,-13,18),(0,0,6),3500,12,(.68,.8,1))
area('DIAGNOSTIC_fill',(12,-5,10),(0,0,6),2400,10,(.5,.75,1))
area('DIAGNOSTIC_rim',(0,9,16),(0,0,5),3800,8,(.45,.35,1))
S['scope']='Finite 02/05 cold-state front assembly candidate; SOURCE FAILED; no native frame or full scene reconstruction.'
S['units_note']='Relative modeling units, not measured metres.'
S['source_pixels']='1192x671 report screenshots, not decoded native video. Per-video time unknown.'
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA'
with open(P/'docs/R01-object-inventory.json','w') as f:json.dump(inventory,f,ensure_ascii=False,indent=2)
deps={'external_textures':[],'source_images_embedded_in_geometry':False,'all_appearance':'procedural proxy shaders, no recovered texture','blender':bpy.app.version_string,'source_manifest':'sources/manifest.json'}
(P/'dependencies/R01-dependencies.json').write_text(json.dumps(deps,indent=2))
def snapshot(tag):
 bpy.ops.wm.save_as_mainfile(filepath=str(P/f'models/R01_{tag}.blend'))
 bpy.ops.export_scene.gltf(filepath=str(P/f'models/R01_{tag}.glb'),export_format='GLB',export_cameras=True,export_lights=True,export_extras=True,export_apply=True)
snapshot('material')
for o in bpy.data.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(clay)
snapshot('white')
print('R01_FROZEN',len(inventory),'mesh objects')
