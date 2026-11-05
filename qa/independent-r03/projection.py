import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
Q=Path(__file__).parent;P=Q/'frozen';F=P/'models/material.blend';bpy.ops.wm.open_mainfile(filepath=str(F));s=bpy.context.scene;c=bpy.data.objects['SOURCE04 conditional'];M=c.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=1192,y=671)@c.matrix_world.inverted();fit=json.loads((P/'qa/camera-fit04.json').read_text());rows=[]
for i,a in enumerate(fit['source_points']):
 p=Vector((*a['model_world'],1));v=M@p;xy=[(v.x/v.w+1)*596,(1-v.y/v.w)*335.5];res=[xy[j]-a['source_pixel'][j]for j in [0,1]];rows.append({'name':a['name'],'source_pixel':a['source_pixel'],'declared_world':a['model_world'],'actual_saved_camera_projection':xy,'positive_clip_w':v.w,'residual_xy':res,'euclidean_error':math.hypot(*res),'vs_fit_prediction_max':max(abs(xy[j]-fit['predicted'][i][j])for j in [0,1])})
params=fit['parameters'];r={'blend_sha':hashlib.sha256(F.read_bytes()).hexdigest(),'points':rows,'component_rmse':math.sqrt(sum(x*x for a in rows for x in a['residual_xy'])/12),'euclidean_point_rms':math.sqrt(sum(a['euclidean_error']**2 for a in rows)/6),'at_bounds':[fit['bounds']['parameters'][i]for i,x in enumerate(params)if min(abs(x-fit['bounds']['lower'][i]),abs(x-fit['bounds']['upper'][i]))<1e-8],'actual_disk_centers':{n:list(bpy.data.objects[n].matrix_world.translation)for n in ['W02 round diffuser 0','W02 round diffuser 1','W02 round diffuser 2']},'camera_differences':{}}
current={o.name:([list(x)for x in o.matrix_world],o.data.lens)for o in s.objects if o.type=='CAMERA'}
bpy.ops.wm.open_mainfile(filepath=str(Q.parent/'independent-seaside-r02-qa-20261105/frozen/models/material.blend'))
for o in bpy.context.scene.objects:
 if o.type=='CAMERA':r['camera_differences'][o.name]=current[o.name]!=([list(x)for x in o.matrix_world],o.data.lens)
old=json.loads((P/'qa/landmarks-r02-original.json').read_text());new=json.loads((P/'qa/landmarks.json').read_text());r['null_changes']={}
for n,lst in new['cameras'].items():
 orig={x['name']:x for x in old['cameras'][n]};r['null_changes'][n]={x['name']:{'old':orig[x['name']]['source_pixel'],'new':x['source_pixel']}for x in lst if x['source_pixel']!=orig[x['name']]['source_pixel']}
(Q/'projection.json').write_text(json.dumps(r,indent=2));print(r['component_rmse'],r['euclidean_point_rms'])
