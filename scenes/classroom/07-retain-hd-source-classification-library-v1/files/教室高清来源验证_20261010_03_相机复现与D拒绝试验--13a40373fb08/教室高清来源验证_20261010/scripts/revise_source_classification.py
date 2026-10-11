from pathlib import Path
import json,hashlib,shutil
p=Path('classroom_hd_alignment_20261010');snap=p/'revision_pending/v0_document_snapshot';snap.mkdir(parents=True,exist_ok=True)
for f in [p/'高清验证说明.md',p/'复现说明.txt',p/'阶段结果.json',p/'qa/saved_main_verification.json',p/'qa/source_family.json',p/'qa/D_root_cause_and_shift_sweep.json',p/'rejected_shift/qa/change_manifest.json',p/'qa/camera_reference_manifest.json']:
 dst=snap/f.relative_to(p);dst.parent.mkdir(exist_ok=True,parents=True)
 if not dst.exists():shutil.copy2(f,dst)
source=Path('classroom_motion_sources_20261010');dest=p/'source_context_revision';dest.mkdir(exist_ok=True);hashes=json.load(open(source/'来源文件SHA256.json'))
for name,sha in hashes.items():
 f=source/name;assert hashlib.sha256(f.read_bytes()).hexdigest()==sha;shutil.copy2(f,dest/name)
