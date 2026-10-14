# Issue #4 新增9处图证浏览器实显核验

核验日期：2026-10-14 UTC。

## 结论

**9/9处实显通过：PR55 1/1、PR56 5/5、PR57 3/3。** 所有图都在已登录的云端 Chromium 私有 GitHub Issue 页面内逐张查看至下边缘/图尾，未观察到坏链、部分加载或折叠。两张长联系图均以重叠截图检查到最后一行。

这里统计的是9处评论内展示位置；N640在PR55与PR57重复引用，不能称作9张新独立原帧。本报告仅确认浏览器展示，不代表几何、来源忠实度或用户验收。D未验收、J1拒绝、H旧85px撤回、模型未验收状态不变。

截图仅裁去账户/Issue侧栏、浏览器外框和无关页面范围，未修改图像内部内容。长图的证据分为重叠上/下段。没有以DOM解码检查替代实显观察。旧35/18图集不在本次复查范围。未改Git或Issue，未操作B站标签页。

## 逐处记录

### 1. PR55 图1：新无人医院原生帧：沙发扶手、上缘与绿椅无遮挡
- 评论：https://github.com/Shuang-su/metaxingtong/issues/4#issuecomment-6160480385
- 图URL：https://github.com/Shuang-su/metaxingtong/raw/4ec706a6f88dcb693742d9acf03e0bbb05d52644/scenes/hospital-room/research/source-acquisition-20261014/frames/BV1GqXMByE1s_640.406589_empty_hospital_native.png
- 截图UTC：2026-10-14T04:38:19.239Z
- 证据截图：PR55_01_N640_full.png
- 结果：完整实显，无坏链/部分加载/折叠。原图全幅至下方图注可见；与PR57 N640是相同源帧的不同评论呈现位置。

### 2. PR56 图1：医院右转 · 642.617525秒
- 评论：https://github.com/Shuang-su/metaxingtong/issues/4#issuecomment-6160654226
- 图URL：https://github.com/Shuang-su/metaxingtong/raw/5cd5259ca3851cdd053b5a79284051bb68257833/scenes/hospital-room/research/expanded-video-20261014/native_frames/BV1GqXMByE1s_642.617525_right_turn_native.png
- 截图UTC：2026-10-14T04:33:46.682Z
- 证据截图：PR56_01_right_turn.png
- 结果：完整实显，无坏链/部分加载/折叠。图像四边和图尾后的俯视图标题可见。

### 3. PR56 图2：医院俯视 · 665.501733秒
- 评论：https://github.com/Shuang-su/metaxingtong/issues/4#issuecomment-6160654226
- 图URL：https://github.com/Shuang-su/metaxingtong/raw/5cd5259ca3851cdd053b5a79284051bb68257833/scenes/hospital-room/research/expanded-video-20261014/native_frames/BV1GqXMByE1s_665.501733_downward_native.png
- 截图UTC：2026-10-14T04:34:19.688Z
- 证据截图：PR56_02_downward_full.png
- 结果：完整实显，无坏链/部分加载/折叠。全幅及后续联系图标题可见；人物遮挡是源帧内容。

### 4. PR56 图3：10:30–11:21 连续周期观察联系图 · 缩小派生图
- 评论：https://github.com/Shuang-su/metaxingtong/issues/4#issuecomment-6160654226
- 图URL：https://github.com/Shuang-su/metaxingtong/raw/5cd5259ca3851cdd053b5a79284051bb68257833/scenes/hospital-room/research/expanded-video-20261014/continuous/1025_initial_hospital_reveal/continuous_1030-1121_contact.png
- 截图UTC：2026-10-14T04:34:44.998Z；2026-10-14T04:35:05.238Z
- 证据截图：PR56_03_contact_upper.png；PR56_03_contact_tail_04_start.png
- 结果：完整实显，无坏链/部分加载/折叠。40格全部查看，顶部至编号39最后一格；以两次重叠截图覆盖。

