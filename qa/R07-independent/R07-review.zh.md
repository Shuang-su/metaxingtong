# 后台 R07 规范渲染状态/GLB画幅修复独立核验

R06→R07全部231mesh世界顶点/面、UV、5camera参数/矩阵、灯、world、hide、材质节点无变化。材白几何/UV/机位/灯/world/hide相同；没有新增对象或隐藏技巧。

实际读取R06，将preview_r06.py的明确执行设置仅施于内存（MANNEQUIN_local/CYCLES/64samples/no denoise/1192×671/100%/6固定线程），与R07保存状态比较：render、image_settings、Cycles、view/display settings全部标量/枚举/数组RNA字段、活动相机、world名字、帧/子帧及use_nodes均相同；只忽略输出filepath与派生file_extension。这加上既有几何/材质/光照一致支持明确复用R06已渲图。不是R07新渲染，也不是任意以后版本可复用。未从命名推断执行态，使用实际加载值验证。首次属性扫描遇EnumProperty无is_array API错误，失败日志保留，改getattr后成功。

R07两GLB实际空场景回导各231mesh/5camera，无缺失/新增。1192×671相同画幅下全部5cam归一化视框方向最大误差2.98023e-8，相机矩阵2.98023e-7；世界顶点双向最近最大4.76837e-7。此前R05/R06导出960×640后改1192×671的AUTO/VERTICAL视框差异，在R07规范画幅下修复；旧失败报告不删。GLB若再改成别的宽高比仍需明确fit适配，不声称任意画幅全等。

原R06两材白1192×671诊断图及其两个前后裁切已在R05-R06-review.zh.md实看/验SHA/像素；本报告仅证状态等价复用，不复制新图名。sourceFAILED、一个诊断角/非源机位、裤帽有限包含抽样、无脚/底座/完整壳、代理衣版/姿态等限制全部继续有效。

## 原件绑定
- R07_material.blend `d35a64a3f2ee81ecf4e3f72d2193155389aad3dc500c8334834b5e46a63492d9`
- R07_material.glb `d895e763465a932792c6c962106f9e7ea17b7acd0ae5b58a774f689128f8c0f4`
- R07_white.blend `72c90af9d26d2774357063c19a56da1b7b29948aa582aa6494cc6c5f08f136fa`
- R07_white.glb `f6cf73e7bf90bb58983ceb69662cf82414136a0b4fac3df9d7fc5719abfc87ad`

证据：R07-diff-check.json、R07-glb-projection-check.json、R07-executed-state-check.json及对应脚本/日志；旧camera-aspect-diagnosis和mixed-aspect-rejected失败均保留。


## 线程表述更正（追加真实版本，旧报告/JSON保留）
上文写6固定线程是脚本意图，原独立检查进程使用CLI -t1，机器记录实际两者为1，不能据旧JSON声称实际6。新独立三次读取证明：无CLI -t时保存态/执行态均FIXED6；-t1均1；-t6均6，其他所比RNA状态分别一致。CLI覆盖导致读取差别，不是模型/图被改。新无覆盖证据支持规范保存6及状态复用；不得把旧-t1测试冒称6。详../R09-thread-correction/R07-thread-correction-addendum.zh.md及三份新JSON/log，旧原文另存R07-original-report-before-thread-correction.zh.md。
