# Terrace T2: two visible pots and rosettes, independent candidate

Basis: October 11 right-rear-table candidate, SHA256 1b927ed757db761d7a81b1a95a0bd63359fd11315c70ac15a27aa981342956d6. Source: BV1g64y1P7VV, native frame at player currentTime 5586.011739, 1920×1080, SHA256 ca728b6e9c87fb01e222e1ac94d342c583a9413efc5be3a5deff2c1eb28d52b0.

Only 26 previously approximated table-decoration objects were replaced: white cup, small planter, 12 leaves and 12 stems. New candidate has two tapered pots, a low purple rosette and a low green rosette. Left pot has an explicitly approximate white deer-like surface marking. The marking and species/product identification are not claimed exact. All back surfaces, leaf layering/count and depth remain inferred from the front-family evidence.

Tray, ribs, white inner object, all unrelated geometry, cameras, lighting and existing materials are unchanged. No ground shadow was made into geometry. The known tray-rim, white inner-object underside and table-bottom projection residuals remain. This candidate does not claim those issues fixed.

Actual mesh-world vertices were inspected before editing: historical objects contain mesh-space offsets, so object.location alone does not represent actual geometry placement. freeze_audit.json records the non-decoration object hashes.

5586 and 6821 are the same front camera family. 5612/5638/6028 and the autumn low views do not show this table completely. No independent second furniture viewpoint is established. Consequently this is a conservative visible-front candidate, not a multi-angle geometry acceptance.

Render camera stays SOURCE_5586__01h33m06s with its historical matrix/lens. Source matching was not recalibrated. Native-size render diagnostics use 1920×1080, 32 fixed Cycles samples and seed 0, no denoising. White render is an explicitly labeled render-only material override with the same camera and lights; saved candidate retains its actual materials. Direct 50% overlays are RGB arithmetic only, with no alignment, image warp or masking. Crops use [1430,580,1650,845), original 220×265 pixels.

Local Git only; no remote push and no CURRENT replacement. Baseline binaries and source are retained in baseline/. Generated inspection logs, scripts and QA are preserved. Image generation is not used.

## T3 leaf-tip refinement

T2 remains separately preserved as Terrace_T2_TwoPots_Candidate.blend (Library version 0). Independent visual review found the rosettes too flat/stacked. T3 raises only leaf tips using a quadratic radial displacement and small per-leaf variation; pots, motif and all other objects remain fixed. T3 is Terrace_T3_RosetteTips_Candidate.blend. T3 preview is a real 32-sample 220×265 crop. Final native-size T3 material/white diagnostics use 8 samples, explicitly noisy raw images, not high-quality appearance acceptance. An earlier T2 full-frame 32-sample attempt was interrupted after review and is not delivered as a finished render. Its log is retained. The original T2 file was restored and never replaced in Library.
