# Independent left-arm pixel/identity audit

## Stage clarification

This is the initial source-identity audit made before the E geometry experiment. Its instruction to freeze the sofa and cameras was the guardrail for that local experiment only. E subsequently failed the multi-view and physical-contact checks and was rejected. The next step is now the shared camera/sofa-space review described in 沙发左扶手条件候选E_拒绝.md, not further isolated arm fitting.

Inspected native F1823.678156, G1116.180816, and H1101.728114 pixels, enlarged unaltered crops, D full 1920 renders, original annotations, and frozen D projection metadata. No source, D, scene, or Git edits. Crops/grids in this directory are inspection notes only.

## Finding

G and H show the same left sofa arm with high visual confidence: an upholstered top and broad front/side, the same large bright polygon and tiny bright patch near its rounded tip, and the same adjacent back cushion. The light polygons establish appearance identity; their edges are not shape constraints.

The old H line mixes the arm/back internal occlusion boundary, points inside sunlit patches, and the true front-end contour. It must not be scored against the complete projected arm convex hull. G front line is especially contaminated by illumination.

## Existing H sample classification

- [873,920]: near chair occlusion endpoint and arm/back contact. Approximate internal visible boundary, not whole-object outer silhouette. ±4–6 px.
- [912,931]: within a few pixels of arm/back boundary but slightly inside arm top. Downweight/correct, not a full-hull constraint.
- [960,938]: inside large sunlit patch. Exclude from geometry-edge constraints.
- [1045,954]: near arm/back boundary but inside shaded top by a few pixels. Downweight/correct; internal occlusion edge only.
- [1073,960]: on small sunlit patch. Exclude from geometry-edge constraints.
- [1088,977], [1092,1010], [1093,1079]: useful actual rightmost front-cap contour against back/seat. Retain as soft visible contour with ±4–6 px uncertainty. Last point is frame clipping, not physical bottom.

The top of the arm is visible against the sofa back. Even when this boundary is geometrically real, the back occludes other portions of the arm's projected mesh. A complete mesh hull includes hidden edges and is not the corresponding curve.

## G classification

- [145,1014], [184,1020]: close to the short physical rear/top skyline between chair and cushion; soft and blurry, ±5 px. [193,1030] instead lies in a cast-shadow region and should be excluded.
- [218,1042], [255,1039], [303,1044], [366,1057]: largely follow or lie within the large bright patch, not the arm/back top contour. Exclude as silhouette constraints.
- [420,1058]: small bright patch near tip. Exclude as silhouette constraint.
- [432,1068], [435,1079]: short front-cap contour, soft and bottom-clipped; retain only with ±6–8 px uncertainty, without extrapolating beyond the frame.

## Optional corrected source samples

These are independently sampled soft curves, never array-index correspondences or rigid vertices. See the JSON note for machine-readable values. Only H front-cap segment is a strong new fitting constraint. The arm/back curve is diagnostic and should use visibility-aware rendering or an explicitly tagged component edge, not an entire projected convex hull.

## Fixed-D geometric implication

The D left arm has full projected x span approximately 626–836 in H and −80–94 in G; the native front-cap contour is around H x1090 and G x432–435. D's left back cushion remains near the observed back location, while its arm appears as a lobe behind the green chair (H) or near the far-left crop edge (G). This is a substantial arm-local placement/forward-extent problem relative to the frozen cushion/seat, not merely a few-pixel tracing error or sunlight mismatch.

A useful candidate must bring the visible left arm/front cap rightward in both views and lower its visible top relative to the already close back cushion. Local position, width/depth/forward extension, and height may trade off under the frozen cameras; these images do not uniquely identify a hidden rear shape or a unique 3D correction. Preserve the source F no-sofa region as an exclusion guardrail. Do not move the whole sofa/cameras to absorb this local mismatch.
