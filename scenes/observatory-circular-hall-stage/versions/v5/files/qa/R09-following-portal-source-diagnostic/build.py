from PIL import Image,ImageDraw
import pathlib,json,hashlib
p=pathlib.Path(__file__).parent;s=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104/sources/report')
data={}
def line(i,sem,pts,e,notes):return {'id':i,'semantic':sem,'pixels_xy':pts,'subjective_error_px':e,'notes':notes}
data['15']=[
line('A1','high_dark_arch_outer_edge',[[635,435],[646,421],[660,410],[669,406]],4,'左半可见；中央发光星遮边，不以星尖代弧顶。'),
line('A2','high_dark_arch_outer_edge',[[684,407],[697,414],[710,427],[719,442]],4,'右半可见；顶部跨星区不补点。'),
line('A3','high_dark_arch_lower_edge_left',[[638,451],[646,437],[658,425],[667,420]],5,'浅色弧纹与暗带交界，局部低对比。'),
line('A4','high_dark_arch_lower_edge_right',[[688,421],[700,431],[710,444],[716,455]],5,'不把浅色内部金/银纹当深框边。'),
line('B1','low_thick_dark_frame_outer_edge',[[631,538],[632,496],[638,473],[651,456],[675,446],[697,455],[713,475],[720,498],[720,539]],3,'较低连续厚暗框外边；下方终点是遮挡截止，不是门脚。'),
line('B2','low_thick_dark_frame_inner_edge',[[643,535],[643,498],[648,479],[660,465],[675,458],[691,465],[702,478],[709,497],[709,535]],4,'通视开口内边，与远处透视纹饰严格分开。'),
line('U1','pale_nested_arch_depth_assignment',None,None,'高暗带与低厚框之间可见多层浅色弧；无法仅此源确认全属同平面门面，可能含沿视线另层/对侧结构。'),
line('U2','high_arch_apex',None,None,'发光星饰遮住中央弧顶，禁止用星尺寸测量建筑。'),
line('U3','door_frame_feet_and_thickness',None,None,'门脚被独立近前拱遮；实体深度和墙厚未知。')]
data['13']=[
line('A1','oblique_dark_portal_outer_arch',[[274,90],[286,77],[301,66],[319,62],[337,66],[354,76],[369,94],[381,120],[386,150]],6,'斜视暗框外缘；左边与厚墙叠影融合。'),
line('A2','oblique_dark_portal_inner_arch',[[280,112],[291,101],[305,87],[321,83],[337,89],[352,101],[364,119],[370,140],[372,168]],6,'内孔上弧；色光压低对比，手工误差较大。'),
line('A3','oblique_portal_right_inner_jamb',[[372,168],[376,190],[379,207]],7,'右门侧可见短段被外栏杆穿过；不把栏杆当门框。'),
line('U1','left_jamb_feet_and_higher_arch_layer',None,None,'左门侧/门脚在阴影和栏杆中不稳；15的高位层在13未能辨同一实例。')]
data['14']=[
line('A1','frontal_lower_portal_outer_arch',[[473,241],[482,199],[500,161],[529,128],[560,104],[593,95],[627,103],[657,125],[683,158],[706,202],[716,240]],4,'大开口内所见较低前置拱，是否同于15低厚框需相机与前后层另证，不能先验同点。'),
line('A2','frontal_lower_portal_inner_arch',[[498,237],[512,197],[533,162],[562,136],[592,125],[625,134],[653,159],[675,197],[691,236]],5,'外层拱的下边与下一层暗拱之间露出天空窄带，必须保留层次，不并成单金框。'),
line('U1','tall_outer_opening_apex',None,None,'最高大开口顶部出画，不能从低拱顶替代。'),
line('U2','lower_portal_vertical_sides_and_feet',None,None,'人物、翼饰、强光束遮挡，不硬描。')]
data['21']=[line('U1','portal_identity',None,None,'左右宽暗开口裁切/字幕/角度使其无法可靠对应15主门；本图不提供可用门框对应点。')]
res={'method':'Source-only manual edge tracing; no model, render, camera fit, or production modification. Original coordinates x-right/y-down. Crop magnifications are inspection only, not new source resolution.','scope':'Visible dark high/low portal layers and whether opposite-view images can compare. Image traces do not assert 3D correspondences.','images':[],'supported_candidate':'A bounded portal-layer hypothesis: source15 visibly contains a high dark curved band and a separate lower thick dark entrance silhouette; preserve their separate image contours and occlusion.','not_supported':['Absolute wall/door thickness, full door feet, hidden arch completion, material physical color under lighting.','Claim that all pale nested curves are exterior decoration on the same plane.','Automatic source13/source14-to-source15 same-feature correspondence.','Any metric inferred from glowing star, character, mirror reflection, or enlarged inspection crop.'],'comparison':'13 supports an oblique thick arch opening, but does not reveal enough high-layer detail to call it the verified reverse of the same facade. 14 reveals multiple nested depth layers plus a tall opening clipped above, not necessarily the same low frame instance as15.21 unusable for this portal correspondence.'}
for n,rows in data.items():
 f=s/(n+'.png');im=Image.open(f).convert('RGB');d=ImageDraw.Draw(im)
 res['images'].append({'id':n,'source':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'dimensions':list(im.size),'native_decoded':False,'video_time':None,'features':rows})
 for j,r in enumerate(rows):
  pts=r['pixels_xy']
  if not pts:continue
  c=['#00ffff','#ffdd00','#ff66aa','#88ff44'][j%4];d.line([tuple(z) for z in pts],fill=c,width=2)
  for x,y in pts:d.ellipse((x-2,y-2,x+2,y+2),fill=c)
  x,y=pts[0];d.text((x+3,y+3),r['id'],fill=c,stroke_width=1,stroke_fill='black')
 im.save(p/(n+'-annotated.png'))
(p/'annotations.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
(p/'README.zh.md').write_text('源图15支持分离的高位暗弧带与较低厚深框假说，不能把两者和内侧浅纹统统压成一个同面金框。高位弧中央被发光星遮挡，顶点保持null；下框门脚被前景拱挡住，保持null。\n\n13斜视确有厚暗框拱口，不能证明就是15外立面反面或同一层框。14大开口顶部出画，里面另有多层拱/天空窄带与人物光束；这种深度叠合反而要求谨慎，不宜只凭正面图合并层次。21不提供可靠门框对应。\n\n手工边界误差3–7原图像素，主观而非统计标定。原图1192×671报道截图、非原生视频，片内时刻未知。3倍局部仅诊断视图。未看模型后改点，未做相机拟合。\n')
a=[]
for f in p.iterdir():
 if f.is_file() and f.name!='manifest.json':a.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(p/'manifest.json').write_text(json.dumps(a,indent=2))
