# 后台局部组 R03 独立 QA

结论：限定接触修复成立，但新增服装相邻重叠、衣架悬空仍失败；所有来源仍 FAILED，不是整房或来源机位验收。

## 实际模型与导出
- 210 mesh / 4 camera。R02→R03 恰53物件变化（48伞骨+5衣物），其他157世界顶点及面序相同。所有相机、灯、world、可见性与材料节点不变；5衣物换网格伴随UV变化，不称所有UV保留。
- 材白世界几何、UV、相机、灯、world及可见性一致。所有单体非流形0、面面积<1e-12退化0、正体积；这不排除物体间重叠。
- 两GLB各实际清空场景回导210 mesh / 4 camera，无缺失/多余对象，双向世界最近顶点最大误差2.6656e-7；camera矩阵最大2.98023e-7，960×640归一化视框方向分量最大2.98023e-8。非渲染等价或逐角法线完全一致证明。

## 实际接触和反例
使用实际calc_loop_triangles、世界坐标、BVH面交叠及连续三角全特征最小距离（AABB下界剪枝）。
- 48伞骨→壳全部表面距离0；40邻段接链和8首段→hub均0。只是表面相交，不是Boolean焊合或机械支承强度证明。
- 5衣物→对应10衣架杆均距离0，各16 BVH面交叠对。
- 4对相邻衣物均距离0、各45 BVH面交叠对；相隔一件以上距离为正。RACK材白原图均可见相邻袖部黑三角，不能以单体闭合盖过此失败。
- 10衣架杆→RACK_horizontal全部仍有0.005085969–0.005086049正表面距离、BVH交叠0，断链未修。
- 对伞径向平面8边界重核，8最外段仍有顶点超出八边外轮廓，最大约0.00293工作单位。轴移没有隐藏该问题；投影超界不是全3D包容检测或来源轮廓误差。

## 六图与记录
实际逐张看R03 MAIN_local / TABLE_high / RACK_local的材白六图，均960×640。仅3诊断角，非6来源角。MAIN/TABLE仍有真实镜反射，白模去反射只因常量clay材质；RACK伞顶和架底裁切，衣物仍是无布料细节的挤出同形粗代理。白图低对比和噪点保留。
已对六图完整解码、SHA和模型SHA与posthoc inventory逐条复核，全部匹配。原preview脚本误写共享R01记录名的错误必须保留；此核只证当前文件身份，不把posthoc清单冒充原时刻运行记录，也不反向证明每幅图渲染时所有设置。

## 精确证据
- R03_material.blend SHA256 `781be4ddd62f727813fafbafe581399cd2ea60f7dcec77db67ac00b7cf04b7ad`
- R03_white.blend SHA256 `32312dd32fe7d05f4dd84a74f9ff64fd29450fb62b5a07b4dc06def9abe689f5`
- R03_material.glb SHA256 `cbc35de1f8c0c046b0e9f119078e1d901fa639db75c69172055689ab323c688e`
- R03_white.glb SHA256 `6f8dd4761f67e224d876b3f3e0c294c7e46f78e48855ddbd845b14566db69630`

同目录：R03-diff-check.json、R03-glb-projection-check.json、R03-contact.json、R03-hanger-bar.json、R03-rib-planar-perimeter.json、R03-viewed-images.json；各check_r03*.py及日志。未运行全面场景碰撞、自交、全周伞遮挡或来源标定。
