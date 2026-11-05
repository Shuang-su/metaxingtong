# v3真实修复：v2均值未应用

8d57874保存v2的图像节点实际使用8192×256点阵PNG，但构造脚本recipe路径仍指首256列横条版，实际Emission Strength6.33471584，而v2-status所写9.124373仅是新纹理配方计算值，并未应用。此错误经独立打开BLEND确认。v2四原件、图、记录、错误文案保持历史；其“均值已匹配”描述在此明确撤销。父仅实看类别，不曾确认强度或均值。

v3只修配方读取，不改图案频率、UV、几何、灯/World或其它材质。脚本build_band_experiment_v3.py显式读textures-v2/pattern-recipe.json并逐PNG SHA断言，独立另存export/roof-led-surface-v3四件/sidecar及execution-record-v3。旧v2不覆写。

新render_saved_v3.py实际打开保存材BLEND，断言节点strength与新配方误差<1e-6、两个packed PNG SHA与外文件同，再各重渲source11/close8s，不能复用错误强度的旧图。当前两张已实际查看，近景点阵类别清楚；source11只有侧缘有限入画，源台位置失败未变。

纹理均值定义/单位限制继续适用：只线性PNG按均匀面参数面积的平均发光亮度，不保证最终渲染亮度相等。正式独立技术QA与有限材白图尚待完成；SOURCE FAILED。
