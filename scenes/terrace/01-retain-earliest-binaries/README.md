# 开放露台 · 留存最早可核实模型及说明

状态：重建候选 / 待来源复核。来源忠实度与几何技术检查分别记录。

### 最早可核实的留存包
先有秋季露台包，再有同一露台绿色换装包；不能算两间新房。保留甲板、栏杆、井格、L形木墙、拱洞及家具共享结构。

这些是已恢复的历史实物；“最早可核实”不保证此前没有版本。
- `02_Seasonal_Terrace_Textured_Blender.zip`；11373711字节；Library版本0；SHA256 `eeff7b8549057fc350dbec17e6f789b1cdfc2553d2c0aa5a8f7a6f0a19755a7d`。
  - 模型 `models/Xingtong_Seasonal_Terrace_Textured.blend`：SHA256 `82ed16241f92f40bb548de833add5e56fccd0e1ecec69e70d64248f3d1fa07f9`。
- `02_Green_Textured_Blender.zip`；10145889字节；Library版本0；SHA256 `28c8898b95396d093685523a8d547b38a3c5ea25db3967ac2af28f1ecbcd5302`。
  - 模型 `models/Xingtong_Terrace_Green_Textured.blend`：SHA256 `125b93e42ef6691ae452bbc060ec35ff9ce811c3b927dc7c7d7504a8e1109d6e`。
- `02_Seasonal_Terrace_Textured_Blender.zip` 的Library条目首次创建：2026-10-07T23:29:37.449464Z；不等于聊天发送时刻。
- `02_Green_Textured_Blender.zip` 的Library条目首次创建：2026-10-07T23:59:28.756838Z；不等于聊天发送时刻。

#### 旧包说明依据：02_Seasonal_Terrace_Textured_Blender.zip 内 README.txt
XINGTONG SEASONAL ROOFTOP TERRACE — autumn reconstruction v1

Source: https://www.bilibili.com/video/BV1g64y1P7VV/
Livestream replay: 你和我的季节限定, January 19 2024.
Primary front reference 29:46; unobstructed floor 31:57;
independent low-oblique geometry/pergola confirmation 45:27.

Open models/Xingtong_Seasonal_Terrace_Textured.blend or White.blend in Blender 4.3+.
GLB versions are portable mesh + material exports. Cameras/lights stay in BLEND.
10 editable collections distinguish deck/gravel, fence, suspended chair, autumn
tree, easel, feature wall, moon/table, arch, generic distant backdrop and cameras.
All visible assets are mesh geometry, including chair ribs/chain, tree branches,
individual lobed leaves, gravel, pergola, boards, and arch opening. No screenshot
billboards or character cutouts. White and textured versions share the same mesh
geometry. UV PBR albedo/roughness/normal texture PNGs are supplied and packed.

What is inferred or simplified:
- Relative proportions from low-resolution video; absolute metre scale is assumed.
- This is the visible terrace zone, not an entire apartment or whole roof.
- No hidden home interior, unseen opposite boundary, or full roof perimeter.
- The arch is open; its thickness/reverse closures are approximated.
- Tree branching/leaf placement, wicker weave, plants and moon markings are
  procedural approximations, not exact original assets. Plants are simplified.
- Easel canvas artwork is left blank because it cannot be reconstructed reliably.
- Distant city masses are explicitly labelled generic approximations, editable in
  their own collection. They are not surveyed skyline reconstruction.
- Source character, UI, subtitles, foreground occluders and moving effects omitted.
- Winter (10:55) and green-season (1:33:06) share the same terrace architecture;
  their trees/snowmen/gifts/balloons are alternate dressing, not extra spaces.
  This release models autumn only. Variant references are included as evidence.
- Primary camera is manually fitted, not calibrated. Comparison overlays expose
  remaining discrepancies; no claim of pixel-exact or survey-grade reconstruction.

Review: renders/Final_*_Wide_clean.png = clean level wide view;
Final_*_Oblique_clean.png = normal oblique geometry view;
qa/Reference_White_Textured.jpg and qa/Final_Overlay.png = same-camera comparison.
qa/Iteration_Comparison.jpg documents the sparse initial blockout, pergola/tree
proportion correction, dense canopy refinement and final source camera/light pass.
Final wide-view QA also repaired deck extent and pergola support/chain connections.
qa/roundtrip_validation.json records native and GLB geometry comparisons.

Reproducible scripts: textures.py, build.py, refine.py, polish.py, finalize.py,
validate_roundtrip.py, denoise.py, package.py. Renders use Cycles; clean previews
use Open Image Denoise as image postprocessing, with raw PNGs retained separately.


