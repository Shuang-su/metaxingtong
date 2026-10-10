# KTV 显式时间布置状态候选

本研究候选只实现状态规则：复用同一份既有模型，沙发有/无状态由显式state或已观察timeline决定。没有修改共享几何、材料、物体坐标，没有保存覆盖模型，没有更改CURRENT或Library。来源几何还原、相机标定、用户验收均未通过。

## 结构与适用范围

- layout_state_manifest.json固定引用既有材质blend与既有GLB的SHA，不复制模型，也不导出两份静态GLB。
- 共享静态舞台保持原模型。18个沙发网格为家具主体；另有8个既有推断家具接触垫作为独立附件组跟随状态，总计26个可见性目标。
- 黄色星伙伴7件、气球狗10件是两个独立动态组，不受沙发状态控制。保留原始可见性与坐标，不新增人物、不生成运动轨迹。
- 当前blend的气球狗collection原本已隐藏；它在当前GLB中完全不存在。此候选没有补入气球狗，也没有把“没有狗的GLB”冒充完整动态场景。黄色伙伴7节点仍在GLB。
- glTF没有可移植的标准节点可见性属性，因此共享GLB通过消费端适配器切换18沙发+8推断附件节点的visible；不宣称普通GLB查看器会自动理解此manifest。不需要复制整套舞台几何。

## 时间规则

保守未知闭区间为[6626.597822,6627.396357]秒，包含两端。来源图的采样起点标签为[6626.598,6627.319]秒，没有精确视频帧PTS。

自动timeline只在两段实际观察链内选择状态：

- 6613.625823≤t<6626.597822：有沙发。
- 6627.396357<t≤6637.312808：无沙发。
- 7105.257433≤t≤7134.185133：无沙发。

这些区间由自然播放离散样本支持，不是逐帧穷尽。其余时间，包括A/B旧参考时刻、未观察的中间数分钟、保守切换包络，都返回unknown。不能外推到整个回放。unknown自动应用会拒绝；允许显式手动选择状态作标记清楚的检查，日志记录人工选择与时间结果。无效或非有限时间拒绝。

## 使用

工作区内已有ktv_fullroom/delivery/models/资产时：

```sh
# 交互打开共享模型，有沙发；不自动保存模型。
/usr/bin/blender --python scripts/open_candidate.py -- --workspace /path/to/workspace --state furnished
# 只在已观察区间按时间选择；6630秒为无沙发。
/usr/bin/blender --python scripts/open_candidate.py -- --workspace /path/to/workspace --source-time 6630
# 完整状态审计与已有GLB实际回导。
/usr/bin/blender -b -t 2 --python scripts/audit_states.py -- /path/to/workspace
# 每图单独持有并释放共享渲染锁。
bash scripts/run_renders.sh /path/to/workspace
```

消费端必须先把共享GLB原始字节交给scripts/layout_state_adapter.mjs的loadVerifiedSharedGlb(loader, bytes, manifest, bindingContract)。预检对精确字节计算SHA并校验GLB文件头、372节点数和26目标的原始名称/索引，再把同一批字节传给GLTFLoader.parseAsync。只有它返回的已验证binding能供applyLayout(binding, manifest, choice)使用；不能直接传任意对象树绕过校验。

每次显隐前还会复核资产/索引、加载后parser节点数和原始名称、唯一节点关联。运行时显示名允许被加载器清洗，身份取原始节点索引。glb_binding_contract.json独立固定期望GLB SHA、节点数和目标名，不改变此次Blender渲染输入manifest。文件被换、节点数错、原始名称错、未验证绑定、加载后数据被改、关联缺失或重复都会在写可见性前拒绝。

Node测试使用实际GLB字节和接收同一字节的模拟loader，另测运行时任意重命名与混合非目标可见性；还有Blender实际回导。没有冒称真实浏览器/GLTFLoader运行验收。

## 核验设计

- 18个既有相机×2状态，共36个组合；每态的完整对象/collection/view-layer可见性指纹在所有相机一致。
- 切换只改变18个沙发对象及8个推断家具附件的hide_render/hide_viewport，其余对象、动态组、collection和view-layer保持原状态。
- 每个物体的几何/UV/材质槽/变换指纹和材质节点指纹保持一致；状态往返恢复初始可见性。
- 闭区间端点、未观察时间、无效time、错误state和人工覆盖均有测试。
- 实际重新导入既有GLB，验证372网格、18沙发及8推断附件存在、两态往返恢复，7黄星存在、10狗缺失。

## 图证怎么读

边界前后的来源图复用刚完成的高清连续采集，不做重复seek。两张原始浏览器截图均为readyState4、1920×1080解码、1180×757截图；保留前后视频读数和原图SHA。它们提供有/无沙发状态证据。

只有这两帧无法唯一标定来源机位。因此两态都使用同一个既有01_front相机、同一共享几何与材料、相同48samples/seed/2线程，不声称它们匹配来源相机。渲染1180×664，按实测画芯y26.625四舍五入到y27嵌入1180×757黑边画布，没有特征拟合、裁切或扭曲。

源图与渲染画布直接50%叠加，机位、尺度、比例、动态人物和已有模型误差完整保留。原始render和独立OIDN副本都保留，4张叠图有逐像素公式校验。对照板等比缩小排版，不替代原图。

两个边界图时间都处于保守unknown包络，因此用于对照的是明确人工按图选择的状态。原渲染命令未传时间；单独render_source_associations.json记录来源前/后秒数、unknown查询结果和人工图像判态，不改写真实渲染命令日志。

此阶段能够证明状态规则独立于相机及共享模型不变，不能证明还原通过。后续若要提高几何准确度，需要独立的相机/尺度标定与来源几何任务。

技术实现参考：[Three.js官方GLTFLoader源代码](https://github.com/mrdoob/three.js/blob/dev/examples/jsm/loaders/GLTFLoader.js)。适配器使用node索引关联，不依赖加载后的显示名称；尚未做真实浏览器加载器运行验收。

## 18件初稿暴露的问题与明确修订

初稿只切换沙发collection的18物体，在无沙发态显露了8个小黑垫。投影框和原生成脚本证明，它们是结构collection中既有INFERRED_furniture_contact_pad至.007，与两把沙发的8只脚水平位置逐项唯一相同。这些垫是建模时推断的家具支撑附件，来源没有独立静态存在证据。

经明确复核，最终候选保留“18沙发主体”和“8推断附件”两个分组，同步显隐。不是将26物体都改称原始沙发，也没有改任何网格/材质/坐标。另3个接触垫.008–.010属于望远镜，继续保留。初稿16图及当时manifest/脚本/QA保存在historical_18_target_diagnostic，原问题和范围变化可追溯。历史诊断中的脚本不是当前入口；运行时只使用根scripts中的最终版本。
