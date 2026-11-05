# R04D：一次实际GLB+sidecar可见探针

输入是独立QA从空场导入R04D材质GLB、显式恢复sidecar后保存的BLEND。另行实际渲染SOURCE02，未补改几何、材料、World或灯，不覆盖四张正式来源比较图。探针是额外一次渲染，不把主图alias算一次新渲染。

事后读取两份冻结输入并应用各自脚本已记录的相同执行覆盖：Cycles采样96、固定4线程、无降噪、100%画幅。Cycles全部可读标量参数（含seed/自适应采样）、render、image/color management/display、World Background数值一致。差异是camera界面的焦距单位标签(MM/FOV)、session UID，以及相机矩阵约1.4e-7浮点差。该检查不是运行时逐参数仪表记录，不伪称早已记录。

实际图像RGB绝对差均值0.0360/255，96.1907%像素RGB完全一致，99分位最大通道差1/255，极值53/255，alpha一致。此为图级往返差，包含矩阵浮差、路径采样等可能因素，不把MAE归因为单独材质误差，不设原场还原验收阈值。

外观肉眼高度接近不能改变两个限制：GLB原生不含本场完整环境，必须用sidecar；source02/05仍来源FAILED，未恢复原光效、材质或完整场景。
