import json,hashlib,pathlib
from PIL import Image,ImageDraw
out=pathlib.Path(__file__).parent;src=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104/sources/report')
d={}
def obj(id,kind,bbox,center=None,status='partial',error=5,note=''):
 return {'id':id,'kind':kind,'visible_bbox_xyxy':bbox,'whole_object_center_xy':center,'visible_fragment_center_xy':[(bbox[0]+bbox[2])/2,(bbox[1]+bbox[3])/2] if bbox else None,'visibility':status,'subjective_error_px':error,'notes':note}
d['13']=[
obj('W1','keyhole_long_window',[0,0,99,213],note='左及顶部裁切，亮色窗身+圆弧底明确；全窗中心未知。'),
obj('W2','keyhole_long_window',[602,0,679,175],note='顶部裁切，暗窗身及下圆弧明确。'),
obj('W3','keyhole_long_window',[761,0,835,183],note='顶部裁切，底部亮反射不另算窗。'),
obj('W4','keyhole_long_window',[934,0,1035,194],note='顶部裁切，窗内装饰圆和下端同属一窗。'),
obj('D1','main_door_visible_opening',[275,67,388,237],None,'partial',7,'可见拱洞，外侧高框与内侧通行孔有层次，中心因下部栏杆/台阶不确定；不计窗。'),
obj('C1','ribbed_wall_support',[104,0,208,282],None,'cropped',7,'一组竖肋墙柱，不把每根槽线计柱。'),
obj('C2','ribbed_wall_support',[473,0,574,245],None,'cropped',7,'门右较宽暗色竖肋组，低对比。'),
obj('C3','ribbed_wall_support',[692,0,738,257],None,'cropped',5,'W2/W3间。'),
obj('C4','ribbed_wall_support',[844,0,909,274],None,'cropped',6,'W3/W4间。'),
obj('C5','ribbed_wall_support',[1031,0,1127,301],None,'cropped',7,'W4右侧组，边界斜。'),
obj('U1','unclassified_edge_fragment',[1142,0,1191,310],None,'ambiguous',12,'最右极窄暗亮片段，不足确认另一个完整窗或柱，不计下界。')]
d['14']=[
obj('W1','keyhole_long_window',[0,0,96,349],None,'cropped',4,'左与顶出画，窗底弧可见。'),
obj('W2','keyhole_long_window',[1090,0,1191,348],None,'cropped',4,'右与顶出画，完整窗中心未知。'),
obj('D1','main_door_outer_high_arch',[432,0,759,430],None,'cropped_and_occluded',5,'高外拱顶出画、人物及光束遮；与下面内拱不是两个门。'),
obj('D2','main_door_inner_portal',[470,95,718,425],None,'occluded',5,'内侧深色拱顶约593,95；门底由人物/舞台遮挡。与D1属于同一门组。'),
obj('C1','ribbed_wall_support',[173,0,240,470],None,'cropped',4,'左明确竖肋组。'),
obj('C2','ribbed_wall_support',[943,0,1014,483],None,'cropped',4,'右明确竖肋组。'),
obj('U1','door_side_decorative_panel',[240,0,431,443],None,'occluded',6,'门左圆纹线板，不是窗。'),
obj('U2','door_side_decorative_panel',[760,0,944,446],None,'occluded',6,'门右圆纹线板，不是窗。')]
d['15']=[
obj('W1','keyhole_long_window',[516,421,527,519],None,'narrow_oblique_fragment',4,'左侧压缩细片，窗头亮圆弧与长竖身仍可分辨。其完整二维形状中心不可靠。'),
obj('W2','keyhole_long_window',[532,421,552,526],[542,474],'mostly_visible',3,'完整头与长窗底可见，中心为轮廓bbox中心，不是三维中心投影。'),
obj('W3','keyhole_long_window',[563,425,600,536],[581.5,480.5],'mostly_visible',3,'门左最近清晰长窗。'),
obj('W4','keyhole_long_window',[760,426,793,541],[776.5,483.5],'mostly_visible',3,'门右最近长窗；斜纹/反射不是附加窗。'),
obj('W5','keyhole_long_window',[805,422,831,536],[818,479],'mostly_visible',3,'第二右窗。'),
obj('W6','keyhole_long_window',[837,419,848,526],None,'narrow_oblique_fragment',4,'最右狭长片可辨窗头及竖身，受侧边墙/支撑遮挡。'),
obj('D1','main_door_high_decorative_arch',[632,404,719,545],None,'occluded',4,'高装饰拱+星饰；不另计窗；下缘被外洞口/前景拱遮。'),
obj('D2','main_door_opening_outer_frame',[630,446,720,541],None,'occluded',3,'真正通行洞口深框，门脚不可见。与D1为同一门组。'),
obj('C1','door_left_wall_pilaster',[605,404,634,548],None,'occluded',4,'中央门左饰星柱面，底被前拱/台基叠挡。'),
obj('C2','door_right_wall_pilaster',[716,404,748,550],None,'occluded',4,'中央门右饰星柱面。'),
obj('C3','outer_left_wall_edge_support',[497,408,512,524],None,'partial',5,'极侧深色墙边，是否独立柱不确；不算明确柱下界。'),
obj('C4','outer_right_wall_edge_support',[846,408,861,525],None,'partial',5,'极侧边界与外撑分开，是否独立柱未知。')]
d['21']=[
obj('W1','keyhole_long_window',[365,0,450,72],None,'cropped',6,'只见窗下端，头部在画外；亮窗底不视为镜像独立窗。'),
obj('W2','keyhole_long_window',[539,0,616,69],None,'cropped',6,'顶部裁切，暗窗身和圆弧底。'),
obj('W3','keyhole_long_window',[712,0,793,73],None,'cropped',6,'顶部裁切，白亮下端。'),
obj('C1','wall_support',[307,0,352,136],None,'cropped',7,'左窗左侧深粉柱组，上端画外。'),
obj('C2','wall_support',[468,0,505,143],None,'cropped',6,'W1/W2间。'),
obj('C3','wall_support',[644,0,684,152],None,'cropped',6,'W2/W3间。'),
obj('C4','wall_support',[806,0,850,162],None,'cropped',7,'W3右侧。'),
obj('U1','left_unclassified_opening',[0,0,213,155],None,'cropped_and_overlay',15,'左上疑开口/外景受字幕和裁切，不称主门或新增窗。'),
obj('U2','right_unclassified_opening',[945,0,1157,172],None,'cropped',12,'右上宽暗开口与外景，无法确认是主门还是其他开口；不计主门下界。')]
counts={'13':{'windows':4,'window_whole_or_mostly':0,'rib_support_groups':5,'door_groups':1},'14':{'windows':2,'window_whole_or_mostly':0,'rib_support_groups':2,'door_groups':1},'15':{'windows':6,'window_whole_or_mostly':4,'rib_support_groups':2,'door_groups':1},'21':{'windows':3,'window_whole_or_mostly':0,'rib_support_groups':4,'door_groups':0}}
res={'method':'Manual inspection of source pixels only, no model/render consulted. Original x,y coordinates. Bounding boxes enclose visible fragments, not inferred full objects. Subjective errors are not calibrated probabilities. Center for mostly visible windows is bbox midpoint, not 3D geometric center. No cross-image instance correspondence asserted.','limits':['All sources are public report screenshots 1192x671, not native decoded video; within-video time unknown.','Per-image counts are lower bounds, cannot be added across images or extrapolated around full circumference.','D1/D2 same door assembly, decorative arch is not extra window.','No metric scale from characters, no hidden symmetric completion, no mirror duplication.'],'images':[]}
for n,objs in d.items():
 f=src/(n+'.png');im=Image.open(f).convert('RGB');dr=ImageDraw.Draw(im)
 res['images'].append({'id':n,'source_path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'size':list(im.size),'video_time':None,'visible_count_lower_bounds':counts[n],'objects':objs})
 for a in objs:
  b=a['visible_bbox_xyxy'];color='#00ffff' if a['id'][0]=='W' else '#ffff00' if a['id'][0]=='C' else '#ff7080' if a['id'][0]=='D' else '#ff00ff'
  dr.rectangle(b,outline=color,width=2);dr.text((b[0]+3,max(2,b[1]+3)),a['id'],fill=color,stroke_width=1,stroke_fill='black')
  c=a['whole_object_center_xy']
  if c:dr.ellipse((c[0]-3,c[1]-3,c[0]+3,c[1]+3),fill=color)
 im.save(out/(n+'-annotated.png'))
(out/'annotations.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
(out/'README.zh.md').write_text('逐图可见窗下界：13=4、14=2、15=6（4完整/较完整+2侧窄片）、21=3。只统计原图明确可见实例，不代表全圈窗数，不能相加。\n\n13/14/21全窗顶部均部分或全部出画，whole_object_center_xy保留null，visible_fragment_center_xy仅可见框中心。15四个较完整窗中心也仅二维bbox中点，不是固定3D同点。\n\n中心门高装饰拱与通行孔是同一门组；14两侧带圆纹的宽线板不是窗。21两端宽暗区不强行认主门。每组柱的细槽不重复计数；15极侧墙边是否独立柱未知，不计明确柱下界。\n\n模型16bay是否失配，需要同一相机/遮挡条件比较可见实例及角间节奏。这组像素不能自行确定全周14/16/18等分区数。未查看模型后迁就标注。\n')
manifest=[]
for f in out.iterdir():
 if f.is_file() and f.name!='manifest.json':manifest.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(out/'manifest.json').write_text(json.dumps(manifest,indent=2));print(counts)
