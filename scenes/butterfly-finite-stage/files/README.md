# 冷态蝴蝶前侧主台：R04D有限候选，来源FAILED

最新可编辑原件：models/R04D_material.blend、R04D_white.blend；对应两个GLB同名。117网格/11相机，材白共享几何。仅有限前台、可见蝶翼前侧脉络/有界薄壳、中央塔弧片段及局部侧构件，不是完整舞台、城市或真实背面。

- 范围、逐部件残差与来源缺口：docs/finite-candidate-status.zh.md。
- 每个物体的可见依据/推断：docs/R04D-object-inventory.json。
- GLB完整环境需dependencies/R04D-environment-sidecar.json及scripts/restore_r04d.py；可在Blender运行 `blender -b --python scripts/restore_r04d.py -- material`。GLB原生不含本项目的World/AREA/画幅/active camera。
- 生成色区PNG在dependencies/R04-generated-color-regions.png；BLEND已打包、GLB已嵌入并实核像素。它不是源纹理，生成脚本不读取源图像素。
- 来源比较：renders/R04_source、R04_direct_comparison。四图真实执行态R04，R04D只改CHECK机位，可凭独立等价核复用；不是重渲。
- 8检查角×材白正式输出：renders/R04D_checks，以实际文件和render-log.json为准。均是模型诊断，不是来源角。原R04/C裁切失败与D低采样预检保留。
- 独立技术QA在qa/independent-R01、R03、R04、R04D。正式像素/八角审核单独保留，技术通过不提升来源等级。
- 深度真实数组/掩码/参数与失败分析在depth。它是未知尺度相对深度，发光翼、塔缝、人物、反射与字幕不可靠。

来源：2024-08-04报道 https://www.bilibili.com/opus/961640175446786069 ，演出2024-08-03，官方身份桥 https://www.bilibili.com/video/BV1CW42197tV/ 指向直播BV11E4m1R716。报道图1192×671和封面1007×630均非本轮解码的原生视频帧；片内时间/最高解码质量/第三结构角/后续同场复用/全部旧场逐像素排重未齐。只02/05冷态基准，06暖态不混几何。

本套件20张正式原图＝4张R04实际来源条件机位渲染（经D状态等价核复用）＋16张D实际检查渲染。主图只是材质CHECK01同字节alias，不是第21张独立渲染；另有1张独立GLB+sidecar探针。8检查角不等于8个来源角，未覆盖完整真实背面或台底。

普通Git保留真实脚本、原件、输出和失败；无LFS、ZIP或强推。本地freeze不等于远端交付，外部归档另核。所有版本包括R04D仍为有限候选、双源FAILED。
