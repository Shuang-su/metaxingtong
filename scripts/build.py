import bpy, math, json, os, sys
from mathutils import Matrix,Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=4
s.render.resolution_x=1080;s.render.resolution_y=603;s.render.resolution_percentage=100;s.render.film_transparent=True
s.view_settings.view_transform='Standard';s.world.color=(.22,.22,.22)
fit=json.load(open(R/'qa/camera-fit.json'));T=Matrix(fit['rotation']).to_4x4();T.translation=Vector(fit['translation'])
def mat(n,c,metal=0,rough=.4):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
silver=mat('M01_lavender_silver_inferred_lighting',(.49,.44,.72),.65);dark=mat('M02_dark_lavender_band',(.06,.025,.17),.25);lens=mat('M03_optical_dark_not_through_hole',(.008,.006,.025),.1,.18)
white=mat('WHITE_shared_geometry',(.7,.7,.7))
def box(n,loc,scale,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);return o
def cyl(n,loc,r,depth,m,rot=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=n;o.data.materials.append(m)
 if rot:o.rotation_euler=rot
 return o
objs=[]
objs.append(box('P01_front_shell_thickness_INFERRED',(0,0,-.025),(1,1.2,.05),silver))
objs.append(box('P02_upper_finish_not_hinge',(0,.235,.001),(.96,.69,.004),silver))
objs.append(box('P03_lower_finish_boundary_not_hinge',(0,-.365,.001),(.96,.49,.004),dark))
# rear panel hinge at y=.6; depth and fold angle wholly inferred
b=box('P04_rear_leaf_unseen_geometry_INFERRED',(0,.6-.6*math.cos(math.radians(25)),-.025-.6*math.sin(math.radians(25))),(1,1.2,.05),silver);b.rotation_euler.x=math.radians(25);objs.append(b)
objs.append(cyl('P05_top_hinge_axis_INFERRED',(0,.6,-.025),.035,1.02,silver,(0,math.pi/2,0)))
for i,y in enumerate([-.30,-.51],1):
 objs.append(cyl(f'P06_lens{i}_rim',(.33,y,.011),.087,.022,silver))
 objs.append(cyl(f'P07_lens{i}_glass',(.33,y,.023),.070,.006,lens))
objs.append(cyl('P08_small_spot_identity_uncertain',(.33,-.095,.006),.022,.008,dark))
for o in objs:o.matrix_world=T@o.matrix_world;o['evidence']='See docs/evidence.zh.md; conditional object proxy, not scene reconstruction'
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='SOURCE7_CONDITIONAL_NOT_CALIBRATED';cam.data.type='PERSP';cam.data.sensor_fit='HORIZONTAL';cam.data.sensor_width=36;cam.data.lens=1000*36/1080;s.camera=cam
for loc,power,size in [((1,2,0),300,5),((-3,-1,0),150,4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector(fit['translation'])-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/phone-material.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'models/phone-material.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
# Shared geometry white material variant only
orig={o.name:list(o.data.materials) for o in objs}
for o in objs:o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/phone-white.blend'))
bpy.ops.export_scene.gltf(filepath=str(R/'models/phone-white.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
for o in objs:
 o.data.materials.clear()
 for m in orig[o.name]:o.data.materials.append(m)
s.render.filepath=str(R/'renders/source7-conditional.png');bpy.ops.render.render(write_still=True)
# No fitting or transforming the object across diagnostic angles.
center=Vector(fit['translation'])
for name,v in [('front',Vector((0,0,3))),('rear',Vector((0,0,-3))),('side',Vector((3,0,0))),('top',Vector((0,3,.3)))]:
 cam.location=center+v;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=48;s.render.filepath=str(R/f'renders/diagnostic-{name}.png');bpy.ops.render.render(write_still=True)
# Topology on original authored meshes, no invented manifold success.
qa=[]
import bmesh
for o in objs:
 bm=bmesh.new();bm.from_mesh(o.data);qa.append({'object':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume':bm.calc_volume(signed=True)});bm.free()
json.dump(qa,open(R/'qa/topology.json','w'),indent=2)
json.dump({o.name:[list(T.inverted()@o.matrix_world@Vector(c)) for c in o.bound_box] for o in objs},open(R/'qa/local-bounds.json','w'),indent=2)
