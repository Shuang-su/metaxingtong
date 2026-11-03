# R09b final incremental independent review

Outcome: conditional camera-fit improvement over R08, not accepted reconstruction. No new scene count: this is the same candidate revision. Reviewed 2026-11-03 04:20 UTC.

## Exact file identity
- R09b_material.blend: SHA256 2e8c8e319f2b0d59b6d68988660acbb14bcd466dbb9bb13267a6f16ef3885a96
- R09b_white.blend: SHA256 bf6ada2c9d8e1db3ddd19a232e8b679a7f95d225ffd7b4ff3d740ccd547a98b6
- R09b_material.glb: SHA256 48360a20d7e14ea167920fe177dafd44b5530ad7c2b776abf39216fac7de13c7
- R09b_white.glb: SHA256 04cbbacc0c2710aa0aa6dd023bbfc4e8424cb35582d9cfba63356d49de5d1129

## Shared geometry and export
Independent Blender 4.3.2 reads show R09b material and white each have the same 565 world-space mesh coordinates/topology as R08. Only D/E/F camera definitions changed. A/B/C and all eight inspection cameras remain unchanged; no hidden mesh flags. Material/white geometry and cameras match. No new geometry was introduced to improve only one image.
Both GLBs actually imported: 565 meshes each, no missing/extra meshes, max bidirectional world-vertex difference 6.743495646333031e-7 working units. GLBs are byte-identical to R08 exports because the geometry is unchanged and these exports contain ZERO cameras. Fourteen editable cameras are retained in each BLEND only. This is not a GLB-camera preservation pass. See R09b-independent-model-check.json.
The existing R08 topology/shell checks remain relevant to unchanged geometry; they do not certify measured scale, no intersections, or an airtight room. No exhaustive collision/occlusion test was added.

## Constraint review and preserved failures
All original 51 annotations remain recorded. Original R09 fit/render retained. F09 was disabled only after source-native crop inspection established that contact/shadow fusion did not justify the hard right-endpoint label. No replacement endpoint was invented. The review does not assert F09 contains no physical object. E has six scalar constraints for six pose variables; its near-zero training residual is saturated, not independent calibration. Manual uncertainties are subjective, and all frames/diagnostics have been seen.
R09b improves D/E/F versus R08 initial camera guesses, but is not uniformly better than R09. On the same eight valid F constraints (both excluding F09), R09 mean/max 5.371/22.434 px becomes R09b 6.590/33.012 px. F01/F02/F03 regress, while F08/F10 improve. Robust-cost selection alone does not establish overall accuracy.
New five front-base observations are diagnostic, not fitted or blind. Full-circle nearest distances give mean 18.201 → 9.053 px, but the R09 nearest locations all lie on the back-facing half of the circle. On the camera-facing half only, R09 errors are 79.58/75.75/68.74/58.56/46.43 px and R09b errors 7.26/5.18/.88/10.39/21.55 px. This supports better front-base orientation in R09b while preserving the top-rim regression. Half-space filtering is not complete ray-occlusion validation.

## Independent visible-arc confirmation
Producer R09c is a computation-only visibility variant: front base arc, named seat front/rear arcs, open arcs without a closing diameter chord, camera above cap. Independent dense arc calculations at the EXACT saved R09b pose yield mean/max D 1.61647/4.81961 px, E .000257/.001422 px, F 6.58986/33.00978 px. Sampled R09b-to-R09c projection changes are at most D .01882, E .00035, F .01307 px. Thus R09c supports essentially the same conditional pose, not a new accepted model or a reason to relabel R09b pixels as R09c.
All 1542 tested ring/line points per saved R09b camera are forward-facing. Exact Blender versus analytic pinhole projection discrepancy is below .000184 px. This verifies implementation on these samples, not the hypothesized source correspondence.
Ring-distance residuals use assumed geometric rings. The top ring (.315 radius, .903 height) is narrower than the wider outer profile (.322 radius, .882 height); observed silhouettes are not automatically those ring edges. Window midpoint fitting also leaves substantial left/right width errors. These caveats survive small training residuals.

## Actual images, reuse and arithmetic
Reviewed R09 trial D/E/F direct50 and R09b material F plus white D/E/F direct50 pixels. Material D/E in R09b explicitly reference the existing trial renders; no renamed duplicate was required. Independent comparison of trial/R09b scene matrices, modifiers, material slots/nodes/input defaults/links, light/world properties, visibility and color management finds only the F camera differs. Runtime session_uid was excluded as a non-render identity; the initial false-difference diagnostic is preserved. D/E camera definitions match exactly. Both preview configs use 8 samples, 6 threads, adaptive threshold .1 and native output dimensions. This supports D/E reuse without asserting a new render occurred.
All six R09b direct50 outputs independently satisfy full-array floor((source+render)/2) exactly, max error 0; source/render/output dimensions and recorded hashes match. D/E are 1920×1080 and F 3840×2160. See R09b-overlay-integrity-independent.json for exact image hashes and render paths.
Actual pixel finding: central stool and window vertical alignment improve visibly, especially compared with original R08 guesses. Remaining failures include curtain position/tie height, bed/headboard silhouette and layout, sill height/angle, bar position/thickness, wooden stool placement and skyline. E/F show large differences outside the fitted central features. Fixed lamp reflection and low-sample noise remain obvious. Material and white agree on these remaining structural errors. Overall source comparison remains FAILED.

## Limits and recommendation
Keep R09b as an explicitly unaccepted, camera-only conditional refinement with all R09/R09c and F09 review history. Existing R08 A/B/C and eight inspection views remain unchanged evidence, not newly rendered or newly passed in this increment. No whole-source acceptance, independent calibration, full room closure, source physical measurements, complete occlusion analysis, remote Git readback or Space cleanup is claimed here. The archival owner must verify the published bytes separately.
