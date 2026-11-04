# R01 冻结技术失败报告

真实检查98af3f44614a75be6f4f9a37d594258764da6971的四原件，已用git show提取到独立frozen/models，逐SHA在check.json。本轮曾先读生产根路径，但制作方已覆盖为变化阶段；首四hash与98af不等，因此保留mutable-path-read-check.json/log，不能当R01证据。随后真正对Git冻结四原件重新执行check_frozen.py与extra.py。没有改生产/重渲。

材白162 evaluated mesh/11camera，世界顶点、三角面、UV、显隐标志完全相同，camera同。单体evaluated非流形边0、面积<1e-12面0；25负signed volume：stage-central-solid、stage-step-ring、stage-outer-floor、inner-luminous-rim、key-pink-ring、four-point-concave-floor-inlay；12 upper-terrace/upper-edge；7 media-grid-lat。闭合拓扑不证明绕序正确。原始media mesh有176非流形边，由Solidify求值闭合；此事实不等于原始mesh已实心。先前仅由代码疑顶端退化，没有在实际face-area审计测到，不能把猜测写成已证退化。

双GLB真实空场回导各162mesh/11camera，双向全部世界顶点nearest最大差0.050000552，定位finite-media-surface-unresolved；其余约9.83e-7以内。Solidify厚度未等效导出，失败。1192:671画幅归一化camera viewframe最大误差约5.965e-8，世界matrix最大误差4.173e-7；不能用相机通过掩盖壳不一致。GLB未含AREA灯，不声称照明等价。

World实际use_nodes=True，Background Color约(.050876,.050876,.050876,1)/Strength1；world.color(.035,.035,.07)不是当前着色节点颜色。render-sidecar只记录world.color，不能准确恢复此场景，缺真实节点/连接恢复核验。

有限接触：bench-seat与bench-leg0真实BVH8面交叠对、piano-body-rim与leg0为8对，不等Boolean焊合/承载。其余严格世界Z分离已实际证实：soundboard对body .00399995；lid对body .06999993；inlay对中央台 .00200000；white-key00及18对outer-floor .14810173。表面BVH均0。stage中央与step ring表面BVH0，vertex→surface最近值约.01999只是连续最短距上界，未计算全feature连续距离。未核全场支持图/包含/全局自交，不把上述局部结果升级整场。

依赖图像列表在check.json，此轮没有源正式图验收。来源仍FAILED，R01应保留失败，不据此开完整长套图。后续不同冻结版本须独立检查。
