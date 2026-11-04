# R06 打开与复核

## 可编辑原件

从本仓库根目录打开 `models/lakeleaf-r06-material.blend` 或 `models/lakeleaf-r06-white.blend`，并保留旁边同级的 `textures/` 目录。四张外部 PNG 通过相对路径引用，不是 packed；依赖检查与独立复核均确认可读。材白共享 2704 个网格节点和 13 个相机，白模只替换诊断材质。13 个原件相机是 3 个主要来源假设、1 个辅助后近、1 个展示和 8 个内部检查，不能称 13 个来源。

`models/lakeleaf-r06.glb` 为材质导出，`models/lakeleaf-r06-white.glb` 为白模导出。实际重新导入均保持 2704 个网格节点与 13 个相机。材质版使用 PBR 常量和嵌入 PNG，不是意外默认白材；叶片颜色、湖色和水法线的嵌入图与外部 PNG 字节相同。粗糙度在 glTF 打包成 RGB 金属粗糙图，其 G 通道逐像素对应原灰度，不能声称打包前后整个 PNG 字节相同。叶舟材质与水面仍是原创代理，不代表来源光度拟合通过。

## 标准 GLB 的限制

标准 glTF 不保存本场俯视相机的离轴 shift。raw GLB 的相机 pose 存在，但该俯视投影不完全等价。完整参数在 `models/lakeleaf-r06-cameras.json`。`scripts/restore_glb_cameras_r06.py` 已实际把原材质 GLB 重新导入后恢复全部相机，产物为单独的 `models/lakeleaf-r06-glb-camera-restored-check.blend`；恢复后的 13 个相机才通过投影核验。不要把这个结果写成 raw GLB 自动保留全部投影。

AREA 灯、Blender 世界设置和 AgX/曝光不具有完整 GLB 可移植性。原 BLEND 保存这些状态；跨引擎画面不承诺相同。白模 GLB 的目的只是几何诊断，并非最终材质展示。

## 渲染与附加诊断的复现

全部图片来自 Blender 4.3.2 Cycles CPU，降噪关闭。正式来源图保持实际 3840×2160，检查图 1280×720，主图 1600×900。每张图片旁的 JSON 记录模型 SHA、相机、采样和实际线程。

R06 四张材质来源图实际为 2 线程。最初运行中的 Blender `-t 2` 命令行参数覆盖了程序内线程设置；没有把已在途帧打断。后续新调用检测到该覆盖后，在渲染任何图片前以真正 `-t 6` 重启该调用，实际 JSON 证明其余图片为 6 线程。`qa/thread-override-probe.log` 保存了该行为复现，不用线程预算替代实际记录。

环境在白模近斜图进行中中断，已完成的 16 张 PNG 解码与 SHA 检查成功，未重渲或覆盖。恢复入口为 `scripts/resume_final_r06_after_interrupt.sh`，旧日志保留；恢复证明见 `qa/r06/render-interruption-recovery.json`。若重新运行生产脚本，请先另存已有图证，避免覆盖历史结果。

额外低仰诊断由 `scripts/render_low_diagnostic_r06.py` 生成，仅在内存中新建一个相机，不修改或保存原 BLEND。相机完整 pose/lens/clip/尺寸及原模型 SHA 在 `qa/r06/low-diagnostic-camera-sidecar.json`，前后网格、13 个旧相机和可见性检查在 `qa/r06/low-diagnostic-invariance.json`。这张附加图不计来源数量，也不替代白模/材质各 8 个检查角。

## 复核的边界

主叶舟壳是闭合、有厚度网格；19 个脉管也闭合。515 个双面植物薄片、1 个水面、2 个有限岸顶面保持开放，没有假装全场水密。水面与壳的全局 z 范围重叠，只能说明无法找到一个同时高于所有水面且低于全壳最低点的相机高度，不能由此单独断言每处穿水或正确浮力。

已有 8 个内部检查角主要覆盖上方、斜方与近侧；完整底面和全部岸林没有无遗漏视觉证明。壳射线证明仅针对生成网格的垂向两次命中与相应厚度，不是来源尺度验证、法向厚度真值或全场连续碰撞证明。来源形态、森林实例、光照和水反射残差仍然存在，来源与用户验收均未通过。
