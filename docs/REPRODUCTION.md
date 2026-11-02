# 当前重制作复现与证据边界

这是2026-11-02新编脚本的新正常Git历史，不能产生丢失F07旧SHA。旧F07的4项Library辅助文件只作失败参考，原生输入是本目录sources中的三张Nov2新补采PNG，各manifest写明实际time/hash/4K失败与1080回退。

## Blender实际已执行链

使用本机 `/usr/bin/blender` 4.3.2，无连接器/无新Codex制作任务：

1. `scripts/build_R00_platforms.py` 从空场景制作最小台盘；`check_render_R00.py`保留首白材丢失失败，`white_R00_repair.py`补可持久白材。
2. `fit_platform_camera.py`在NumPy/SciPy对手描轮廓极值作条件拟合；`R01A_platform_condition.py`实际改盘层/相机并渲染。没有把像素极值当固定世界点。
3. `fit_shared_inner_arch.py`仅两图软局部片段+弱先验，非唯一标定；`build_R01B_superstructure.py`产生共享几何/相机，三图实际失败保留。
4. `build_R01C_technical_camera.py`修LED文字方向与一个原本低于台面的机位条件；仍来源失败，23物体法线反向由actual audit发现。
5. `build_R01D_technical.py`仅修23绕序与两发光饰条+.012径向共面问题，保存材质/白覆盖/真灰材槽原件及2 GLB；`audit_R01D.py`与`check_R01D_shared_white.py`真实回导/指纹检查。
6. `render_R01D_suite.py`只读冻结D模型，新渲8结构角和3源各自原尺寸材白，Cycles CPU2线程32样本、无不可用降噪器；`finish_R01D_outputs.py`原尺寸直接50%混合并记录每项SHA，另生成标明derived的显示图。

命令均从本目录或以脚本绝对路径运行；脚本以自身路径定位本目录。生产 .blend不随渲染改写。审计world AABB不等于全材质/全拓扑视觉等价。269个mesh的数量不能替代逐物体来源验收。

## 相对深度可复现依赖

当前共享环境放在本目录旁 `depth-validation-20261102/venv` 与 `depth-validation-20261102/model`。未将venv或99MB官方权重打包进项目Git。`evidence/depth-packages-freeze.txt`锁实际包版本；`evidence/depth-model-artifact-manifest.json`锁官方repo、revision和各文件SHA。官方 https://huggingface.co/depth-anything/Depth-Anything-V2-Small-hf ，revision `5426e4f0f36572d16453bbda7a8389317b1bef99`，Apache-2.0。

离线推理前须先以官方允许下载取得该revision的 config.json、preprocessor_config.json、model.safetensors，并按manifest核验。CPU torch来自官方CPU索引、其他包官方PyPI；不用CUDA包、不读凭据、不加载pickle、不允许trust_remote_code、不绕过下载拒绝。工具验证repo保留实际安装日志/冻结包/模型API元数据。

`depth_first_source.py`使用共享环境做第一图真实分析；`depth_companion_sources.py`用同一model/config对另两图。输入始终原生源，模型网格约924×518，归一化灰度/显示上采样分开；灰色近亮只是相对逆深度，不是米制/亮度灰图。原网格float32保留；高分展示只是bicubic派生，不伪造原生4K深度。所有置信度unknown，掩码不完整；光束、薄杆、人物、反射及原实例状态未知，不作为几何真值。

## 未验收边界

当前粗弧/星链/背景/字带尺寸/材光及第三机位仍明显不符来源；外部弧端和后屏支承未完整建证，无全场基础/接触认证。冻结当前候选是为了保存可编辑实际进展与失败，不是用户接受或高质量还原完成。没有新增独立回放通过；全部三张都是训练。同一场重做不计当天真正新场景。
