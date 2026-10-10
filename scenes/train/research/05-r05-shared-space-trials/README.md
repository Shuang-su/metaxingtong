# r05共享窗口与灯条诊断试验

研究/验证证据归档；来源未验收，不进入CURRENT。原图片和项目文件按原字节保存。

来源：https://www.bilibili.com/video/BV1fMP4ziEUd/

继承A2/B2/D2及新增J_empty_window_clean_paused、Dseq_03_clean_paused、Door_wide_59m53_paused，精确新增时刻以相邻JSON/manifest为准；59m53文件名不替代暂停实际值。

paused/readyState4、1920×1080解码，1180×757视口，内容约1180×663.75；固定整数裁图1180×664；源/渲染常统一590×332直接50%叠加，正常主图1180×664。

A/B共享窗带、洞、玻璃、框、墙板、帘/钩一致映射，灯高和货架横截面共享调整；家具数量/位置与车厢长宽/bay未改。B与A几何相同，仅新拟合相机。C与B相机一致，恰36个横档/灯壳/亮芯网格改变；J亮芯长度与横档为拟合数据，A/D提供留出方向支持。独立checkpoint已导出，4个新Library身份均已保存（材质/白模/诊断纹理证据/普通主图），仍是未整体验收独立候选，不替换r03/CURRENT；本次Git仅归档图证报告。

- review_b/*_r03_r05_same_camera.jpg命名错误：实际旧相机vs新拟合相机，不能当同机位几何归因。review_c/*_B_C_same_camera.jpg才严格同机位；归因由B_C_scene_state_check与B_C_attribution_check支持。
- J灰面/提手前景实体身份未定，非已证缺固定桌，不加/抬桌；J侧别与绝对bay未解。
- A/B/D靠背厚顶、斜率、排间可见层数、桌花遮挡仍不匹配；C不能因为局部灯条好转而称全图通过。
- 独立checkpoint保留端门框回导零角法线例外；技术回导不是来源验收。模型/GLB/纹理/大ZIP均不在此次图证白名单。

所有图片直接在对应Issue的阶段图证评论中展开；阶段manifest保存精确原件哈希。未知时刻和未观看区间不推定通过。
