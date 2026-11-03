# R08 final independent QA — candidate, not accepted

The four exact inputs below were independently opened/read in Blender 4.3.2. Final image review completed 2026-11-03 01:52 UTC. Model conclusions are bound to these exact file hashes, not a future Git HEAD.

- R08_material.blend: SHA256 `edb6d27130bc42f8f2a9ecb4e2149439ff07459a1a4d7b91a88270e058d2f4e5`
- R08_white.blend: SHA256 `53136e1b905d440f1b7bb0e45794ea262cd81ea57c36f9107a6134fd223c74c6`
- R08_material.glb: SHA256 `48360a20d7e14ea167920fe177dafd44b5530ad7c2b776abf39216fac7de13c7`
- R08_white.glb: SHA256 `04cbbacc0c2710aa0aa6dd023bbfc4e8424cb35582d9cfba63356d49de5d1129`

## Limited technical passes
- Material/white versions have exactly matching 565 mesh names, world-vertex and face-index hashes, and camera definitions.
- Both GLBs actually imported; no missing or extra mesh objects. Maximum bidirectional world-vertex difference is 6.743495646333031e-7 working units.
- BLEND meshes have zero boundary/nonmanifold edges, degenerate faces or negative signed volumes. Imported GLB meshes have the same result after a diagnostic in-memory 1e-6 vertex weld to account for attribute splits. Input files were not changed.
- Only CENTRE_hourglass_stool geometry changed from R07. R07 had only changed WALL_rear_sill from R06.
- 58 representative shell rays give 54 expected solid hits and 4 expected openings through the real window aperture. The unintended right sill gap discovered in R06 no longer occurs at the tested point. This is not an exhaustive airtightness/contact/intersection proof.
- No mesh hide_render or hide_viewport flags are set.

## Source fitting remains failed
- Actual Blender projection of 14 remaining manually specified training landmarks gives A mean/max 25.259/43.515 px, B 16.548/33.720 px, C 28.006/74.531 px.
- Stool base and rim hypotheses were explicitly shifted to Z=0 and Z=.903 after the R08 grounding change; no camera refit.
- Three old bar landmarks became invalid after the R06 topology change. They remain excluded and are not silently replaced.
- These are manually estimated training correspondences on hypothetical geometry, not independent calibration or global image quality. The stated ±10 px input estimate is not a measured confidence interval. D/E/F remain uncalibrated.

## Final render and overlay review
PASS (artifact presence/formula only): independently decoded and hashed all 28 final PNGs: material/white each SOURCE_A/B/C/D_low/E_oblique at 1920×1080, SOURCE_F_fan4k at 3840×2160, CHECK_01–08 at 1280×720. All nonblank. Each of the 28 renders was actually viewed, not merely counted. Each of the 12 direct50 PNGs was actually viewed. Independent full RGB array checks of floor((source + render)/2), with uint16 addition and no resizing, have maximum pixel error 0 for all 12. All source/render/output hashes match their metadata. See R08-final-image-integrity-independent.json and check_r08_final_images.py. Formula correctness does NOT imply source alignment.

PASS (diagnostic coverage only): material and white independently show eight distinct useful inspection views. CHECK_01/02 opposite frontal obliques show room/furniture and window; CHECK_03 left-side view shows bed, curtain and bar depth; CHECK_04 reverse side shows bar thickness/stools and bed side; CHECK_05/06 rear-facing views show furniture backs and the inferred front enclosure; CHECK_07/08 high opposite views show floor layout and furniture spacing. These are eight model diagnostic cameras, NOT eight source observations, and NOT geometry acceptance. Rear-facing images intentionally include largely bare inferred enclosure. No blank, inside-solid, or fully blocked image was counted as effective.

The inspected render_views.py opens one frozen model, changes only camera/render settings per view, and does not hide geometry or change object transforms. This agrees with the independent zero-hidden-mesh result and identical material/white world-space geometry/camera hashes. Glass remains optically reflective; white materials do not imply a flat unlit segmentation pass.

R08 stool: actual renders show a continuous waist/flare rather than the earlier coarse piecewise profile. The technical check confirms only CENTRE_hourglass_stool changed from R07 and grounding was explicit. This is a visible quality correction, not proof its dimensions match the source.

## Actual source comparison: FAILED / not accepted
- A: stool base is lower than source, window mullion/curtain contours and bed headboard rhythm visibly differ.
- B: stool/rim is comparatively close, but window/frame, curtain ties and nested bed arches remain discrepant; bar thickness/position also differ.
- C: window/frame slant and bed/bar arrangement retain visible double edges. Performer occlusion and possible scene-state differences make the central stool comparison ambiguous; no per-view disappearance was introduced to hide it.
- D: uncalibrated low camera, conspicuous stool/vertical-mullion and bar differences.
- E: uncalibrated oblique camera, substantial source/render lateral position and perspective differences.
- F: actual 3840×2160 comparison has major stool/mullion/bar perspective displacement. Native decoded 4K pixels are not proof of upstream 4K rendering.
- City skyline is a rough proxy rather than the observed building silhouettes/lights. Cloth/bedding/headboard detail and lighting still differ. These limitations apply to both material and white comparisons.

Fixed-light round reflections remain visible in glass (notably CHECK_02/04 and SOURCE_D), and renders have visible sampling noise. They reduce visual polish but do not invalidate the diagnostic existence of those views. No request to endlessly rerender or alter the frozen candidate is implied.

## Dependency evidence review and scope limits
Reviewed producer R08-external-dependencies.json plus corresponding Blender 4.3.2 log for the exact matching blend hashes: only Render Result VIEWER image, no image file paths, no linked libraries, no fonts. This is reviewed producer evidence, not a separate independent Blender dependency rerun. Both GLBs were independently imported successfully as recorded above.

NOT RUN / not established: exhaustive collision/intersection/contact or whole-room airtightness validation; measured physical scale; calibrated multiview reconstruction; held-out landmark validation; proof of hidden structure or precise skyline; exhaustive repository-wide pixel novelty comparison; remote Git roundtrip/hash/Space cleanup (archival owner responsibility). 58 shell rays do not certify an airtight room. Depth estimates are not physical geometry acceptance. Later independent-event same-scene validation is outside this model/image check and must be evaluated from source evidence separately.

Prior R01–R07 failures and experiments remain valid history, not overwritten by this report. Overall outcome: technically inspectable new-scene candidate, source reconstruction fidelity FAILED / unaccepted. Do not merge or label accepted based on topology, export integrity, overlay arithmetic, or eight rendered cameras alone.
