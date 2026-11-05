# Current branch: wing-sign exploratory addition

Read docs/sign-scope.md first. The inherited base-scene final report below is historical, not acceptance of this addition. Current sign r00 has recorded topology failures and only two low-sample previews.

# Seaside three-arch finite foreground reconstruction candidate

**Not accepted; source gates FAILED.** Model units are arbitrary. The scene is a finite foreground study, not a complete seaside venue. No claim of native frame acquisition, highest-quality playback, independent later-video angle, calibrated camera, metric scale or hidden-space recovery.

## Editable deliverables
- models/material.blend / material.glb
- models/white.blend / white.glb, same mesh coordinates and camera collection
- models/environment.json, required for GLB World/AREA lights and exact camera/render settings
- scripts/restore.py: Blender4.3.2, factory-empty GLB import and explicit sidecar restoration
- source/03.webp and 04.webp: original1192×671 report-image bytes, unknown video timestamp, not native video frames
- source/depth: actual Depth Anything V2 relative-depth research and limitations, no metric or geometric validation

Reconstruction generator sequence: build.py → apply_camera04.py → capture_environment.py. Model revision r03 changes SOURCE04 only after r02 geometry, and shares all scene objects across every camera. No image planes, screenshot textures, per-camera geometry changes, warped overlays or character proxies.

## Known failures and uncertainty
- Missing native highest-quality source chain and later independent same-scene replay angle; 03/04 are near-frontal and insufficient to establish hidden depth.
- SOURCE04 bounded fit hits y/z constraints. The 6-feature component RMS is a descriptive fit residual, not calibrated pose accuracy. Original wrongly identified arch-endpoint observations are preserved and corrected to null.
- Source material, sky and lighting differ; purple World is an explicitly simplified environment proxy, not the sunset reconstruction. Signage, wings, dynamic effects, people and reflection figures are not static geometry.
- Six narrow gold insets retain approximately .0025-unit gaps to their parent arches. Full structural/support/contact gate remains unpassed. Hidden arch support, pavilion depth/roof, umbrella base, back walls and chair joints are not source-confirmed.
- Lower circular light inserts partially overlap inferred panel surrounds in projection, a known layout defect. Approximate rail/panel counts and spacing are not verified individually.
- r00/r01 umbrella shaft was disconnected. r02 changes close actual triangle distance to all8 ribs and8 canopy segments; intersection is not welded topology or physical stability.
- World/AREA/camera restoration is actually executed. Cycles samples are32 and denoising is disabled; restore.py is specific to this scene and currently writes32 rather than universally loading all possible Cycles fields.

## Evidence history
r00 initial model and low preview; r01 category/composition/chair changes; subsequent r01 failure record preserves interrupted render subset and stale matrix problem. r02 repairs shaft/diffuser contact and captures camera state after updating dependencies. r03 camera-only fit retains rejected wide fit and approximate landmark tables. Formal suite and direct50 all-array report appear only after actual completion; consult qa/render-*-validated.json for model SHA, dimensions, samples and image SHA.

Independent technical QA is under qa/independent-r02 (read its scope and failures). It is not a source-accuracy approval. Every completed version remains in ordinary Git history; no LFS, ZIP, public share or rewritten history.
