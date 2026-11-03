# R01 independent QA — not accepted

Scope: original production HEAD e773229b81c4f40293c5fb17196aa158d8b9ba8d; material BLEND SHA256 d7720baf20f1bba9ebd47a103cc117e3f919fc60012e5a16bdad3048fd865bef. Exact four input hashes and object-level results are in R01-independent-model-check.json. No production files were modified.

## Passed limited technical checks
- Material and white BLEND have identical 560 mesh names, exact world vertex/face-index hashes, and camera definitions.
- Both GLBs were actually imported into Blender 4.3.2. No missing or extra mesh objects; bidirectional nearest world-vertex discrepancy at most 4.915124804938387e-7 model units.
- No mesh object has hide_render or hide_viewport enabled.
- render_views.py switches camera and render size only, without per-camera geometry changes.

## Failed / incomplete
- Producer mesh audit independently reviewed: 320 boundary/nonmanifold edges on 10 bed arch tubes, one degenerate WINDOW_glazing polygon, 129 negative signed-volume meshes. Producer is fixing these in R02; R01 must remain a failed historical stage.
- Independent GLB import has four degenerate WINDOW_glazing triangles. Raw import has many attribute-split edges, which must NOT be interpreted as geometric holes without a welded diagnostic.
- Visually inspected SOURCE_A, SOURCE_B, CHECK_01 and CHECK_07 previews. Source window occupies materially more of the frame than the render. Native source A clips the upper arch while the R01 render contains it fully; central mullion has a different horizontal relation to the stool. Camera/scale fitting is not accepted.
- Large circular area-light reflection in the rendered glazing is absent from the source. Altering actual light/material parameters may be warranted, but hiding glass per view would not be an acceptable fix.
- Preview images are 960×540, while native sources are 1920×1080. No direct equal-size source overlay was available at this review. No upsampled preview was treated as a native overlay.
- Only two inspection-camera images were available; the eight-view requirement is not yet checked.
- Finite room shell is present and unseen sides/ceiling are explicitly tagged as inferred. Full inter-object intersection and physical contact verification has not run.

This review does not establish source reconstruction accuracy, lighting equivalence, absolute scale, unseen architecture, or later-replay verification.
