# 霓虹舞房 · 留存最早可核实模型及说明

状态：重建候选 / 待来源复核。来源忠实度与几何技术检查分别记录。

### 最早可核实的留存包
旧包是霓虹拱景、柱、顶面线框、PERFECT、侧墙图案、箭头与收音机。后方开敞、墙顶有缝且部分管线字形装饰未封口。

这些是已恢复的历史实物；“最早可核实”不保证此前没有版本。
- `Xingtong_Dance_Studio_Neon_3D.zip`；11096603字节；Library版本0；SHA256 `0e5ea27297d7dc67011ec4d9bc28c084f49e0fd0bb977042502f1dd63d251fd3`。
  - 模型 `Xingtong_Dance_Studio_Neon.blend`：SHA256 `d5e020459a6e00943b810bda69c12adf259b80f3b7ec530cb825e7ad7932d534`。
  - 模型 `Xingtong_Dance_Studio_Neon.glb`：SHA256 `cffc394d17168596e85ceefb63a71e7c5ecc74b955f57a70de8924e9f3a5ede9`。
  - 模型 `Xingtong_Dance_Studio_White.glb`：SHA256 `78665c441007533f184080449ab4c9379ce91b7be711c146baa9b46b2be4ec36`。
  - 模型 `Xingtong_Dance_Studio_White.blend`：SHA256 `456e412403dae8995b6b2812f60173c99172ffb6ba538bb7b451b2e113224a21`。

#### 旧包说明依据：Xingtong_Dance_Studio_Neon_3D.zip 内 README_中文.txt
星瞳 3D 直播舞蹈房：霓虹表演状态重建

来源：星瞳官方 2024-04-19《与星瞳共度的一天》
https://www.bilibili.com/video/BV1mx4y1z7oY/

选用状态与证据
- 00:58:09：低机位霓虹广角，天花 PERFECT、裸露管线、拱龛、两侧柱、黄带、地面箭头可见。
- 01:00:10：略高偏侧广角，右墙绿色像素图案、收音机、后墙拱龛可见。
- 00:30:16 与 01:02:10：清洁紫色状态广角，核对相同拱门、凹槽大柱、细圆柱、三枚地面箭头、右侧收音机。
- 00:58:58：左侧近景辅助核对柱字与黄带。
播放器显示时间可能比截取定位秒数多 1 秒。重建只采用这个舞蹈房，未与视频中卧室、钢琴/沙发房或户外合并。

场景结构
01_Verified_room_shell：共享墙体、地板、内侧细圆柱、外侧凹槽圆柱与侧墙面板。
02_Arch_and_signs：拱龛与竖向板、实体向上箭头、DANCE STUDIO、两侧 PERFECT 标识、顶部线框与 PERFECT、三枚地面箭头。
03_Ceiling_services：梁、裸露管线和矩形风管。
04_Neon_state_decoration：黄色交叉带、墙上荧光涂写及绿色像素图形。与建筑独立，属于本次选择的表演状态。
05_Radio：右侧手提收音机的盒体、提把、双扬声器、网格与旋钮。
06_Lighting / 07_Cameras：灯光与固定机位。

真实几何与材质
主要结构、文字、灯管、箭头、柱肋、收音机均为可编辑 Mesh。没有人物模型、参考截图背景、投影映射或为了某一机位改变的几何。两个匹配相机和正常平视相机共用同一份刚性场景。
材质文件包含 UV，以及 Base Color、ORM（R=1，G=粗糙度，B=金属度）与切线空间 Normal 贴图。贴图既随 textures 文件夹外置，也嵌入 .blend 和材质版 .glb。发光使用 glTF 标准材质和 KHR_materials_emissive_strength。白模使用中性材质，保留相同几何、UV 与机位。

尺寸和不确定性
单位按米组织，但源视频没有标尺。可见房间宽约 10.0m、顶高约 3.8m、中央拱龛宽 3.7m / 高 3.3m，均为比例推定，不是测绘值。地板前向延伸与两侧墙前段不可完整核实；未封闭看不到的前墙。顶部管线的遮挡段与收音机微细结构为合理补全。
墙上荧光插画只用低清可见轮廓作平面近似，未把它做成场景人物。未编造不可核实的小字；黄带使用色块和短横标记代替细小印刷文字。字幕、播放器图标、水印和直播人物均不属于模型。

如何检查
01 / 02 为同一模型两机位材质渲染。
03_Normal_Material 与 04_Normal_White 为同一正常平视机位的材质/白模配对。
05 / 06 为相同匹配机位的白模。
Overlay_A_50pct / Overlay_B_50pct 为 50% 透明叠图。参考只裁去播放器边框，再等比例缩放至相同画幅；未做透视扭曲、局部变形或像素修饰来掩盖差异。
Compare_A / Compare_B 为参考与重建并排图。
最终渲染采用 Cycles 64 samples、4 CPU 线程，并使用独立 Intel Open Image Denoise 降噪。降噪仅处理渲染噪点。

文件
Xingtong_Dance_Studio_Neon.blend / .glb：霓虹状态材质版。
Xingtong_Dance_Studio_White.blend / .glb：同几何白模版。
validation.json 与 roundtrip_validation.json：UV、贴图嵌入、几何一致性及 GLB 回导检验。

#### 本阶段实际归档路径
- `scenes/dance-studio/01-retain-earliest-binaries/assets/Xingtong_Dance_Studio_Neon_3D.zip`；11096603字节；SHA256 `0e5ea27297d7dc67011ec4d9bc28c084f49e0fd0bb977042502f1dd63d251fd3`；Git blob SHA1 `e03eabbc2f29ec5ba977478558dc3aa1b79179af`。

#### 日期语义
- Xingtong_Dance_Studio_Neon_3D.zip：精确原始日期未知。只确认实际留存字节及内容阶段；未取得精确保存/制作/聊天发布日期。
聊天发布时间、原始模型制作日期及旧Git提交日期未获证实。新归档commit日期以实际执行时间为准。

共享标准：`docs/reconstruction-standard.md`。
本阶段是现有实物的候选快照归档；不是重新建模。
完整原始包未重打包、未改字节。
