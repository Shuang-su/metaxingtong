"""Actual empty-scene GLB reimport plus explicit sidecar restoration.
Never modifies mesh or material to hide interchange differences.
"""
import bpy,json,pathlib,sys
from mathutils import Matrix
P=pathlib.Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
tag=args[0] if args else 'material'
j=json.loads((P/'dependencies/R04C-environment-sidecar.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
assert not list(bpy.data.objects),'Scene must be empty before import'
bpy.ops.import_scene.gltf(filepath=str(P/f'models/R04C_{tag}.glb'))
s=bpy.context.scene;before={'objects':len(s.objects),'meshes':len([o for o in s.objects if o.type=='MESH']),'cameras':len([o for o in s.objects if o.type=='CAMERA']),'area_lights':len([o for o in s.objects if o.type=='LIGHT' and o.data.type=='AREA']),'active_camera':s.camera.name if s.camera else None}
r=j['render'];s.render.engine=r['engine'];s.cycles.samples=r['samples'];s.cycles.use_denoising=r['use_denoising'];s.render.threads_mode='FIXED';s.render.threads=4
for k in ['resolution_x','resolution_y','resolution_percentage','pixel_aspect_x','pixel_aspect_y','film_transparent']:setattr(s.render,k,r[k])
for k in ['view_transform','look','exposure','gamma']:setattr(s.view_settings,k,r[k])
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
w=bpy.data.worlds.new('R04C_explicit_sidecar_world');w.use_nodes=True;s.world=w
b=w.node_tree.nodes['Background'];b.inputs[0].default_value=j['world']['color'];b.inputs[1].default_value=j['world']['strength']
camera_report=[]
for c in j['cameras']:
 o=bpy.data.objects.get(c['name']);assert o and o.type=='CAMERA','Actual GLB camera missing'
 delta=max(abs(o.matrix_world[i][k]-c['matrix_world'][i][k]) for i in range(4) for k in range(4))
 camera_report.append({'name':c['name'],'native_glb_matrix_error_before_sidecar':delta})
 o.matrix_world=Matrix(c['matrix_world'])
 for k in ['type','lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','clip_start','clip_end']:setattr(o.data,k,c[k])
for l in j['area_lights']:
 if bpy.data.objects.get(l['name']) and bpy.data.objects[l['name']].type=='EMPTY':bpy.data.objects.remove(bpy.data.objects[l['name']],do_unlink=True)
 d=bpy.data.lights.new(l['name'],'AREA');o=bpy.data.objects.new(l['name'],d);s.collection.objects.link(o);o.matrix_world=Matrix(l['matrix_world'])
 for k in ['energy','shape','size','color']:setattr(d,k,l[k])
s.camera=bpy.data.objects[j['active_camera']]
out=P/'qa/R04C-empty-scene-restore';out.mkdir(exist_ok=True)
report={'tag':tag,'empty_scene_before_import':True,'before_sidecar':before,'cameras':camera_report,'restored':{'active_camera':s.camera.name,'world_color':list(b.inputs[0].default_value),'world_strength':b.inputs[1].default_value,'world_surface_connected':bool(w.node_tree.nodes['World Output'].inputs['Surface'].links),'area_lights':[{'name':o.name,'energy':o.data.energy,'size':o.data.size,'color':list(o.data.color)} for o in s.objects if o.type=='LIGHT'],'resolution':[s.render.resolution_x,s.render.resolution_y],'pixel_aspect':[s.render.pixel_aspect_x,s.render.pixel_aspect_y],'display':[s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,s.view_settings.gamma]},'notes':'World/AREA/frame/display restored explicitly. Native GLB environment not equivalent. Geometry and materials not changed.'}
(out/f'{tag}-restore-report.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out/f'R04C_{tag}_restored.blend'))
if 'render' in args:
 s.render.filepath=str(out/f'{tag}-SOURCE02-restored.png');bpy.ops.render.render(write_still=True)
print('ACTUAL_EMPTY_SCENE_RESTORE_COMPLETE',tag)
