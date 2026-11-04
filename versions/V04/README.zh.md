# V04 有界单角条件研究

入口：models/phone-material.blend / phone-white.blend，以及同名GLB。只把P04后片绕原轴从25°改为45°，其余对象、机位与灯光均保留。45°不是实测折角，来源整体仍FAILED。

- 正式最少检查图：renders/material-source7.png、material-side.png、white-source7.png、white-side.png。
- 两个源直接50%：renders/material-source7-direct50.png、white-source7-direct50.png。全画幅1080×603，不warp，不裁图拟合。
- 详细证据/限制：docs/report.zh.md。
- 完整25–55°扫描、原V03图、40/45低样本试验：diagnostics/。
- 独立扫描复算：independent-scan-qa/；新保存态与图像QA另列。
- 重建/场景恢复/正式渲染入口：scripts/build-v04.py、restore-state.py、render-v04.py、overlays.py。

底部被Logo/草遮挡、右伸亮带身份未定，不用它们宣称下缘或接地改好。只确认中段候选亮边更接近原像素主观带。当前仅一个来源假设机位和一个人工侧诊断，不称8角、完整新场或用户接受。
