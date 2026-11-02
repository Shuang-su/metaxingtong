from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'stages/r06-review-candidate'
geo=json.loads((R/'stages/r04-review-candidate/geometry-identity.json').read_text())['objects'];qa={x['id']:x for x in json.loads((O/'qa/all-object-topology.json').read_text())};sources={x['id']:x for x in json.loads((O/'source-cameras.json').read_text())}
all_src=list(sources);preview=['preview-front','preview-high','preview-wide','preview-low'];live=['aug24-front','companion-120','companion-126']
groups={
 'curved_support':('两前曲带',all_src,'左右两前支承及网格正面/黑色厚侧面有直接来源；底脚接台轮廓可见','具体截面/深度/隐藏根部、真实嵌入或接缝仍推断；未添加未经证实的第三/第四腿'),
 'crown':('上冠环和下碟',preview,'顶筒、大薄环、中环、下碟及中央细条可辨','精确断面/完整后缘、环是否局部开口、中央孔/全部隐藏支撑未证；各环封闭与细杆做法为候选'),
 'inferred_structure':('显式推断连接',preview,'相关连接区邻接可见，但实际固定方式不可见','全部连接截面/端点/数量为推断；模型连通不证明原场结构'),
 'platform':('主盘/外裙/台阶',all_src,'镜面台面、边光带、侧外翼与多层边缘可见','底厚、前台阶与侧翼完整轮廓受字幕/观众遮挡；中央盘与外裙划分仍有残差'),
 'chevron_frame':('两侧空心折箭框',all_src,'每侧三框与真实孔洞可辨；右侧厚边在实演4K可见','间距、倾角、背面和底座为条件拟合；圆形插饰/气泡不可混当同一实例'),
 'chevron_light':('折箭内光管',preview+['companion-120','companion-126'],'空心框内发光折线可辨','管径、端头固定和真实光源功率推断；非唯一PBR匹配'),
 'circle_insert':('箭框周围圈件',preview+['companion-120','companion-126'],'可见圈/球样装饰','当前三/侧实例映射与支撑未知；可能包含效果物，不宣物理悬挂已证'),
 'stage_lights':('地面/环下灯',preview+['companion-126'],'边灯与吊灯存在、实际节目可见moving-head形态','40+40数量与位置推断；当前灯头/底座为简化体，真实转轴/支架未完成'),
 'circle_pads':('左右圆形台灯盘',preview,'两侧圆盘状亮件可见','厚度、接触、半径及具体位置为模型单位推断'),
 'palms':('棕榈及叶/果',all_src,'多个棕榈簇可见，弯曲树干和宽叶轮廓有来源','六树是候选实例分配，叶9/株及果数推断；未逐叶追踪同一真实实例'),
 'lighthouse':('灯塔',preview,'远处塔身分段、灯室/顶轮廓可辨','位置/尺度/条带配色、栏杆数和未见内部未校准；不当测量地标'),
 'boats':('游艇/帆船',preview+['aug24-front'],'游艇和帆船的相对背景类别可辨','具体舱体/窗/船体深度与港位为简化候选，未恢复不可见内部'),
 'umbrella':('遮阳伞',preview,'左右紫/粉伞可见','伞叶分区纹理、尺寸和杆接头推断；r03b只修模型内杆顶间隙'),
 'surfboard':('冲浪板',preview,'彩色竖板样道具可见','三实例对应不确定、背部斜撑未见；落地修正不是抗倾倒/源支撑验收'),
 'neon_prop':('霓虹拱/点唱机样道具',preview+['companion-126'],'右后景拱线/机柜样轮廓在实演4K可辨','当前两件仅粗轮廓，面板/按钮/文字/内部缺失；拓扑修复不代表形状通过'),
 'environment':('海滩/海面/远丘',all_src,'开放海港、水面、岸与植被丘有来源','地形边界、距离、尺度、植被分布是有限工作域；不声称精确地理/完整外景'),
 'other':('其它',all_src,'见个体说明','未独立核实的项目保持推断/待查')
}
def group(n):
 if n in ('FRAME_L','FRAME_R') or n.startswith(('FRAME_L_EDGE','FRAME_R_EDGE')):return 'curved_support'
 if n.startswith('INFERRED_'):return 'inferred_structure'
 if n.startswith('CROWN_'):return 'crown'
 if n.startswith(('PLATFORM','STAIR','OUTER_WING','INNER_DISC','BACK_')):return 'platform'
 if n.startswith('CHEVRON_LIGHT'):return 'chevron_light'
 if n.startswith('CHEVRON_RING'):return 'circle_insert'
 if n.startswith('CHEVRON_'):return 'chevron_frame'
 if n.startswith(('STAGE_SPOT','OVERHEAD_SPOT')):return 'stage_lights'
 if n.startswith('CIRCLE_PAD'):return 'circle_pads'
 if n.startswith('PALM_'):return 'palms'
 if n.startswith('LIGHTHOUSE_'):return 'lighthouse'
 if n.startswith(('YACHT_','SAILBOAT_')):return 'boats'
 if n.startswith('UMBRELLA_'):return 'umbrella'
 if n.startswith('SURFBOARD_'):return 'surfboard'
 if n.startswith('NEON_PROP_'):return 'neon_prop'
 if n.startswith('ENV_'):return 'environment'
 return 'other'