for name in ['manifest_DC_frozen.json','来源性质与切点复核.md','来源文件SHA256.json']:shutil.copy2(source/name,dest/name)
s=(snap/'高清验证说明.md').read_text();s=s.replace('# 教室高清验证版：几何未变，D仍未通过','# 教室高清来源验证修订：几何未变，D为待关联辅助参考')
s=s.replace('没有把完整几何宣称为来源还原通过，也没有为了桌面数量临时增桌。','没有把完整几何宣称为来源还原通过，也没有为了桌面数量临时增桌。\n\n## 本次来源性质更正（优先于旧版结论）\n\n后续实际连续播放确认：D出现在叙事剪辑的静态教室/信件背景中，不能当作已经验证的正片实时运镜基线。D是否复用正片同套模型、同一布局、另一状态或预渲染仍未知，不能断言它是另一套模型，也不能继续把D桌面数压成正片共享布局的硬验收条件。\n\n- D前面5438.056–5438.206秒仍是黑底字幕，5441.539–5441.708秒已切到空教室；没有声称逐帧锁定其切点。\n- 5443.14–5453.55秒D构图保持静止；5457.678–5457.833秒整幅失焦，5461.84秒开始叠出信件，5464.887秒保存了叠信画面。\n- E近正面到C广角也是切镜：连续0.5倍慢播中，4282.187–4282.338秒仍为近景，4282.348–4282.508秒已突变广角。没有可跨切点追踪桌ID的中间运动视角。两侧画面仍可分别作约束，不可据两张截图推导连续相机轨迹。\n- 这次只实查4276–4290秒与5432–5465秒附近，不代表全片或其他回放没有有效运镜。\n\n冻结取证见source_context_revision/来源性质与切点复核.md、manifest_DC_frozen.json及来源文件SHA256.json。新取证使用已登录云浏览器会话、1920×1080解码，但仍是1180×757视口截图；视频内容约[0,47,1180,664]，不能套用旧5张补帧的[0,27,1180,664]裁切。新会话状态不追溯证明旧5帧的登录状态。\n\n原12对至少14的数值事实、所有锚点误差与拒绝试验都保留；改变的是适用范围。A/B/C/E仍有桌椅、光色、细节与保留点残差，尚不能宣布整体来源还原通过。')
s=s.replace('阴影、外观和D共同布局仍有残差','阴影、外观和家具轮廓仍有残差；与D的布局关联未知')
s=s.replace('| D 斜向 | 5447.186218 | 旧SOURCE_D同机位重采；再次直接看到至少14个独立木桌面/围板单元 | 6点RMS 8.96px，最大18.78px | 当前20总桌仅12可见，差至少2；远桌带身份/位置未统一 |','| D 辅助静态背景 | 5447.186218 | 旧D画面族高清重采；至少14个独立木面/围板；现已确认处在叙事剪辑静态背景中 | 6点RMS 8.96px，最大18.78px；仅为辅助画面对照 | 固定模型投影总20桌、可见12；同正片模型/布局关系未知，不能作硬验收失败依据 |')
s=s.replace('| E 近正面运镜帧 | 4282.103530 | 相比C提前2.3741秒的近正面特写，并非C广角近重复；新增讲桌/书柜深度关系检查 |','| E 切镜前近正面 | 4282.103530 | 相比C提前2.3741秒的独立近正面画面；连续慢播已证实其后发生切镜，不是连贯拉远；保留讲桌/书柜深度关系检查 |')
s=s.replace('这些小偏差也包括旧拼图面板抽取/重采样边界，不能全归为相机改变。','这些小偏差也包括旧拼图面板抽取/重采样边界，不能全归为相机改变。D旧/新图相似仅证明重采的是相同画面族，不能证明D与正片C同一模型或布局。')
s=s.replace('## D数量冲突的根因','## D辅助画面的数量差异与适用边界')
s=s.replace('这证明“现有共享布局在D的可见域分布不匹配”，没有证明唯一正确的改法。来源之间没有连续可追踪桌ID，无法从数量差直接推出应该加两张或移动哪两张。','这证明固定模型在所拟合D相机下与该辅助静态图的数量分布不同；不再据此推断正片共享布局错误。D与正片模型/布局的关联未知，来源之间也没有连续可追踪桌ID。无法从数量差直接推出应该加两张、移动哪两张，或将正片几何判为硬失败。')
s=s.replace('它不满足真实共同布局修复的证据要求，因此被明确拒绝','它原本就不满足真实共同布局修复的证据要求；在D降为待关联辅助参考后，更没有据此修改正片布局的依据，因此该试验继续明确拒绝')
start=s.index('## 下一轮最有用的采集');end=s.index('## 主图去噪说明');s=s[:start]+'''## 下一轮最有用的采集

1. 在正片中寻找同一连续镜头内带出桌列侧边、桌脚接地点、杯子/笔袋和人物相对位置的真实移动视角，优先追踪已确认正片桌ID。
2. 不再把已证实切镜的4282.1→4284.5秒当连续拉远，也不再要求从D叙事静态背景接回C的不存在已证实轨迹。
3. 若希望进一步利用D，先补足它复用正片同模型/同布局的直接证据；否则保留为辅助外观/布局参考，不据它重排正片桌椅。
4. 其余时间段和其他BV尚需继续核查；换回放时分别记录场景、黑板、道具及布局状态，避免把不同状态硬合并。

本阶段结论：5张高清验证链已建立，主几何未变。D降级为待关联辅助参考，E/C跨帧连续运镜假设撤回。正片来源仍有残差，未作整体通过判断；不是最终还原完成声明。

'''+s[end:];(p/'高清验证说明.md').write_text(s)
f=p/'复现说明.txt';s=(snap/'复现说明.txt').read_text().replace('阶段结论：几何未变，D仍未通过。','阶段结论：几何未变，D为待关联辅助静态参考；正片来源仍有残差，未作整体通过判断。');s+='\n来源性质修订：D处于叙事剪辑静态背景，同正片模型/布局关系未知；D相机只用于辅助对照，不是硬验收机位。E→C已实播确认切镜，不可拟合连续轨迹。冻结证据在第03包source_context_revision目录。原5源、对应渲染、直接叠图和两个主图像素全部未改；只更新解释与证据分类。\n';f.write_text(s)
stage=json.load(open(snap/'阶段结果.json'));stage['status']='HD_EVIDENCE_CHAIN_GEOMETRY_UNCHANGED_D_AUXILIARY_UNLINKED_PRIMARY_RESIDUALS';stage['source_fidelity_status']='NOT_ESTABLISHED_PRIMARY_RESIDUALS_REMAIN';stage['D_reference_class']='STATIC_NARRATIVE_BACKGROUND_AUXILIARY_UNLINKED';stage['D_same_model_or_layout_as_primary']='UNKNOWN';stage['D_count_difference_is_primary_geometry_hard_failure']=False;stage['E_to_C_continuous_camera_track']=False;stage['E_to_C_transition']='HARD_CUT_CONFIRMED_BY_CONTINUOUS_HALF_SPEED_PLAYBACK';stage['source_classification_revision_evidence']='source_context_revision/来源性质与切点复核.md';stage['source_pixels_unchanged']=True;(p/'阶段结果.json').write_text(json.dumps(stage,ensure_ascii=False,indent=2))
f=p/'qa/saved_main_verification.json';j=json.load(open(snap/'qa/saved_main_verification.json'));j['conclusion']='Geometry unchanged; D auxiliary static narrative background with unknown primary-layout linkage; primary source residuals remain; rejected branch excluded.';f.write_text(json.dumps(j,indent=2))
f=p/'qa/source_family.json';j=json.load(open(snap/'qa/source_family.json'))
for row in j:
 if row['old_camera']=='D':row['source_classification_revision']='Same old/new D image family only. D is static narrative background; association with primary model/layout unknown. Not a hard primary geometry constraint.'
