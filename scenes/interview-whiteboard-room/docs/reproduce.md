# 本地复现与验证

当前环境：Blender4.3.2，Python3/Pillow/NumPy/SciPy；OpenCV5.0.0.93仅用于静态白板SIFT匹配，安装在本轮/tmp/interview-vision-deps。来源纹理与特征结果已提交，正常重新建模不需要联网或重新下载参考。没有授权推送。

在仓库根目录运行：

```bash
python3 scenes/interview-whiteboard-room/scripts/prepare_textures.py
python3 scenes/interview-whiteboard-room/scripts/fit_cameras.py
python3 scenes/interview-whiteboard-room/scripts/refine_shared_fit.py
blender -b -t 4 -P scenes/interview-whiteboard-room/scripts/build_scene.py -- --models-only
blender -b -t 4 -P scenes/interview-whiteboard-room/scripts/validate_scene.py
blender -b -t 4 -P scenes/interview-whiteboard-room/scripts/check_intersections.py
blender -b -t 4 -P scenes/interview-whiteboard-room/scripts/render_deliverables.py
python3 scenes/interview-whiteboard-room/scripts/make_qa.py
```

`render_deliverables.py`只切换相机/输出分辨率和采样，读取冻结材质/白模文件，没有按相机显隐、变形、材质或光照修改。它跳过已经存在的最终PNG以便断点接续；改模后必须另建阶段或明确移走旧PNG再渲染，不能混用不同几何。

标准Cycles CPU路径可运行。当前Blender没有OpenImageDenoise，所以保留采样噪声；不把画面噪声处理成伪细节。源图为1920×1080原生PNG，最终源相机渲染/50%叠图同尺寸；内部检查为1280×720。JPEG联系图中的缩放只用于展示。

模型内有完整推断内壳，各源相机和内部相机都在内壳里；检查05在狭窄白板背侧，检查07专门展示未知前闭墙。它们不是来源角度，不可增加来源覆盖统计。

白板纹理变换仅对源板面作有记录的四角逆透视UV提取；来源/渲染叠图从未透视扭曲。板面源照明仍存在；不得将其看作准确无光照反射率。

初期`export_checkpoint.py`为检查R03已保存模型而使用，最终R05产物由`build_scene.py --models-only`正常导出；最终真实回导报告位于qa/r05/geometry-validation.json，两套回导后的BLEND也保留。最终相机参数文件沿用camera-fit-r03.json，因为R04/R05修正共享几何，不修改相机。
