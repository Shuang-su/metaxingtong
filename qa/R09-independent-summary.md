# R09 independent review: technically intact, new 4K source visibly FAILED

R09 adds SOURCE_G_4K_top only. Independent actual evaluation confirms all 625 meshes exactly match R08 world vertices/faces, all old 14 cameras and lights remain unchanged. Material/white geometry, all 15 cameras and lights match each other. Actual GLB import retains 625 meshes and 15 cameras with zero bidirectional nearest world vertex error; per-mesh topology/hide checks have no anomalies. Camera projection and split-normal diagnostics are in R09-independent-extra.json.

Both R09 GLB binary buffers are byte-identical to their respective R08 buffers, and mesh/material/texture/image JSON fields are identical. No texture or geometry payload changed. This supports reuse of R08 technical texture checks. Existing R08 renders remain explicitly R08 outputs, not newly rendered R09 images.

G conditional training arithmetic was independently recomputed using actual Blender camera projection at 3840x2160: mean76.02268px, max178.25065px. Maximum disagreement with saved optimizer projections is0.000365px. This verifies arithmetic only. The annotation image shows approximate flower-cup centers, with subjective ±40px definitions and unproven object identities. The visibly possible unmatched front-rim cup is retained as uncertain, not deleted. All points are training data, not holdouts.

Visibility FAIL: ray tests toward provisional centers FLOWER_01/02/03/06/09/10 first hit FAR_TREE_17 or its branches about11 model units from camera, whereas target distances are32–37 units. The other five first hit their own expected flower centers. Six non-self occlusions explain the visibly dominant foreground trunk in the actual G preview. The original4K source shows a largely unobstructed high-air island. A fitted center projection cannot validate scene visibility/world state. No objects were hidden and no island geometry was moved to conceal this failure. Final G native-sized overlay is diagnostic, not source acceptance.

R08 six material direct50 images have been independently visually inspected: all fail source alignment. A/B plant order and camera/state mismatch, C flower height/background discrepancy, D forest density/trunk and island/environment relation, E underside and foreground leaf silhouette, F giant-flower arrangement/size/color and upper-background mismatch remain. R08 eight original material CHECK images were also inspected:01/04 contain foreground partial occlusion but still reveal layout/tree-island relations;02/03/05 expose flower/top layout from distinct azimuths;06 exposes side/rim and underside relation;07 is overhead;08 clearly exposes lower cone/root/airgap. They are useful diagnostic model views, not eight source views or proof of accurate reconstruction. White final checks and final overlay arithmetic are pending separate evidence.

Not run/accepted: full scene collision/contact test, exact source geometry/material identity, animation/world-state reconstruction, cross-engine render equivalence, later independent replay acceptance.

Exact file hashes:
- R09_material.blend: ee0b8fd08654d64fc2b914fe688e6d35dc97892063d95e0162e1d2c8cd77fd17
- R09_material.glb: 1668b5ea934e48110a119b88d32ca25e66a34e6653f84ac30dab7bf9d2bb0db6
- R09_white.blend: 84164fe4be25c34ec6a8a1ead46c8bf4338b8a104b202633850afdb636fea18a
- R09_white.glb: 0318d373a8e7b5e9d8d23d5ed1597880b378e74eb252c6a515e709212fdd78a3

Evidence: R09-independent-roundtrip.json, R09-independent-extra.json, R09-independent-landmark-check.json, R09-r08-glb-payload-diff.json.
