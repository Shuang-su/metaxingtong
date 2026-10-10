# 城堡花园 · 留存最早可核实模型及说明

状态：重建候选 / 待来源复核。来源忠实度与几何技术检查分别记录。

### 最早可核实的留存包
旧包为开放花床、栏杆、玫瑰柱、花拱与有限城堡门窗立面。旧README追述V1→V2压缩纵深/改花拱、V2→V3改UV和花色，但未恢复这些阶段独立二进制。

这些是已恢复的历史实物；“最早可核实”不保证此前没有版本。
- `01_Garden_White_Model.zip`；11673823字节；Library版本0；SHA256 `acd24106e5d0b63986e253a5268987002de86ef6e36f1b3e03f50d3e02a3f281`。
  - 模型 `models/Xingtong_Castle_Garden_White.blend`：SHA256 `75f7a65493ff0192812ccea44d4ab214bc36df5b6df35e36e2e30eae5f891991`。
  - 模型 `models/Xingtong_Castle_Garden_White.glb`：SHA256 `ee32e1706af252be69941b29d8fb0e0f456c62a6a9612d44b2c247cf56ef0280`。
- `04_Garden_Views_and_QA.zip`；13040755字节；Library版本0；SHA256 `84205b28850bbfa67f809a9cd536f12dc06482c3af057928fd1afcd3899c5ef7`。
- `03_Garden_Textured_Blender_and_PBR.zip`；15625202字节；Library版本0；SHA256 `3dc0049facf882ef19dc78922d7d349ec7ac5c22b7087156afb2652e0fd2b03d`。
  - 模型 `models/Xingtong_Castle_Garden_Textured.blend`：SHA256 `fa8de8260492464d21f740555877e7e890947eef0b6359c7c0ac15eb86d1dc8e`。

#### 旧包说明依据：01_Garden_White_Model.zip 内 README.txt
XINGTONG CASTLE GARDEN ENTRANCE — editable reference-based reconstruction

Source: https://www.bilibili.com/video/BV1aw411T7ws/
Primary garden frames: 00:21:59 and 00:25:11. Secondary frames: 00:11:06, 00:15:06, 00:20:09, 00:26:39, 00:27:43, 00:28:41. The supplied evidence manifest records the capture history; excluded_stale images were never used.

Deliverables
01: White clay BLEND + GLB.
02: Textured self-contained GLB.
03: Textured BLEND with packed PBR images, external PNG textures and editable scripts.
04: Normal wide/oblique renders, camera-matched renders, 50% overlays, source references and QA.

What is supported
A straight purple-dark paved axis; paired dense flowerbeds with low pale stone edges; balustrades and urns; nearby climbing-rose uprights; a farther flower-covered arch with a small center dip; purple-gray masonry facade; pointed dark double door; tall cyan windows with dominant dark vertical divisions. Meshes model the visible scene rather than displaying source frames on image planes. The livestream character and UI are not reconstructed.

What remains approximate
This is a scene reconstruction from compressed livestream images, not recovered production assets or a photogrammetric scan. Relative dimensions and camera solutions are approximate. Ornamental door panels, urn profiles, individual flowers, exact masonry/paving patterns and fine surface appearance are simplified procedural interpretations. Visible window vertical divisions are retained; unsupported repeated diamond lattice was removed. Dense planting is represented by editable petal and leaf surfaces, grouped into material batches. Some fine plant surfaces are two-sided, zero-thickness sheets. Matching camera views preserve the same world model; lighting differences and the occluding character limit direct comparison.

Explicitly omitted / inferred
The building roof, upper silhouette, complete castle footprint, hidden garden perimeter, reverse view, surrounding landscape, interior and hall connection are not observed and are not invented. The facade is a finite visible patch. The thin support slab, unseen backs, clipping edges and metric scale are construction conveniences. Wide and oblique views intentionally reveal those limits.

Version improvements
V1 to V2: compressed excessive garden depth, increased facade/door presence, corrected flower arch center sag, aligned foreground bed ends, and oriented climbing leaves and roses toward the viewer.
V2 to V3: corrected world-scale masonry UVs; added dark marbled and bordered paving; muted excessive blue/white flower brightness; removed unsupported diamond leading; increased floral density. Final overlay fit widened path and far arch and adjusted matched camera framing. Comparison files retain honest residual differences.

Textures / interoperability
Procedurally generated basecolor, roughness and normal PNG sets: violet masonry, aged limestone, purple paving, dark wood, cyan glass and foliage. Other flower/stem materials use explicit PBR color constants. No livestream frames were baked into textures. BLEND has packed textures; GLB embeds them. White and textured variants use identical geometry, UVs and cameras; only surface materials/light settings differ. Open the BLEND normally in Blender or import the GLB into a glTF-compatible editor. Units are arbitrary metre-scaled working proportions, not surveyed measurements.

QA
qa/roundtrip_validation.json records source meshes, imported GLB geometry, embedded texture checks and coordinate tolerances. qa/variant_uv_validation.json verifies native geometry and UV identity. Standard overview cameras show the complete reconstructed patch. Overlays are diagnostic 50/50 blends, not an assertion of pixel-perfect correspondence.

Lighting note
Final matching views use a darker nighttime setup and low-emission blue glazing. Normal textured overview renders receive a 1.5x area-light boost solely for legibility. White-clay versions use neutral inspection lighting. These are rendering differences, not geometric differences.

#### 本阶段实际归档路径
- `scenes/castle-garden/01-retain-earliest-binaries/assets/01_Garden_White_Model.zip`；11673823字节；SHA256 `acd24106e5d0b63986e253a5268987002de86ef6e36f1b3e03f50d3e02a3f281`；Git blob SHA1 `a9c8ed0f7eb79ac0f1ff45ade5ef97f55e317d17`。
- `scenes/castle-garden/01-retain-earliest-binaries/assets/03_Garden_Textured_Blender_and_PBR.zip`；15625202字节；SHA256 `3dc0049facf882ef19dc78922d7d349ec7ac5c22b7087156afb2652e0fd2b03d`；Git blob SHA1 `402ff2b8ddb09169f7b19b69d43a94bd7101218c`。
- `scenes/castle-garden/01-retain-earliest-binaries/assets/04_Garden_Views_and_QA.zip`；13040755字节；SHA256 `84205b28850bbfa67f809a9cd536f12dc06482c3af057928fd1afcd3899c5ef7`；Git blob SHA1 `dd997ec420500d92f40e89b8a7a94e72f005d7d0`。

#### 日期语义
- 01_Garden_White_Model.zip：精确原始日期未知。只确认实际留存字节及内容阶段；未取得精确保存/制作/聊天发布日期。
- 03_Garden_Textured_Blender_and_PBR.zip：精确原始日期未知。只确认实际留存字节及内容阶段；未取得精确保存/制作/聊天发布日期。
- 04_Garden_Views_and_QA.zip：精确原始日期未知。只确认实际留存字节及内容阶段；未取得精确保存/制作/聊天发布日期。
聊天发布时间、原始模型制作日期及旧Git提交日期未获证实。新归档commit日期以实际执行时间为准。

共享标准：`docs/reconstruction-standard.md`。
本阶段是现有实物的候选快照归档；不是重新建模。
完整原始包未重打包、未改字节。
