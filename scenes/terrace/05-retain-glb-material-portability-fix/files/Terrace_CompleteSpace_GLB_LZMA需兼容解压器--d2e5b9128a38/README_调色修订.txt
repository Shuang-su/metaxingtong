GLB BaseColor 调色可移植性修订（2026-10-10）

本次只修教室与露台GLB内7个BaseColor节点调色丢失；原主BLEND、主ZIP、空间几何、UV、相机、灯光和源匹配均不变。历史交付GLB未覆写。

方法：原PNG的sRGB像素先解码为线性RGB，在其后计算原Gamma(0.699999988)或MixRGB MIX(Fac0.449999988，线性Color2约[0.58,0.46,0.35])，最后编码回sRGB PNG。Alpha逐像素不变。仅目标材质改为独立烘焙贴图；共用原图的其他材质不受影响。保留所有原BIN字节，新增贴图资源，不重新导出几何。

教室：Ceiling / Chalkboard / DeskOak / FloorOak / Plaster共5个REVIEW lighter albedo材质。
露台：RearRail_PaleFinish_HYPOTHESIS与V4_Inferred_Tree_Leaf_Tone。

验证：Blender4.3.2重新导入新旧GLB后，几何、UV、节点变换、三角面材质槽的合并SHA256完全一致。教室1260网格、193828三角面；露台1416网格、805950三角面。原始GLB的全部二进制数据、所有原bufferViews以及所有非目标JSON值保持不变。

视觉验证：同一原BLEND几何/UV/灯光/世界/相机，仅更换真实GLB回导材质；Cycles CPU、8samples、seed17、无降噪/合成。仅问题材质的隔离对照相对原BLEND的全图平均绝对误差(0–255)：教室22.381→0.119；露台3.219→0.00996。全部GLB材质回导：教室26.167→4.682，露台3.509→0.345。余差是其他既有glTF材质近似，不能宣称GLB与BLEND完全同像。三联图按原BLEND、旧GLB、新GLB排列。

贴图烘焙有8-bit量化与纹理滤波近似；无画质重采样、无几何降面、无新UV量化。主BLEND仍为完整可编辑材质与灯光的主要文件。