#### 旧包说明依据：02_Green_Textured_Blender.zip 内 README.txt
XINGTONG — SAME TERRACE, WINTER AND GREEN-SEASON DRESSING

These are two seasonal dressing variants of the terrace already delivered in autumn form. They are not two additional rooms. The existing deck, inset, steps, fence, pergola, cedar feature wall, side table and arch geometry/coordinates/UVs are preserved. The autumn originals were not overwritten.

FILES
Each season has an editable .blend and portable .glb, separately in White and Textured forms. White and Textured versions have identical geometry and UVs. Packed PBR texture maps are embedded in textured files. GLBs contain only that intended season and exclude inactive seasonal objects. Blender files open at a normal-wide inspection camera. MATCH_A and WIDE_Oblique cameras are also provided.
Optional Xingtong_Terrace_Three_Season_Switch.blend: choose 01_AUTUMN_delivered_base, 02_WINTER or 03_GREEN from Blender's Scene selector. Core collections are shared across all three scenes. This combined file has no combined GLB; use the individual seasonal GLBs for clean exports.

SOURCE AND SCOPE
https://www.bilibili.com/video/BV1g64y1P7VV/
【直播回放】【3D】你和我的季节限定 2024年1月19日19点场
Winter references: 10:55, 16:06, 20:17, 25:10.
Green references: 1:33:06, 1:40:28, 1:50:22.
The evidence manifest and sampled reference frames are included with the review package. The prior source review was distributed sampling, not a continuous watch. Multi-minute coverage gaps remain.

WINTER
Snow-flocked conifer with individually modeled needles, branch scaffold, warm lights, gold baubles/bows, wrapped gifts, additive snow layer, low timber bench and two snowmen. The autumn tree, chair, easel, leaf scatter and moon are absent. Camera-visible prop categories and layout are supported; exact ornament counts, twig details and snowflake placement are approximate.

GREEN
Broad-leaf tree, leafy understory/pale pots, retained chair and easel, simplified pale teddy/cloud-like base and pink/cream balloons. The autumn leaf scatter and moon are absent. Artwork on the easel is intentionally left blank; unreadable lettering and illustrations were not invented.

LIMITS
Relative proportions reconstructed from low-resolution video; metric scale is assumed. Small foliage, snowman facial details, teddy details and ornament shapes are approximate. City silhouettes are generic background stand-ins inherited from the delivered base. No unseen home interior, opposite terrace boundary or complete roof perimeter is claimed. The inherited shared architecture was not resurveyed or redesigned for these variants.

REVIEW AND VERIFICATION
Source-match comparison sheets and 50% overlays are unwarped comparisons to the same inherited MATCH_A camera. They expose remaining differences rather than claiming pixel identity. Iteration sheets show the canopy/understory and conifer corrections. Normal-wide and oblique white/textured views are provided.
QA JSON reports: native white/textured geometry equality, per-season GLB roundtrip object coverage/triangle counts/bidirectional vertex distance/area, finite UVs and normals, embedded textures, variant isolation, and preservation of shared core topology/transforms/UVs. Every delivery ZIP is tested for CRC integrity and is below 18 MB decimal.

#### 本阶段实际归档路径
- `scenes/terrace/01-retain-earliest-binaries/assets/02_Seasonal_Terrace_Textured_Blender.zip`；11373711字节；SHA256 `eeff7b8549057fc350dbec17e6f789b1cdfc2553d2c0aa5a8f7a6f0a19755a7d`；Git blob SHA1 `b01156fbe952a4c2469419877b1c05b99ac44d4f`。
- `scenes/terrace/01-retain-earliest-binaries/assets/02_Green_Textured_Blender.zip`；10145889字节；SHA256 `28c8898b95396d093685523a8d547b38a3c5ea25db3967ac2af28f1ecbcd5302`；Git blob SHA1 `c33d285b0cd53f8ef5dbd6d66ce5206f4212ccd1`。

#### 日期语义
- 02_Seasonal_Terrace_Textured_Blender.zip：library_item_created_at=2026-10-07T23:29:37.449464Z。同身份未修改的Library条目首次创建时间；不是模型制作/聊天发布时间。
- 02_Green_Textured_Blender.zip：library_item_created_at=2026-10-07T23:59:28.756838Z。同身份未修改的Library条目首次创建时间；不是模型制作/聊天发布时间。
聊天发布时间、原始模型制作日期及旧Git提交日期未获证实。新归档commit日期以实际执行时间为准。

共享标准：`docs/reconstruction-standard.md`。
本阶段是现有实物的候选快照归档；不是重新建模。
完整原始包未重打包、未改字节。
