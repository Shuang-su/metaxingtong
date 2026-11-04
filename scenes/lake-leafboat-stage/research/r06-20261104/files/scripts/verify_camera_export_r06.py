import bpy,pathlib,json
R=pathlib.Path(__file__).resolve().parents[1]
def cams(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));dg=bpy.context.evaluated_depsgraph_get();return {o.name:{'world':[list(row) for row in o.matrix_world],'projection':[list(row) for row in o.calc_matrix_camera(dg,x=3840,y=2160,scale_x=1,scale_y=1)],'lens':o.data.lens,'sensor_fit':o.data.sensor_fit} for o in bpy.context.scene.objects if o.type=='CAMERA'}
a=cams(R/'models/lakeleaf-r06-material.blend');b=cams(R/'models/lakeleaf-r06-glb-reimport-check.blend');rows=[]
for n in a:
 rows.append({'camera':n,'present':n in b,'world_matrix_max_abs_error':max(abs(a[n]['world'][i][j]-b[n]['world'][i][j]) for i in range(4) for j in range(4)) if n in b else None,'projection_matrix_max_abs_error':max(abs(a[n]['projection'][i][j]-b[n]['projection'][i][j]) for i in range(4) for j in range(4)) if n in b else None,'original':a[n],'reimport':b.get(n)})
report={'resolution':[3840,2160],'rows':rows,'all_present':a.keys()==b.keys(),'all_world_matrix_errors_le_1e4':all(r['present'] and r['world_matrix_max_abs_error']<=1e-4 for r in rows),'all_projection_errors_le_1e4':all(r['present'] and r['projection_matrix_max_abs_error']<=1e-4 for r in rows),'source_camera_calibration':False}
(R/'qa/r06/glb-camera-validation.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k!='rows'})
