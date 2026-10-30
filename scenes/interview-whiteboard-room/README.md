# 面试白板房 / Interview whiteboard room

状态：2026-10-30 新建、未验收的有限室内空间候选。仅本地制作；无外部发布授权，不 push、不建 Issue/PR、不评论、不合并。

来源：星瞳官方 2026-04-24《一起去面试》，BV14ioLBAEDt，原生 1920×1080 PNG 两张。两帧各为正面宽景与有视差的斜近景；后一张人物严重遮挡，不能称完整多视角约束。不是既有 classroom 的固定黑板教室；未将同回放棕沙发招聘区、办公隔间或摄影背景并入此房。

## 范围与证据边界

观察：独立金属框白板、文字平面、单张木桌、黑色无扶手椅、左侧凸出墙角、右墙、深色踢脚线、地面。逐件轮廓与遮挡按两张原图检查。

推断：绝对尺度、白板底脚、后背/隐藏支撑、椅背隐藏轮廓、房间前端闭合墙与天花、墙厚和不可见接缝。以模型单位工作，不按角色身高标定。有限闭合内壳是可编辑建模假设，不证明未见结构真实存在；没有门窗证据，不添加门窗。

动态人物不建模、不合入白板纹理；来源原图完整保留。因此原图与渲染的人物区域必然不同，叠图保持直接50%混合，不能将人物消除或扭曲。

原图及原播放器记录：[sources](sources/)。原始 manifest 保持字节，实际正面捕获 currentTime 为 **1283.813032**，不是定位预览的1283.248；斜视为1505.632497。播放器读数不等于帧PTS。

模型、材料、照明、显示状态在各来源相机间共享。至少8张内部检查角度与来源机位分开；没有按相机隐藏墙或挪动物件。

## 阶段

- R00：来源下载、哈希/解码核验与范围冻结。
- 后续阶段与视觉缺口记录于 docs；文件或几何测试通过不等于来源验收。

## 当前候选 R04

- [可编辑材质 BLEND](models/r04/interview-room-material.blend) · [同几何白模 BLEND](models/r04/interview-room-white.blend)
- [材质 GLB](models/r04/interview-room-material.glb) · [白模 GLB](models/r04/interview-room-white.glb)
- [逐物件属性核验](docs/object-audit.md) · [逐实例 provenance](docs/object-provenance-r04.json)
- [几何与真实GLB回导](qa/r04/geometry-validation.json) · [桌椅白板三角面穿插检查](qa/r04/furniture-intersections.json)
- [阶段与失败记录](docs/stages.md) · [复现](docs/reproduce.md)

R04继承共享相机标定，修正R03椅背/后撑穿过桌后沿的问题；并未解决来源近景桌面遮挡冲突。来源图、失败候选、回导文件均保留普通原文件，不交付ZIP。
