# 配对同移屋盖a=.55有界实验最终状态

交付独立实验材白BLEND/GLB四原件及必要恢复sidecar、restore脚本。不替换R05/R06b或生产CURRENT。源验收仍FAILED，不是完整新场或完整检查套。

## 当前内容
- export/roof-paired-a055.blend 与 roof-paired-a055.glb：275mesh、11保留相机、原材质；只主屋盖缩脊单参数a=.55。
- export/roof-paired-a055-white.blend 与 white.glb：共享全部几何/UV/可见性，仅白材替换。没有实际白图，不称视觉验收。
- export/roof-paired-a055-recovery.json及scripts/restore_paired_a055_glb.py：补回GLB原生没有完整保存的World/AREA与精确相机/渲染配置。恢复方法只针对本输入，非通用无损工具。
- 仅4张真实1192×671/8sample材图：2基线+2候选，另4张原尺寸direct50与2张三联派生图。两候选图先在内存生成，后保存原件；实际275mesh哈希/摄像机/World灯材节点一致证据允许关联，不是新渲染。没有当前八角检查套。

## 有限结果与保留失败

原壳由默认Solidify生成，2145对原顶点有明确连接，非纯竖直挤出。新法给每对同位移，原配对向量保持、两完整檐管固定；其他48管每环SO3保径。原脊连接保留，避免强加新解析双坡等厚接缝。不是新坡法向等厚：Blender多边形法向夹角最高15.7023°、投影最小.115521；三角面积法向口径旧28.4688→新28.9585°，投影min.104996，不混用。

11顶杆宽度条件残差改善到±8.443px，但顶杆仍低31.169px，坡接仍低17.574px，下缘仍低约31..34px；10脊出画，下缘包络数字不变且语义/first-hit不足。台盘、侧屋、云形态及原穿插继续错误，不能称两源共同通过。

局部rib00左云三角交叠54→60；双向全质心有限包含指标旧/新保留，无更深穿入证据不是无穿插。非共顶点自交、退化、体积仅限定检查，不涵盖所有邻接折叠或全场连续包含。未扩参数、补洞或调灯掩饰失败。

## 独立核验

results/independent-baseline-qa、independent-a055-qa、independent-images-qa、independent-saved-qa完整记录实际验证及QA失败日志。保存态材白共享，双GLB空场实际回导全世界顶点集合双向误差0；双factory-empty sidecar恢复275mesh/11cam/3AREA，World及render同，camera浮差≤3.58e-7，灯≤1.50e-7。原生GLB裸lens因sensor归一化不等，但归一化视框射线差≤3.55e-8，不误报画幅失败。没有跨软件渲染等价实测。

早期报告的“尚未保存/独立QA pending”是其阶段历史，不覆写；本文件为当前总入口。export/artifact-manifest.json仍保留首freeze pending阶段字段，最终状态以上述实际独立报告为准。project_single_arrays旧x-field注释已在render-review单独作废，实际算法是配对+SO3。
