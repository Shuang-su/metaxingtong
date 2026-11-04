import bpy,pathlib,json,hashlib
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parents[1];audit={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R09_{mode}.blend'));oldnames=set(bpy.data.objects.keys());clay=bpy.data.objects['COSMETIC_case_body'].data.materials[0] if mode=='white' else None;dark=bpy.data.materials.get('DARK_metal')
 trim=bpy.data.materials.new('DEVICE_pale_edge_proxy');trim.use_nodes=True;pr=trim.node_tree.nodes.get('Principled BSDF');pr.inputs['Base Color'].default_value=(.22,.20,.17,1);pr.inputs['Metallic'].default_value=.35;pr.inputs['Roughness'].default_value=.5
 def finish(o,n,m,e):
  o.name=n;o.data.materials.append(clay if mode=='white' else m);o['source_evidence']=e;o['limit']='Visible front-panel category only. Dimensions, depth, material and position conditional; no measured device identity, brand, frequency or unseen controls.';return o
 def box(n,p,dim,m,e):
  bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,m,e)
 for side,x in [('left',-.72),('right',-.18)]:box('DEVICE_front_bezel_'+side,(x,-.059,1.0),(.012,.012,.30),trim,'009 visible bright outer front border; hidden lower extent inferred')
 for side,z in [('top',1.15),('bottom',.85)]:box('DEVICE_front_bezel_'+side,(-.45,-.059,z),(.54,.012,.012),trim,'009 visible front border; bottom partly occluded, finite continuation inferred')
 box('DEVICE_left_grille_region',(-.585,-.058,.99),(.235,.010,.23),dark,'009 D04 left large dark grille/panel; no fabricated detailed mesh weave')
 box('DEVICE_horizontal_tuning_region',(-.35,-.059,1.10),(.17,.012,.07),trim,'009 D05 horizontal display/scale-like strip; unreadable markings intentionally absent')
 box('DEVICE_front_divider',(-.45,-.059,.99),(.008,.012,.29),trim,'009 front panel division; local dimensions inferred')
 for j,z in enumerate([1.075,.94]):
  a=Vector((-.215,-.053,z));b=Vector((-.215,-.082,z));d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.021,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();finish(o,f'DEVICE_visible_knob_{j}',trim,'009 two identifiable right-side round knobs; third dark blot not modeled')
 for j,x in enumerate([-.53,-.495,-.46]):box(f'DEVICE_top_button_{j}',(x,-.01,1.182),(.014,.025,.010),trim,'009 three visible pale top controls; back/under surfaces inferred')
 body=bpy.data.objects['COSMETIC_case_body'];body['semantic_correction']='Legacy name retained for history. Source009 front grille, tuning-like strip and two knobs suggest handled radio/audio device, not established cosmetic case. Exact function/type remains conditional.'
 d=bpy.data.cameras.new('DIAG_device_front');d.lens=55;d.clip_start=.001;o=bpy.data.objects.new('DIAG_device_front',d);bpy.context.collection.objects.link(o);o.location=(-.85,-1.12,1.32);o.rotation_euler=(Vector((-.45,-.025,1.04))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R10_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R10_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True);audit[mode]={'added_objects':sorted(set(bpy.data.objects.keys())-oldnames),'old_mesh_geometry_unchanged_intent':True,'scope':'12 visible device front/control category proxies; source009 only, not calibrated; old tabletop collisions/gaps retained; rejected case/clock bottom extension not applied','model_sha256':hashlib.sha256((P/'models'/f'R10_{mode}.blend').read_bytes()).hexdigest()}
(P/'qa/R10-device-applied.json').write_text(json.dumps(audit,indent=2))