f.write_text(json.dumps(j,indent=2))
f=p/'qa/D_root_cause_and_shift_sweep.json';j=json.load(open(snap/'qa/D_root_cause_and_shift_sweep.json'));j['interpretation']='The eight invisible desktops are fully outside the fixed D-camera frustum. This is a model-to-auxiliary-static-image diagnostic; D primary-model/layout linkage is unknown. Do not interpret12vs14 as a primary-scene hard failure or authorize geometry edits from count alone.';f.write_text(json.dumps(j,indent=2))
f=p/'rejected_shift/qa/change_manifest.json';j=json.load(open(snap/'rejected_shift/qa/change_manifest.json'));j['source_classification_revision']='D downgraded to unlinked auxiliary static narrative background. The count-only shift remains rejected; there is no justified shared-layout constraint from D.';f.write_text(json.dumps(j,indent=2))
f=p/'qa/camera_reference_manifest.json';j=json.load(open(snap/'qa/camera_reference_manifest.json'))
for row in j:
 if row['source']=='classroom_5447_key':row['reference_role']='AUXILIARY_STATIC_NARRATIVE_BACKGROUND_UNLINKED';row['primary_layout_identity']='UNKNOWN'
 if row['source']=='classroom_motion_4282':row['reference_role']='PRIMARY_CLOSE_SHOT_BEFORE_CONFIRMED_CUT_TO_C';row['continuous_track_to_C']=False
f.write_text(json.dumps(j,indent=2))
for f in [p/'scripts/verify_saved_main.py',p/'scripts/finish_package.py']:
 s=f.read_text().replace('HD_VERIFIED_CHAIN_GEOMETRY_UNCHANGED_D_NOT_PASSED','HD_EVIDENCE_CHAIN_GEOMETRY_UNCHANGED_D_AUXILIARY_UNLINKED_PRIMARY_RESIDUALS').replace('Geometry unchanged; source validation chain complete; D NOT passed; rejected branch excluded.','Geometry unchanged; D auxiliary static narrative background, primary-layout linkage unknown; primary residuals remain; rejected branch excluded.');f.write_text(s)
protected=json.load(open(p/'revision_pending/修订清单_待取证冻结.json'))['protected_pixels_sha256'];assert all(hashlib.sha256((p/f).read_bytes()).hexdigest()==sha for f,sha in protected.items())
(p/'qa/source_classification_revision.json').write_text(json.dumps({'status':'LOCAL_R2_PREPARED_NOT_UPLOADED','D_role':'auxiliary static narrative background; primary model/layout relation unknown','E_C':'hard cut, not continuous tracked motion','all_21_existing_source_render_overlay_files_byte_identical':True,'no_geometry_or_material_change':True,'numeric_metrics_unchanged':True,'frozen_evidence_file_count':len(hashes),'existing_main_images_unchanged':True},indent=2));print('Local source classification revision prepared; all21 protected images unchanged.')
