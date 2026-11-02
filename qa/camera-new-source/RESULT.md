# One new-source conditional camera-only diagnostic: FAIL

R03 original mesh/cameras unchanged. Used genuinely new Nov2 high-bitrate native2490.361500/2560.507406. Manually identified source display-content edges (not red outer frame), with independent5–10px annotation uncertainty. Actual Blender mesh front straight edges extracted; interior source line points fitted to finite projected mesh segments, never pretended to be rounded 3D corners. No source warping.

Three bounded focal initializations36/55/80mm converged to substantially same poor conditional solution in each view. Selection used training only. Principal point(960,540) and current working geometry were assumptions. Computation bounds Cx±6/Cy[-25,-2]/Cz[.3,8]/f[16,100] are NOT measured room boundaries or proof that other cameras cannot exist. Unknown front wall was not imposed.

## Actual results
Front: fitted display-line distances0.6–3.7px, trained left lower-panel line still10.2–13.9px. Held opposite portion of that same lower edge78.6–122.6px (not independent physical geometry), held gold-plinth bottom52.2–81.7px. Thus good screen-only training is not adequate. Cx hits−6 working bound; final f50.49mm, C≈(−6,−7.83,2.76). Held normalized residual worsens3.12→7.83; reject.

Oblique: two lower screen edges0.3–4.3px, but inner vertical display sides remain30.2–59.4px despiteσ6. Held lower-red-panel bottom edges79.4–102.1px, despiteσ10. Train residual improves from poor initial camera, but still not within annotations. Cx−6 and Cz.3 hit working bounds; f78.37mm,Cy−20.23. Jacobian weakest singular value~.00094 vs largest~1059; focal/pose underconstraint remains severe. Do not turn this into accepted intrinsics or broaden bounds until a target fits by chance.

Known cabinet/back/right-wall center tests are reported; no complete ray-occlusion proof. All camera y<−2 avoids cabinet volumes, but this alone is not source agreement. 2570.580591 reverse view was not trained/selected on and has no fitted camera; it cannot be claimed passed holdout. Pad rim/rings were not trained; exact usable noncoplanar pad/rim correspondence remains missing. No new model or expensive render produced for this failed fit.

## Concrete remaining ambiguities
- Display-content plane vs lower-face/plinth are stepped; their current relative depths/heights are inferred. Although actual mesh edges were used, this does not certify the source layer corresponds exactly to that working edge.
- Front native source central display straight sides x≈721/1228 give~507px width; outer red frame roughlyx650–1295 gives~645px (manual, perspective affected). Approximate ratio~.79 differs from model2.32/2.72≈.85. This suggests a shared display-to-frame proportion error, not just camera translation, but is not a measured metric dimension or a license for per-view scaling.
- Adjacent repeated cabinet slot identity is conditional on ordered three-cabinet assembly; noncoplanar rear/side plinth junction remains ambiguous because bevel/shadow/occlusion.
- Next justified geometry test would need actual same-layer straight-boundary annotations across front/oblique, with a small shared screen/frame proportion parameter and separate pad/low-panel holdout. Do not run repeated unbounded camera-only loops or silently alter models from this failed result.

Projection implementation cross-check: eight actual Blender world_to_camera_view projections vs this NumPy convention, maximum difference 0.00008562px. This checks arithmetic, NOT source correspondence, camera identifiability or geometry acceptance.
