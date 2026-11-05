# R14 有限珠底接桌候选

仅将R13既有32颗珠代理统一平移Z=-0.007499992847442627模型单位，不改变XY、数量、局部mesh、材质或UV。材白各236个mesh，其余204个mesh、原9相机、灯与World保持原样。原R13冻结历史完整保留，未覆盖。

32珠对有限桌面的距离由0.007499992847442627变为0，每珠仅一个底点接触边界；这是表面接触，不是焊接、完整真实珠链、真实尺寸或来源验收。旧组内4对穿插（0–1、0–31、15–16、16–17）保留，未新增珠与旁物干涉。source009只支持珠链放在桌上的语义，不证明32珠或精确轮廓。source matching仍FAILED。

## 原件与恢复

models/R14_material.blend、R14_white.blend及对应GLB为独立原件。真实基线94395cddd15fc46a93cab6cc9e527eeab99c5d69，首次候选冻结4b670be4f2b2fbdbb1c3aefed4f5beddc2264ba9。精确原件SHA见qa/R14-build-record.json。

GLB并不独立包含完整Blender环境。原AUTO相机在回导中需侧记恢复sensor fit/画幅；World和AREA灯需恢复真实节点与参数。scripts/restore_r14_glb.py从factory-empty场景导入材或白GLB，再用qa/R14_*_camera_restore.json和environment_restore.json恢复。Background隐藏Weight=0在新节点不存在，脚本只对此已知零值作显式兼容例外，其他缺失输入仍抛错。原失败脚本/日志保留。具体独立恢复和剩余导出限制以独立QA为准，不能称GLB自行完整还原。

## 正式4图

renders/R14的R13/R14 × material/white四图为同一内存诊断机位的珠24及邻珠底部对照。原9相机没有改动或新增；诊断机位matrix和光学参数见qa/R14-render-records.json，可恢复。4图都为1192×671、Cycles 64 samples、无降噪、4CPU。材白前图可见明确悬空与分离阴影，后图可见底点接桌。粗球代理的棱面与旧链内穿插不在此修改范围。

原1CPU首次进程因中断消失，仅记录57/64且0成图，不能作为完成；恢复后1CPU重试被明确Ctrl-C退出130再切4CPU，未产出重复图。正式resumed4完成exit0，四图SHA/用时/模型哈希全记录。中断与恢复日志均保留于qa，详细执行链见R14-execution-recovery.json。

独立保存态、双GLB fresh恢复、4图核验现已完成，详见qa/R14-independent-final/review.zh.md和image-addendum.zh.md。World节点/输入/链接精确同，灯矩阵最大8.94e-8、相机相关总体最大2.68e-7；这只证明检查字段恢复，不证明跨软件渲染一致。4图单角局部仍有采样噪声、裁切和遮挡，不能替代全32珠几何核。