### 5. PR56 图4：54:31–55:27 医院淡黑至校园表演插段 · 缩小派生图
- 评论：https://github.com/Shuang-su/metaxingtong/issues/4#issuecomment-6160654226
- 图URL：https://github.com/Shuang-su/metaxingtong/raw/5cd5259ca3851cdd053b5a79284051bb68257833/scenes/hospital-room/research/expanded-video-20261014/continuous/5430_hospital_to_insert/continuous_5431-5527_contact.png
- 截图UTC：2026-10-14T04:35:05.238Z；2026-10-14T04:35:23.552Z；2026-10-14T04:35:42.623Z
- 证据截图：PR56_03_contact_tail_04_start.png；PR56_04_transition_contact_upper.png；PR56_04_transition_contact_tail.png
- 结果：完整实显，无坏链/部分加载/折叠。43格全部查看，顶部至编号42最后一格；黑格是评论说明的源片淡黑阶段，后续校园格正常显示；最后一行仅3格为43张内容自然排版。

### 6. PR56 图5：校园分类参考 · 3600.996983秒 · 禁止用于医院拟合
- 评论：https://github.com/Shuang-su/metaxingtong/issues/4#issuecomment-6160654226
- 图URL：https://github.com/Shuang-su/metaxingtong/raw/5cd5259ca3851cdd053b5a79284051bb68257833/scenes/hospital-room/research/expanded-video-20261014/native_frames/BV1GqXMByE1s_3600.996983_campus_native.png
- 截图UTC：2026-10-14T04:36:02.384Z
- 证据截图：PR56_05_campus_full.png
- 结果：完整实显，无坏链/部分加载/折叠。全幅、评论末尾及无折叠状态可见；仅作校园分类参考。

### 7. PR57 图1：N640 · 640.406589秒 · 本阶段29分支来源之一
- 评论：https://github.com/Shuang-su/metaxingtong/issues/4#issuecomment-6160677630
- 图URL：https://github.com/Shuang-su/metaxingtong/raw/2ef168321ba28cbfa99bcfd94f5c6bfe2eb23dee/scenes/hospital-room/research/source-acquisition-20261014/frames/BV1GqXMByE1s_640.406589_empty_hospital_native.png
- 截图UTC：2026-10-14T04:36:56.334Z
- 证据截图：PR57_01_N640_full.png
- 结果：完整实显，无坏链/部分加载/折叠。原图全幅及旧G下一标题可见；不是新标注叠加图。

### 8. PR57 图2：旧G · 1116.180816秒 · 人物遮挡范围必须排除
- 评论：https://github.com/Shuang-su/metaxingtong/issues/4#issuecomment-6160677630
- 图URL：https://github.com/Shuang-su/metaxingtong/raw/2ef168321ba28cbfa99bcfd94f5c6bfe2eb23dee/scenes/hospital-room/verification/native-hd-source-recapture-20261011/frames/hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png
- 截图UTC：2026-10-14T04:37:13.564Z
- 证据截图：PR57_02_G_full.png
- 结果：完整实显，无坏链/部分加载/折叠。全幅及旧H下一标题可见；人物遮挡应排除。

### 9. PR57 图3：旧H · 1101.728114秒 · 不恢复旧85px统计
- 评论：https://github.com/Shuang-su/metaxingtong/issues/4#issuecomment-6160677630
- 图URL：https://github.com/Shuang-su/metaxingtong/raw/2ef168321ba28cbfa99bcfd94f5c6bfe2eb23dee/scenes/hospital-room/verification/native-hd-source-recapture-20261011/frames/hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png
- 截图UTC：2026-10-14T04:37:32.603Z
- 证据截图：PR57_03_H_full_tail.png
- 结果：完整实显，无坏链/部分加载/折叠。原图全幅及评论末尾可见；不恢复旧85px统计。

## 注意事项

PR56 第二张联系图中的连续黑格是源片记录的淡黑阶段，后续校园内容正常呈现；不是网页图像未加载。该联系图最后一行仅3格，与43张总数一致。

引用的当前main为8638dc96db6817ea907d97077260f91a812398b6，由任务上下文提供；此次只读浏览器检查没有重新核验仓库HEAD。
