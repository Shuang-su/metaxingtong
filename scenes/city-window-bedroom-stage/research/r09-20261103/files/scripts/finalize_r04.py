import bpy,math,json
from mathutils import Vector
from pathlib import Path
D=Path(__file__).resolve().parents[1]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R03_{mode}.blend'));s=bpy.context.scene
 def rod(n,a,b,r,mat):
  d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);o['observation_status']='Hidden support inferred; not source confirmed';o['object_role']='SUPPORT';return o
 for o in list(s.objects):
  if o.type!='MESH':continue
  im=o.matrix_world.inverted()
  if o.name.startswith('WALL_arch_spandrel'):
   for v in o.data.vertices:
    w=o.matrix_world@v.co
    if abs(w.z-7.348)<.002:w.z=7.42;v.co=im@w
  if o.name.startswith('BARSTOOL') and '_leg' in o.name:
   zmin=min((o.matrix_world@v.co).z for v in o.data.vertices);o.location.z-=zmin
  if o.name=='LAMP_base':o.location.z-=min((o.matrix_world@v.co).z for v in o.data.vertices)
  if o.name.startswith('BED_head_arch'):o.location.y-=.035
  if o.name.startswith('BED_foot_arch'):o.location.y+=.035
 m=bpy.data.objects['LAMP_stem'].data.materials[0]
 for j in range(3):
  a=2*math.pi*j/3;rod(f'SUPPORT_lampshade_spider_{j}',(-5.45,2.8,2.7),(-5.45+.38*math.cos(a),2.8+.38*math.sin(a),2.7),.009,m)
 # Curtain top cross-rail and short wall brackets: engineering hypothesis, shared all views.
 m=bpy.data.objects['WINDOW_central_mullion'].data.materials[0]
 rod('SUPPORT_curtain_rail',(-3.1,4.78,6.76),(5.9,4.78,6.76),.035,m)
 for x in [-3.1,1.4,5.9]:rod('SUPPORT_curtain_bracket_'+str(x),(x,4.78,6.76),(x,5.23,6.76),.028,m)
 def camera(n,loc,target,lens):
  c=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,c);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();c.lens=lens;c.clip_start=.02;c.clip_end=200
 camera('SOURCE_D_low',(.2,-3.8,.65),(0,2,1.5),28)
 camera('SOURCE_E_oblique',(-.8,-3.6,1.25),(.1,2.1,1.7),30)
 camera('SOURCE_F_fan4k',(-2.2,-3.8,1.4),(.3,2.1,1.65),32)
 # Inspection views retained as fixed complete-scene views, no per-view hiding.
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/R04_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/R04_{mode}.glb'),export_format='GLB',export_apply=True)
(D/'qa/R04-changes.json').write_text(json.dumps({'technical_changes':['Closed 0.072 working unit rear top gap created by R03 vertical scale; roof underside stays z7.42.','Lowered wooden stool leg bottom vertices to ground; central lamp base to ground.','Bed arch bars shifted 0.035 into bed frame joint region.','Added inferred lamp shade spider, curtain rail and brackets; not observed construction.'],'camera_additions':'D low, E slight oblique and F stronger fan4K oblique, all conditional guesses on same geometry.','limits':'No global collision/source acceptance. Curtain top/rail contact and windows remain hypotheses.'},indent=2))
