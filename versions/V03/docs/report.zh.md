# V03：机位持久化与指标勘误

V03仅修正可复现性，不改几何/材质/灯光，不重新渲染等价图片。V02与V03材质、白模的10物件顶点/面/变换/材质参数逐项完全相同，见qa/unchanged-geometry.json。此前后片过宽、底缘与源失配仍为FAILED；不会因为几何导出合格而改写来源验收。

## 纠正误差说法
V02原记5.2229px是四点共8个像素坐标分量的RMSE，不是四点欧氏RMS，也不是四点平均距离。四点欧氏RMS为7.3863px，逐点约6.935–8.102px，具体数值见qa/corrected-source-errors.json。只有四个人工不确定角点、固定比例/焦距先验，不能认作真实机位标定。V01较小数值4.5113也属于坐标分量RMSE，其后片左露出方向错误仍为失败。

## 文件与机位
models/phone-material.blend与phone-white.blend均保存5个实体机位：SOURCE7_CONDITIONAL_NOT_CALIBRATED，以及DIAGNOSTIC_front/rear/side/top。BLEND默认激活来源条件机位。GLB两份均真实导出10mesh与5camera；没有在文件中伪造不支持的AREA灯或world。

qa/material-scene-state.json与white-scene-state.json保存每机位4×4世界矩阵、焦距、sensor_fit/尺寸、clip、shift、DOF开关、画幅/像素比例；同时保存两盏AREA灯的矩阵/能量/尺寸/颜色和world、色彩管理/曝光/gamma、CPU/samples/去噪状态。

GLB真实重新导入后，5个原生相机对10物件世界包围盒角点的投影最大误差0.000378px（固定1080×603，图像高度603，不得改成605）。GLB消费者必须遵循glTF相机aspectRatio/yfov。Blender载入时若需准确复现灯/world/画幅，可执行scripts/restore-state.py；它只恢复场景状态，不修改几何。恢复后的最大投影误差0.000216px；这些是数值比较，不是新渲染验收。GLB不承诺跨软件渲染器像素一致。

## 图片身份与历史
V03首个机位持久化提交802c073未生成新图。准确复用V02主图及4最终诊断图，路径/角色/相机/SHA见qa/reused-render-map.json；不是把旧图伪装成新输出。直接50%叠图继续引用V02/renders/source7-direct-50pct.png，仍为未标定的条件诊断。失败V01、裁切失败图、V02模型及早归档均未覆盖。

目前结论：仅有限技术导出/同几何/装配检查通过，来源仍FAILED/待补源；不算完整新场、不算独立来源验收，不代表用户接受。

## World恢复失败与修正
独立QA发现首版sidecar仅记录world.color=.22，但实际启用节点，Background真实颜色为(.05087608844,.05087608844,.05087608844,1)，Strength=1。首版恢复并未保证真实节点，不能称灯光状态完整。失败sidecar/脚本/测试记录保存在failed-world-state-attempt；模型本体World未变，因此无需重渲已有V02图。

修正版保存World节点bl_idname/输入默认值/连接，恢复时清空再建节点，并实际恢复Background Color/Strength及Background→World Output.Surface连接。自检改为先将fresh GLB场景world=None再恢复，防止沿用原BLEND World掩盖遗漏。原文件含内部Weight=0隐藏输入，新建Background无此socket，首次逐项设置抛KeyError亦保留；修正版仅明确跳过该隐式零值，其他缺输入立即失败。Color、Strength与真实连接重新读回见camera-roundtrip.json，不把world.color当渲染Background颜色。

## 独立V03技术复验结论
independent-v03-final-qa保留独立首次失败与修正后检查。修正版两种World节点值/类型/连接全等；恢复后的相机视框零差，机位矩阵约1e-7浮点差，不能称字节精确相等。5张复用图SHA、4诊断recipe相机已核，没有重渲。V02的独立源FAILED结论未变；这里只解决文件机位和照明状态复现，不产生新的来源验收。


## V03白模图追加
在机位修正后仅新增白模source7与side诊断两图（renders/white-source7.png、white-diagnostic-side.png），从V03白模BLEND保存机位直接渲染，4CPU/16 samples/无去噪，1080×603。模型/机位/灯光未改；材质图仍复用V02，不重渲。white-source7-direct-50pct.png为同原图与白模透明图固定纯黑底后直接全画幅50%混合，无warp/对齐。白模图仅验证可见几何与文件，不消除来源FAILED。

白图独立附录已完成，见independent-v03-final-qa/white-image-addendum.zh.md及white-image-integrity.json：两白图和叠图实际查看，尺寸/哈希/alpha边界吻合；固定黑底合成后50%取整全数组误差0。白源偏亮低对比、侧内面噪声仍保留，不因图可打开称源通过；后片宽/底缘错位依旧FAILED，仅1源假设机位+1人工侧角，不是8个检查角或多源确认。
