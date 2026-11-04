# R06 冻结独立技术检查（图像待完成）

版本130b5632b838729af6b97059849972d60640b924，实际读取versions/R06四原件，未改生产/未渲染，Blender4.3.2单线程。完整机器记录check.json/restore-check.json与复现脚本同目录。

SHA256：
- material BLEND 591c0347a4ab63be9f7c6028058874d846fb16e3ba10c5e4c18775a40ed06d06
- material GLB 5ad49c5884e9695dca74332ffd78079c8ffec15dc798be0258ce0ac750d031e2
- white BLEND 0c50e2b00305eb6335fed61bb163377e5754e8f905f17daf98fbdf929b48ea66
- white GLB ddefc745fec5d86b671b34901b8f0234fe494cfd3491cb260f5996fcc9c1c08e

## 实测通过的有限技术项

材白162求值mesh/11相机，世界顶点、三角拓扑、UV层、显隐标志完全一致，全部相机参数/世界矩阵一致。162单体非流形edge0、面积小于1e-12的face0、signed volume全正。R01负绕序、R04接缝内部面、R05中心松边失败均已在前版记录保留；本版本真实复跑，不继承早版哈希。

两个GLB分别真实空场导入：162mesh/11camera，无丢mesh/camera。全部mesh世界顶点双向nearest最大9.8302496099e-7，不是仅bbox；1192:671归一化camera viewframe最大3.6912e-8。导入后相机worldmatrix最大差4.1724e-7，见restore-check。media Solidify导出缺厚度已修。未用GLB回导重渲来证明材质视觉完全等价。

模型未使用外部图像纹理（check.json图像列表保留），材质采用程序节点常量；本次没有逐一证明所有非glTF节点语义/颜色管理跨软件一致。

## 灯光与World实际恢复

实际对两种GLB从空场运行制作方restore_glb_lighting.py，输出仅写独立QA目录restored-material/white.blend。World Background节点颜色(.035,.035,.07,1)、Strength.45及Surface连接与原BLEND完全相同。3 AREA的energy/color/DISK/size一致，世界matrix误差最大1.1921e-7；R05 rim sidecar错误已实际修。1192×671/100%、Cycles64sample/no denoise、active source21、AgX/None/exposure0/gamma1均精确相同。

原生GLB本身不含AREA灯/World；必须使用BLEND或配套restore，不声称其他查看器等价。GLB留下同名empty节点，恢复的实际灯名字会带.001；首次独立检查器错误假设完全同名而KeyError，失败脚本/log保留，随后按实际唯一基名匹配灯参数和矩阵重新完整运行成功，没有改生产脚本。CPU线程不在本次等价结论：CLI -t1会覆盖RNA值。

## 代表接触与未验范围

R06实际复核：凳面/凳腿0为8BVH面交叠对、琴体/琴腿0为8对、音板/琴体16对、四尖地纹/台面241对。琴盖到琴体最近顶点至表面为0但BVH0，不能称完整铰链/承载。白键00/18到外台仍约7.79e-6微隙（BVH0），原始结果保留，不称严格焊合；中央台到环步表面BVH0、最近vertex-surface约.01999只是上界，不是全feature连续距离。

R04另做过代表对象全AABB邻居检查，白键与黑键、黑键与粉环有真实交叠链，因此单对floor正隙不能判整体浮件。那份关系图只绑定R04，不移称本版全场验证。本版未完成所有物件包含/自交/支承图，接触也不证明Boolean融合、施工或物理承载。圆台缝隙、隐藏底部、球幕边界仍需来源/图像核。

正式来源直叠与八有效角本报告NOT RUN，待生产实际出图后逐图核。全部来源忠实度仍FAILED/未验收，技术修复不计来源通过。
