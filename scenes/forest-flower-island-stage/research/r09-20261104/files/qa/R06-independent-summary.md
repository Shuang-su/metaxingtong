# R06 independent technical review

Exact file identities: R06-independent-roundtrip.json contains SHA256 for both blend and both GLB files. Material blend a2f8c2c379576dea097a4d58c76ab191c88be6cfe1aac9a0e37130a239de94ea; material GLB 486dffc2faa308552939400cec41a3bd5a9574b7953c5b4c15a28ecd543ee145. White blend 96d86e6ebe62ce049d859627310411d62059407e2dc507a8c20f730239ea99f9; white GLB 0c861f70234ef7a2a91036d43189970872e8840e554428c4423e7e21c5fb90e7.

PASS within technical scope:
- Each actual Blender/GLB variant has 625 meshes and 14 cameras, with all object names retained. World vertex nearest-neighbor differences in both directions are zero after actual GLB reimport.
- Material and white evaluated world mesh vertices/faces match exactly. Cameras and lights match exactly between blends. All white mesh assignments use WHITE_clay.
- Original meshes have zero detected nonmanifold edges, degenerate faces, nonpositive signed volumes and hidden meshes. Export split-normal seams close under diagnostic in-memory 1e-6 welding, with no resulting degenerate faces. No original model was changed.
- Reimported camera poses agree to floating-point precision; same-render-aspect camera projection ray slopes differ by at most 2.98e-8. Raw Camera.angle comparison is not appropriate across different sensor-fit settings; supplemental projection checks supersede that initial diagnostic.
- No external linked libraries. Three packed PNG image payload hashes equal the external PNGs and GLB embedded image bytes exactly.
- Bark, Leaf and Moss_and_earth now have GLB baseColorTexture references. R04's missing Bark/Leaf color problem is corrected. All 538 textured GLB primitives have TEXCOORD_0; original meshes have UVs with finite values.

Texture provenance and limits: these three PNGs are newly generated procedural PBR appearance assets, not source photographs and not baking of the previous arbitrary 3D procedural shader. Source-detail accuracy is unproven. Matching texture payloads and represented PBR fields do not establish whole-render equivalence across engines, lighting or tone mapping. No cross-engine render test was performed. General overlapping surfaces, contacts, complete object correspondence and source fidelity are not accepted by these topology/export tests.

Pending visual scope: final native-size material/white source renders, exact direct-50 overlays, and eight useful inspection views per variant. Prior high-frame object-count mismatch is not closed merely by adding two flowers; their positions/identities and all other vegetation still require source comparison. No reconstruction acceptance is granted by this report.

Evidence: R06-independent-roundtrip.json, R06-independent-extra.json, R06-texture-bytes.json, R06-packed-uv-check.json. All checks used Blender 4.3.2 read-only, one thread; reports and scripts written only to the independent QA directory.
