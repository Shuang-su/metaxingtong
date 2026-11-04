# R08 independent technical review

R06-to-R08 evaluated world geometry remains exactly identical for all 625 meshes. Only CHECK_01 through CHECK_08 camera records differ; all six source cameras and all lights remain exactly unchanged. Material and white R08 evaluated geometry, cameras and lights match exactly.

Both frozen R08 GLBs were actually reimported: 625 meshes and 14 cameras retained by name, bidirectional nearest world vertex error zero. Original topology and hidden-object checks show no anomalies. Diagnostic welding of export normal-split seams yields no nonmanifold edges or degenerate faces. Original models were not modified. Same-aspect camera projection ray slope error is at most 2.98e-8. These are technical checks, not source reconstruction acceptance or comprehensive scene collision proof.

Three new R07-named sRGB PNG textures are actually packed in material blend and embedded in GLB, with exact byte/hash matches to the corresponding external files. Bark/Leaf/Moss use baseColorTexture; all 538 textured primitives have UV attributes, with no missing/nonfinite original UVs. White mesh assignments use WHITE_clay. Texture provenance remains procedural, not source photographs or baking of the older 3D shader. Matching bytes does not prove full render equivalence.

R08 CHECK_02/03/05 low-sample white previews were independently visually inspected: flower island is not hidden by foreground tree trunks, and top/flower layouts are diagnostically visible. These are preliminary elevated angles only. Final eight-angle inspection must include useful underside/separation views and actual final material/white images; no eight-view pass is granted yet.

Final source-render overlays and source fidelity remain pending in this report. Source camera and geometry staying unchanged does not reduce already observed source mismatches. Source reconstruction remains unaccepted.

Exact files:
- R08_material.blend: 058d04b4bdfa72a4002f2952070c99f0685addb0e898fc8f57946bc29b31eb83
- R08_material.glb: 2dfd29c5790e261bb262f7e7db44e70ec3a61ef26df04fd912c0d0e541c78ff7
- R08_white.blend: c1fdb6291e6844d9c4e9874a9049f6f86493a8c2769a0a460eec73bdfe0e3fa4
- R08_white.glb: 2a0b3cb13a67ea692cc61f9542526753cf4c3dfd959260464676e8742ad83f85

Evidence: R08-independent-roundtrip.json, R08-independent-extra.json, R08-packed-uv-check.json, R08-texture-bytes.json. Blender 4.3.2, one thread, read-only.
