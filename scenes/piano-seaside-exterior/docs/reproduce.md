# 本地复现

已实际使用环境：Blender 4.3.2 / Python 3 / Pillow / NumPy，均为环境原有安装。没有添加扩展、软件包或凭据。首次Cycles降噪失败已留在R01；当前Eevee可真实渲染。启动时可能输出EGL警告，最终以PNG实际存在和解码为准。

从仓库根执行（新stage避免覆盖保留版本）：

```bash
python scenes/piano-seaside-exterior/scripts/make_textures.py
blender -b -t 8 --python scenes/piano-seaside-exterior/scripts/build_scene.py -- --stage r05-rerun --render all
blender -b -t 4 --python scenes/piano-seaside-exterior/scripts/validate_scene.py -- r05-rerun
blender -b -t 6 --python scenes/piano-seaside-exterior/scripts/render_glb_check.py -- r05-rerun
python scenes/piano-seaside-exterior/scripts/make_review.py r05-rerun
```

所有机位由脚本同时创建，几何/材质/灯光不按机位切换。当前只做共同近似黄昏状态；晚间来源依然使用这套状态显示残差。原生来源图不经过重采样、擦除或生成补图；叠图直接RGB 0.5 blend，同尺寸1920×1080；联系表缩小仅用于展示。模型单位不是米，不使用角色身高定尺度。

BLEND保存可编辑对象、修饰器、材质和打包的PNG。GLB以同一求值几何导出；木纹使用UV图片。沙地和海面使用可跨格式传递的基础PBR，未声称真实云图、潮位或波浪。QA回导BLEND仅为检查记录，不是新的源模型版本。
