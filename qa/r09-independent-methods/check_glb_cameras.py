import bpy,json,struct,math,hashlib
from pathlib import Path
P=Path('/workspace/scratch/fa58bfcf0425/cityroom-refinement-20261103/models');O=Path(__file__).parent;result=[]
for mode in ['material','white']:
 bp=P/f'R09b_{mode}.blend';gp=P/f'R09b_{mode}.glb';bpy.ops.wm.open_mainfile(filepath=str(bp));s=bpy.context.scene;aspect=(s.render.resolution_x*s.render.pixel_aspect_x)/(s.render.resolution_y*s.render.pixel_aspect_y);orig={o.name:{'matrix':[list(v) for v in o.matrix_world],'yfov_expected':2*math.atan(o.data.sensor_width/(2*o.data.lens*aspect)),'lens':o.data.lens,'sensor_fit':o.data.sensor_fit,'shift':[o.data.shift_x,o.data.shift_y]} for o in s.objects if o.type=='CAMERA'}
 raw=gp.read_bytes();length,typ=struct.unpack_from('<II',raw,12);g=json.loads(raw[20:20+length]);spec={n['name']:g['cameras'][n['camera']] for n in g['nodes'] if 'camera' in n};bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(gp));imp={o.name:o for o in bpy.context.scene.objects if o.type=='CAMERA'};rows=[]
 for n,a in orig.items():
  if n not in imp or n not in spec:rows.append({'name':n,'missing':True});continue
  b=imp[n];rows.append({'name':n,'max_matrix_element_difference':max(abs(a['matrix'][i][j]-b.matrix_world[i][j]) for i in range(4) for j in range(4)),'source_sensor_fit':a['sensor_fit'],'source_shift':a['shift'],'expected_yfov':a['yfov_expected'],'exported_yfov':spec[n]['perspective']['yfov'],'yfov_difference_rad':abs(a['yfov_expected']-spec[n]['perspective']['yfov'])})
 result.append({'mode':mode,'blend_sha256':hashlib.sha256(bp.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(raw).hexdigest(),'source_aspect':aspect,'source_camera_count':len(orig),'imported_camera_count':len(imp),'missing':sorted(set(orig)-set(imp)),'extra':sorted(set(imp)-set(orig)),'cameras':rows})
(O/'R09b-glb-camera-independent.json').write_text(json.dumps(result,indent=2));print([(r['mode'],r['imported_camera_count'],max(x.get('max_matrix_element_difference',float('inf')) for x in r['cameras']),max(x.get('yfov_difference_rad',float('inf')) for x in r['cameras'])) for r in result])
