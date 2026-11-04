# R04 independent technical review

Scope: frozen production commit 87ebd89; exact file SHA256 values recorded in R04-independent-roundtrip.json. Read-only Blender 4.3.2 actual import, one CPU thread. No production files modified.

- Material and white each contain 611 evaluated meshes and 14 cameras. Evaluated world mesh vertices/faces match exactly between the two blends; cameras and lights also match. White mesh material assignments exclusively use WHITE_clay.
- Each blend has zero inspected nonmanifold edges, degenerate faces, nonpositive signed volumes and hidden meshes. This is per-mesh technical evidence, not full-scene collision/contact proof.
- Both GLBs actually reimport with all 611 mesh and 14 camera object names. Bidirectional nearest world vertex coordinate error is zero. Exported split normals cause 16 meshes to have disconnected raw edge indices; diagnostic in-memory welding at 1e-6 eliminates these nonmanifold edges with no degenerate faces. The original exports were not modified.
- Camera world matrix maximum error is 1.94e-7. Actual projection-frame ray-slope maximum error at the original render aspect is 2.98e-8. Raw Camera.angle differs because import uses a different sensor fit; do not interpret that unnormalized diagnostic as a FOV failure.
- No linked Blender libraries or external file images found.

FAIL / export material limitation: material GLB contains no images/textures. Bark and Leaf have no exported baseColorFactor, so use glTF's white default, not the Blender procedural appearance. Bark noise/ramp/bump and Leaf object-random/ramp are not carried into GLB. Moss/earth and rock procedural bump also do not export. Ordinary PBR constant colors and roughness are represented for the other materials. Recommend an explicitly documented constant-color export fallback or real baking; do not claim render equivalence. Preserve R04 unchanged.

NOT ACCEPTED / not tested here: source geometry fidelity, all-source direct overlays, eight useful inspection-angle final rendering suite, complete object correspondence, comprehensive scene intersections, animation reconstruction. Nine initial giant flowers do not account for at least eleven visible large cup candidates in the 3050.458712 high native frame; uncertain cases and approximate centers are in 3050-large-flower-review.json. Existing camera-only manual training has large reported residuals and is not an acceptance test.
