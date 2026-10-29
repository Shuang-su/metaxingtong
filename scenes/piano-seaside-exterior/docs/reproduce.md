# 本地复现

已实际使用环境：Blender 4.3.2 / Python 3 / Pillow / NumPy / SciPy 1.17.0，均为环境原有安装。没有添加扩展、软件包或凭据。首次Cycles降噪失败已留在R01；当前Eevee可真实渲染。启动时可能输出EGL警告，最终以PNG实际存在和解码为准。

从仓库根执行（新stage避免覆盖保留版本）：

```bash
mkdir -p scenes/piano-seaside-exterior/qa/r07-rerun
cp scenes/piano-seaside-exterior/qa/r07/camera-anchor-fit.json scenes/piano-seaside-exterior/qa/r07-rerun/camera-anchor-fit.json
blender -b -t 8 --python scenes/piano-seaside-exterior/scripts/build_scene.py -- --stage r07-rerun --render all
blender -b -t 4 --python scenes/piano-seaside-exterior/scripts/validate_scene.py -- r07-rerun
blender -b -t 6 --python scenes/piano-seaside-exterior/scripts/render_glb_check.py -- r07-rerun
blender -b -t 4 --python scenes/piano-seaside-exterior/scripts/render_white_review.py -- r07-rerun
blender -b -t 4 --python scenes/piano-seaside-exterior/scripts/check_piano_joints.py -- r07-rerun
python scenes/piano-seaside-exterior/scripts/make_review.py r07-rerun
```

所有机位由脚本同时创建，几何/材质/灯光不按机位切换。当前只做共同近似黄昏状态；晚间来源依然使用这套状态显示残差。原生来源图不经过重采样、擦除或生成补图；叠图直接RGB 0.5 blend，同尺寸1920×1080；联系表缩小仅用于展示。模型单位不是米，不使用角色身高定尺度。

BLEND保存可编辑对象、修饰器、材质和打包的PNG。GLB以同一求值几何导出；木纹使用UV图片。沙地和海面使用可跨格式传递的基础PBR，未声称真实云图、潮位或波浪。QA回导BLEND仅为检查记录，不是新的源模型版本。

R07共同角度/相机参数来自`fit_source_cameras.py`的明确人工点假设；重新求解会写入qa/r07/camera-anchor-fit.json，复现实验应复制到新stage，不覆盖保留版本。脚本、输入参数和模型均随真实commit保留。

## R09 共同环境阶段

使用已安装 Blender 4.3.2、Python/Pillow/NumPy/SciPy。先保留 R08 原文件；不运行早期 `build_scene.py` 覆盖 R08。以下命令在本场目录运行：

```bash
python scripts/make_environment_textures.py
blender -b -t 8 --python scripts/build_environment_r09.py
blender -b -t 8 --python scripts/render_environment_r09.py -- preview
blender -b -t 8 --python scripts/validate_environment_r09.py
blender -b -t 8 --python scripts/validate_scene.py -- r09
blender -b -t 8 --python scripts/render_environment_r09.py -- full
blender -b -t 8 --python scripts/render_environment_r09.py -- white
blender -b -t 8 --python scripts/render_glb_check.py -- r09
python scripts/make_review.py r09
python scripts/make_environment_review_r09.py
```

`full` 的主输出固定 S40；S105 全部来源另在 `alternate_S105/`，不按相机切状态。HDR 世界、场景灯光与相机不是此 GLB 导出的内容，跨软件需显式载入 `textures/r09/S40_sunset.hdr` 或 `S105_bluehour.hdr`。GLB 回导图只验证在保留的 Blender 世界/灯光中导入后的表现。真实时间状态值均是候选，不是光照测量。
