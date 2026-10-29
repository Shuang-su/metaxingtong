from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
# Manual native-pixel readings of visible soft lip/face/aperture boundaries, not calibrated world dimensions.
D={'1801.323':{'outer_recess':[892,921,1249,983],'inner_face':[900,928,1241,976],'left_aperture':[707,927,840,977],'right_aperture':[1303,925,1454,976],'left_lip':[691,923,846,983],'right_lip':[1297,920,1466,983],'board_top_at_feature_center':{'left':866,'center':842,'right':864}},'1804.861':{'outer_recess':[861,933,1215,993],'inner_face':[869,940,1207,986],'left_aperture':[680,938,809,987],'right_aperture':[1268,937,1418,986],'left_lip':[662,934,816,994],'right_lip':[1261,932,1430,993],'board_top_at_feature_center':{'left':880,'center':852,'right':875}}}
for frame,d in D.items():
 p=P.parent/f'c26/new_evidence/frame_{frame}.png';im=Image.open(p).convert('RGB');draw=ImageDraw.Draw(im)
 d['source']=str(p.relative_to(P.parent));d['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();d['boundary_uncertainty_px']=3;d['board_top_uncertainty_px']=3
 for key in ['outer_recess','inner_face','left_aperture','right_aperture','left_lip','right_lip']:
  b=d[key];color='cyan' if 'aperture' in key else ('yellow' if key=='inner_face' else 'red');draw.rectangle(b,outline=color,width=1);draw.text((b[0],b[1]-12),key,fill=color)
 def h(k):b=d[k];return b[3]-b[1]
 def cy(k):b=d[k];return (b[3]+b[1])/2
 mean_h=(h('left_aperture')+h('right_aperture'))/2;mean_lip=(h('left_lip')+h('right_lip'))/2
 center=(cy('left_aperture')+cy('right_aperture'))/2
 d['metrics']={'outer_recess_height_px':h('outer_recess'),'inner_face_height_px':h('inner_face'),'aperture_heights_px':[h('left_aperture'),h('right_aperture')],'outer_height_over_mean_aperture':h('outer_recess')/mean_h,'outer_height_over_mean_lip':h('outer_recess')/mean_lip,'outer_image_width_height':(d['outer_recess'][2]-d['outer_recess'][0])/h('outer_recess'),'inner_image_width_height':(d['inner_face'][2]-d['inner_face'][0])/h('inner_face'),'center_y_minus_interpolated_aperture_centers_px':cy('outer_recess')-center,'top_margin_px':[d['left_lip'][1]-d['board_top_at_feature_center']['left'],d['outer_recess'][1]-d['board_top_at_feature_center']['center'],d['right_lip'][1]-d['board_top_at_feature_center']['right']]}
 im.save(P/f'{frame}_annotated_native1x.png')
D['limitations']=['Manual soft-edge estimates ±3px per boundary; apparent pixel ratios are not a plane rectification.','Hole mouth and dark through-aperture differ due to lip depth and perspective; both are annotated.','New cameras uncalibrated: no absolute pixel to world scale.','Outer dark/bright recess lip is distinct from inner flat cream face; shadows blur exact boundary.','G shows only left hole and left portion of central recess; no complete central width or center measurement.']
json.dump(D,open(P/'native_endboard_ratios.json','w'),indent=2)
print(json.dumps({k:v['metrics'] for k,v in D.items() if isinstance(v,dict)},indent=2))
