# R06新版导出独立实核

实际从R06材白BLEND读取，再分别清空场景导入对应R06新GLB；不是引用R04旧导出结果。两版各187mesh/12camera名称完整。

材GLB SHA256：958f45d5b9e54cbedd22a8da02a99785dd1d80a4275e55bb97a7e930c67f7e47
白GLB SHA256：5085b7683b384367e29988b8986ce785dbc5e7c376b71da811172b2370f94b79

双向世界最近顶点最大误差4.777675712830387e-7；相机世界矩阵最大差3.5762786865234375e-7；相同1192×671视幅下归一view_frame方向差5.960464477539063e-8。所比较12相机均实际存在。

新增全部mesh双向角点属性检查：以2e-5世界位置半径寻找同位置候选，在候选中找匹配法线/UV的最小误差。位置候选缺失0，最终最大位置差4.77768e-7、UV差2.38419e-7、世界角点法线向量差5.90156e-5。法线存在小数值差，未冒称精确同值；这不是面索引一一一致或全渲染等价证明。地面另按世界角点/UV配对取整1e-5，材白均24独特配对完全相同。

GLB实际解析内嵌PNG并解码全数组：材地面baseColor和normal RGB与各原PNG差0，重打包roughness G通道与原灰值差0。normal scale=.5，floor有TEXCOORD_0；白地面WHITE_clay RGB约.35/roughness约.8，无图为预期。两GLB无外部buffer/image URI。程序石纹仍是合成代理，不是原来源材质恢复。

所核几何/灯/world差分与局部接触范围见R06-contact-review.zh.md；来源23-S3支撑线/可见性失败不变。正式渲染24图及6直接叠图本轮未检查，未提前声称有效8角、来源通过或全部交付完成。

数据：R06-glb-projection-check.json、R06-corner-attributes.json、R06-floor-uv-roundtrip.json、R06-texture-check.json及相应脚本/日志。
