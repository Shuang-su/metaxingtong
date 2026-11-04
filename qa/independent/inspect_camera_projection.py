import bpy,json,sys,hashlib
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];src=Path(args[0]);out=Path(args[1]);mode=args[2]
if mode=='glb':
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(src))
dg=bpy.context.evaluated_depsgraph_get();rows=[]
for o in bpy.context.scene.objects:
 if o.type!='CAMERA':continue
 rows.append({'name':o.name,'sensor_fit':o.data.sensor_fit,'sensor_width':o.data.sensor_width,'sensor_height':o.data.sensor_height,'lens':o.data.lens,'matrix_320x176':[list(row)for row in o.calc_matrix_camera(dg,x=320,y=176,scale_x=1,scale_y=1)],'matrix_1920x1080':[list(row)for row in o.calc_matrix_camera(dg,x=1920,y=1080,scale_x=1,scale_y=1)]})
out.write_text(json.dumps({'file':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'cameras':rows},indent=2))
