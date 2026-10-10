# 开放露台 · 记录GLB颜色响应修复

状态：重建候选 / 待来源复核。来源忠实度与几何技术检查分别记录。

### 独立GLB颜色响应可移植性修复
V10→V13说明记录共享太阳强度和后栏浅木面；GLB后续将后栏混色、树叶Gamma烘入独立纹理，不改变原几何、UV或节点变换。
原BLEND未修改；原GLB二进制buffer、已有bufferViews、全部几何/UV/法线/索引和节点变换保持；只追加颜色贴图资源并改相应baseColor引用。
修复项目：
- RearRail_PaleFinish_HYPOTHESIS：MIX_RGB响应固化到独立贴图，原alpha不变；旧图SHA256 `ad70862745047fc7f05b97ef3ab2851b273b47f21ed7f50908f3bfbd910b31a0` → 新图SHA256 `7b1db66786bd11adcd84589d3e4e09048cf969f306d293761a508774ee5258f4`。
- V4_Inferred_Tree_Leaf_Tone：GAMMA响应固化到独立贴图，原alpha不变；旧图SHA256 `26ed773767a25531785a9afedef2338b83140095fd152f967b24d94e81462744` → 新图SHA256 `3c340985bd16be75e72aae3b48e5ffed62cc6f45cf79966e87682b15453bb3c2`。
- 旧GLB：33658432字节，SHA256 `d303270a27552ce33b932da59e959920fd1bcf0ffa0592b18e2c9702776ffade`。
- 新GLB：34076844字节，SHA256 `9c4551b99e20b02a8c0a29f2115f2c83bbf28ae18c5628228263d6cd8b12435d`。
该修复不是新几何版本，不修复原来源拟合残差。当前文件清单中的独立GLB/GLB压缩包已是修复后交付；BLEND主包仍对应完整几何阶段。

#### 2026-10-10 逐场来源覆盖补充核验
- 新1920×1080解码；1180×757/1180×664；6751裁图1178×662；旧部分裁图1353×760。
- 登录后采集：未知：未找到可关联该场有效帧的登录状态日志。
- 独立角度：至少低斜与正面2族；6751=2727族、6821=5586族，中近景不可逐张增加基线。
- 新证据使用：独立6帧补采包到最终交付引用未证实；另V15已有6751高清实际用于共享外观/花团修改及低机位对照，最终完整空间继承V15并做来源相机回归。。
- 跨视频后续回放：未证实：已检查记录只有单个BV；同BV更晚时间不等于后续其他回放。
- 原生1080导帧未实现。总体来源验收仍待复核。详见 `scenes/terrace/source-coverage-audit-20261010.json`。

#### 本阶段实际归档路径
- `scenes/terrace/05-retain-glb-material-portability-fix/assets/Terrace_CompleteSpace_GLB_LZMA需兼容解压器.zip`；17108443字节；SHA256 `d2e5b9128a3826b72a639f3bddc8881881bc60df77a8bfb826c0bdea5063c9ec`；Git blob SHA1 `b21e9a3546fe86ff04bbd98eb34c032cb8404778`。
- `scenes/terrace/05-retain-glb-material-portability-fix/qa/terrace_complete_candidate_20261010_source.png`；159269字节；SHA256 `545ee02bb9d22e17e2b0cac580ba40d37102436ae2b2e54346b716f6f8358d3a`；Git blob SHA1 `1caa80313e9225cf7c409b67d97cebe61de751e4`。
- `scenes/terrace/05-retain-glb-material-portability-fix/qa/terrace_complete_candidate_20261010_glb_color_only.png`；159117字节；SHA256 `f6c920c98f707a14419857a5ec9403f442ebfaaeb625ca20817a2921f52c6eaf`；Git blob SHA1 `cd393247c35216316506cedb403ef4f4b6077429`。
- `scenes/terrace/05-retain-glb-material-portability-fix/qa/terrace_complete_candidate_20261010_repaired_color_only.png`；159295字节；SHA256 `b153449ffa67b21ecf4a4463ea6b282a496a2276310469648975903b69473128`；Git blob SHA1 `32f9300eaf018b02571a3b5973048d71983da4e5`。
- `scenes/terrace/05-retain-glb-material-portability-fix/qa/terrace_complete_candidate_20261010_glb_materials.png`；158847字节；SHA256 `223974bf6ade829fd7c69e9a74133ce9665ea05d76024531e6377fe85612bb43`；Git blob SHA1 `34328980f211912dd2fc179f3ab3f0a3e0ce4fc4`。
- `scenes/terrace/05-retain-glb-material-portability-fix/qa/terrace_complete_candidate_20261010_repaired_all_materials.png`；159116字节；SHA256 `c299dd24af03014bda5dd7cfb89aed84b0b2e4619a8325be237060217b0c099d`；Git blob SHA1 `f9bf25f7a28b6c97cdedb55ac27750f0975d5c47`。
- `scenes/terrace/05-retain-glb-material-portability-fix/qa/material-portability-evidence.json`；5793字节；SHA256 `20334606a332a73c5fe859ebf526f17bb47e481fca918b05fb4df45920f53a21`；Git blob SHA1 `9ec52b26570ce5464202751b903bcf93121af364`。
- `scenes/terrace/source-scope.json`；2698字节；SHA256 `4827314824cc21cffce03452dbc8f2232a141ef5ad5b2e7bb8508d94d014cb23`；Git blob SHA1 `b8fbf7283d78085431a6b158c0720fb0f75df8b0`。
- `scenes/terrace/source-coverage-audit-20261010.json`；2371字节；SHA256 `671618096e2e8d7768401ff8e2185a63152a003b9b5958775a76d072e1dc2fa6`；Git blob SHA1 `50afd2b8f410c04083fb7dabcf547fbf764df010`。
- 相同字节复用 `scenes/terrace/05-retain-glb-material-portability-fix/qa/terrace_complete_candidate_20261010_source.png`；SHA256 `545ee02bb9d22e17e2b0cac580ba40d37102436ae2b2e54346b716f6f8358d3a`。

#### 日期语义
- Terrace_CompleteSpace_GLB_LZMA需兼容解压器.zip：library_item_created_at=2026-10-10T02:40:41.551009Z；library_item_modified_at=2026-10-10T06:06:43.385810Z。Library条目创建与最新修改事件；创建时间不等于当前版本发布时间，修改时间不是聊天发布时间。
聊天发布时间、原始模型制作日期及旧Git提交日期未获证实。新归档commit日期以实际执行时间为准。

共享标准：`docs/reconstruction-standard.md`。
本阶段是现有实物的候选快照归档；不是重新建模。
完整原始包未重打包、未改字节。