rows=[]
for n in sorted(geo):
 g=group(n);label,ids,seen,unknown=groups[g]
 rows.append({'id':n,'group':g,'label':label,'world_bbox_model_units':geo[n]['bbox'],'model_geometry_sha256':geo[n]['full_sha'],'source_frames':[{'id':i,'path':sources[i]['file'],'sha256':sources[i]['source_sha256']} for i in ids],'source_observation':seen,'inferred_or_unseen':unknown,'attribute_status':{'identity':'candidate mapping; stable model ID, source instance not universally verified','silhouette':'coarse visible family, quantitative residual not passed','thickness_depth':'model-unit hypothesis unless explicitly visible side; no measured values','contact_support':'model construction check only; hidden source joints unknown','openings':'real mesh openings where modeled, source completeness not universally passed','material_lighting':'canonical teal approximation; exact PBR and other temporal light states not matched'},'native_topology':qa[n],'source_acceptance':'NOT PASSED','independent_holdout':False,'later_replay_verified':False})
(O/'object-evidence-394.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
lines=['# 逐物件证据与未完成项','', '394 个稳定模型 ID 的逐条来源、工作坐标、几何摘要和属性状态见 `object-evidence-394.json`。所有距离仅为模型单位。模型 ID 稳定不代表源重复实例已经逐个对应。','', '|分组|模型件数|来源可见|推断/缺项|','|---|---:|---|---|']
for g,(label,ids,seen,unknown) in groups.items():
 count=sum(r['group']==g for r in rows)
 if count:lines.append(f'|{label}|{count}|{seen}|{unknown}|')
lines += ['','## 尚未完成的来源形态','- 左侧蓝色大型吉祥物/充气物、右侧火烈鸟与TV图形充气物、空中气球，仅在预告明确可见；尚未建，不能假装已在Aug24所有时刻确认。','- 沙滩木板/标牌、部分桌椅/围篱/音响/烛光、侧外台阶与边缘小构件未完整恢复。','- 真实moving-head灯具支架/转轴、伞瓣双色纹理、精确LED像素/中文文字、环境精细地形与水面光学未完成。','- 观众、演唱者、广播标识/字幕、激光/粒子光束是动态或屏幕层，不被建成固定结构；在分析mask中排除，但原图保留。','','## 验收边界','技术拓扑、真实GLB回导、工作构造接触和源还原是不同门槛。全部7帧已用于构建/诊断，不存在holdout；8个内部检查角不增加来源视角数。后续独立回放未证。任何未知项目不因文件可打开或本表齐全而通过。']
(O/'object-evidence.md').write_text('\n'.join(lines)+'\n')
