import bpy,math,json,pathlib
from mathutils import Matrix,Vector
P=pathlib.Path(__file__).resolve().parents[1];data=json.load(open(P/'qa/R06-bounded-fit.json'));audit={}
for mode in ('material','white'):
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R05_{mode}.blend'));s=bpy.context.scene
 o=bpy.data.objects['FLOOR_four_point_inlay'];r=Matrix.Rotation(-math.pi/4,4,'Z')
 for v in o.data.vertices:
  p=v.co.copy();p.x*=.8;p.y*=.8;v.co=r@p
 o['evidence_limit']='Outer radius2.4; conditional observed gold-ring/star radius1.934. Ring4.65 identity remains hypothesis. Axis relative doorway from report14.'
 for name,entry in data.items():
  eligible=[t for t in entry['all_focal_trials'] if t['inside_conservative_box']];c=min(eligible,key=lambda t:t['mean']);cam=bpy.data.objects[name];cam.matrix_world=Matrix(c['matrix_world']);cam.data.lens=c['lens'];cam['calibration']='FAILED constrained trial; max residual '+str(c['max']);audit[name]={'chosen':c,'reason':'minimum mean among retained fixed-focal trials satisfying finite hall camera bound; exceeds manual4px assumption, not accepted','visibility':[]}
  bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
  for pt in entry['world']:
   origin=cam.location;target=Vector(pt);direction=target-origin;hit,loc,norm,idx,obj,mat=s.ray_cast(deps,origin,direction.normalized(),distance=direction.length+.002);audit[name]['visibility'].append({'point':pt,'hit':obj.name if hit else None,'distance':float((loc-origin).length) if hit else None,'target_distance':float(direction.length)})
 cam=bpy.data.objects['SOURCE_15_exterior'];cam.data.lens=18;cam.rotation_euler=(Vector((-3,0,4.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam['calibration']='Manual framing hypothesis from full exterior, not fitted or accepted'
 s.camera=bpy.data.objects['MAIN_exterior'];bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R06_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R06_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True)
(P/'qa/R06-applied-camera-visibility.json').write_text(json.dumps(audit,indent=2))
