import bpy,os,json
from bpy_extras.object_utils import world_to_camera_view
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));bpy.ops.wm.open_mainfile(filepath=r+'/models/material.blend');s=bpy.context.scene;sem=json.load(open(r+'/qa/wing-sign-source/semantic-regions-v1.json'));out={'scope':'Model projected vertex bounds versus manual source ROI only; ROI is not exact contour/point residual, no refit','cameras':[]}
for src in sem['sources'][:2]:
 c=bpy.data.objects['SOURCE'+src['name']+' conditional'];rows=[]
 for label,name,key in [('left','SIGN_L_closed_shallow_wing','left_wing_roi'),('right','SIGN_R_closed_shallow_wing','right_wing_roi'),('text','SIGN_QQ炫舞_font_proxy','lettering_roi')]:
  o=bpy.data.objects[name];p=[world_to_camera_view(s,c,o.matrix_world@v.co) for v in o.data.vertices];bb=[min(v.x*1192 for v in p),min((1-v.y)*671 for v in p),max(v.x*1192 for v in p),max((1-v.y)*671 for v in p)];rows.append({'object':name,'source_roi':src[key],'model_projected_bounds':bb,'bounds_minus_roi_not_alignment_metric':[bb[i]-src[key][i] for i in range(4)]})
 out['cameras'].append({'source':src['name'],'camera':c.name,'rows':rows,'source_null':src['null']})
json.dump(out,open(r+'/qa/sign-projection.json','w'),indent=2)
