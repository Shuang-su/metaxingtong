# C25 read-only whole-chair structural review

## Decision

A visibly different whole-backrest construction is justified. Replace the inherited flat, rounded slab with a shallow shaped back-panel volume, a broad convex left return/side volume, a visibly narrower descending post, and one coordinated transition between them. Do not attempt another small fold of the old left rim.

This is a recommendation for the next model experiment, not a newly fitted or accepted model. No geometry, camera, material, source pixel, tolerance, or branch definition was changed in this review.

## What the actual pixels support

All inspected originals are 1920×1080. The saved review crops preserve their native pixels without enlargement or resampling.

- H1101 and new 1103 show the complete visible back-panel width. At the left end there is a bright, turned upper lip, a broad vertically convex green surface, and a narrower green stem continuing below it. The region occupies a significant area of the backrest, not just a one-pixel contour or a cylindrical post.
- 650 and 658 repeat this side surface independently of the person's arm. 658 is especially clear for its outside contour, turned top, broad body, and narrow continuation. The arm conceals the central panel and some of the inner junction.
- 872 repeats the feature but remains heavily occluded. It adds semantic continuity of the design, not a measurable uninterrupted chair pose.
- N665 provides useful exposed post sides and small panel-rim fragments. The forearm hides the decisive band-to-post transition. It must not certify that hidden junction or the warm diagonal surface as a chair seat.
- G provides a cropped right shoulder and upper edge. It cannot distinguish left-side topology.
- N642 was inspected in this review, as it already was in C24. It is development evidence, not a fresh holdout. It shows the same design family, but the left return runs out of frame.

The strongest tangible mismatch is not the central panel's exact cupping depth. It is the missing broad convex left surface and the wrong panel-to-side-to-post hierarchy. Central cupping remains a hypothesis that should be kept low-dimensional and tested rather than asserted from shading.

## Boundary ownership ledger

1. Upper and lower panel silhouettes against the city/background are geometric visible boundaries where exposed. H is the principal existing view for them.
2. The far-left chair/background boundary is a composite silhouette. Its upper portion can belong to the return/side surface and its lower portion to the post. One label for the whole sampled branch does not make it a single manufactured part.
3. The bright upper lip supports a change of surface orientation. The light stripe itself is not a second contour or a recovered material seam.
4. The internal band-to-main-panel transition is a persistent surface change. Pixels do not settle whether this is the silhouette of an overlapping side frame, the trough of a continuous return shell, or a smoothly blended molded region. Keep that ownership ambiguous.
5. Exposed post/background sides are silhouette evidence. The left post's short H segment and longer N665 segment constrain visible shape under a common-pose assumption. Their endpoints are occlusion cuts, not measured mount locations.
6. No source here establishes the back face, hidden fasteners, exact shell thickness, seat perimeter, feet, or ground contact.

The existing branch file explicitly excludes the bright inner stripe from geometry. Preserve that rule. A broad side surface can be evaluated visually without silently converting its shading boundary into hard 3 px seam annotations.

## Why the inherited slab is restrictive

This was checked against the actual C23 scene snapshot and the recovered C21 locked construction:

- Object: `Chair • narrow curved wraparound back`.
- 12,960 vertices; 12,240 quad side faces plus two 720-vertex cap faces.
- The C23 vertex array matches the recovered C21 array within 5.961e-8 scene units, and its complete face list is identical.
- Along the recovered fixed normal [0.3855205877, 0.6304425900, -0.6737328976], the actual C23 vertex span is 0.010000153 scene units. The saved construction thickness is 0.01 and edge-round radius is 0.0025.
- Each large cap is planar to float precision: normal-coordinate ranges about 1.47e-7 and 1.51e-7 scene units. This is a thin planar body with a rounded perimeter, regardless of its object name.
- The construction uses 24 scalar 2D silhouette controls and seven explicitly non-source samples labelled `unobserved_left_closure`. These join the observed upper/lower regions by a smooth left closure. They are a construction prior, not measured chair geometry.

Consequently, the flat cap consumes the area where the source shows a broad side volume. Keeping that cap, its closure, and the independent support endpoint frozen makes a return patch compete with the old slab. C24 confirms the practical failure: edge scores can improve without a recognizable broad band, while stronger local protrusion produces the unsupported lower-left lobe. C23's good visible-post score is useful evidence, but its hidden connector is not an immutable truth.

## Concrete low-DOF C25 construction

Use one chair-local coordinate frame and a small surface grid through the backrest interior, rather than two huge flat n-gon caps. Parameterize the front/back surfaces and their rounded edge together. The old silhouette is an initialization/prior only; the synthetic left closure must not remain a fixed target.

A compact initial family can use nine structural scalars:

1. Main panel transverse camber c: one shallow bend across the broad face. Zero remains a permissible hypothesis.
2. Panel thickness t: one positive separation, initially a construction prior, not a measured thickness.
3. Left-band width b: controls how much of the whole backrest transitions into the side volume.
4. Left-band return depth d: produces a real convex cross-section and turned upper lip, rather than a normal-map stripe.
5. Band lower taper q: one monotone profile from its wider upper/middle body into the narrow lower region. No extra lower lobe or local S-bend.
6. Shared slender-post section scale w: define the posts as narrow relative to the band. Do not blindly make the already-fitted C23 exposed post narrower; its original silhouette evidence remains a constraint.
7. Left-post setback s relative to the band, not a free cloud of independently fitted 3D points.
8. Transition length l from side volume to left post: derive its position/tangent from the band and post, rather than retain a fixed hidden elbow.
9. Right upper-post inset j relative to the panel underside/shoulder: addresses the unresolved H right inner junction without allowing an independently deformed right-backrest patch.

Keep the overall chair pose and camera variables outside these nine shape controls. Do not let camera or chair movement be absorbed into c, d, or s. Existing source-supported outer rim and post constraints should be retained with their current tolerances and visibility checks; an actual failure must remain a failure.

As a native-image sanity check only, H's broad left surface is of order 45–60 px across in its wide region, while the exposed lower left stem is around 30 px wide. These are approximate visual extents with ambiguous inner ownership, not new annotated targets or a 3D width ratio. The point is a clearly visible broad-to-narrow hierarchy.

Two construction interpretations remain defensible:

- Continuous shaped return: panel turns into the broad left shell and tapers into a blended post transition.
- Overlapping shaped side member: a broad convex side frame overlaps a shallow panel and narrows toward the post.

Use the same gross volume controls and the same evaluation views for both. Their hidden connectivity cannot be selected as ground truth from the current frames. At most two coarse hypotheses are warranted before further local detail; neither should inherit the old flat left cap underneath as unexplained duplicate geometry.

## What would count as a tangible improvement

The first H native render should show, without an explanatory overlay:

- a clearly readable broad convex left band occupying a meaningful part of the backrest;
- a turned top lip that belongs to that volume;
- a smooth broad-to-narrow continuation into the post, without an extra lower-left bulb;
- a panel that reads as one coherent shaped body rather than a rounded rectangular sign attached to posts;
- a right post that joins the underside naturally, with the original first inner sample still reported if it remains out of band.

Then verify the same complete model in G and N665. New 650/658/1103 frames are valuable semantic checks now; they become pixel-fitting/validation views only after independently checked cameras and chair-to-room pose. A white geometry render can expose volume changes, while the material render confirms that the improvement survives the existing lighting. Neither should be treated as photometric reconstruction because lighting/materials are not calibrated.

Keep numeric and visual acceptance separate. Better silhouette counts alone are insufficient; a nice broad band with regressed silhouettes, invisible branch ownership, self-intersection, or new collisions also fails. Existing 3 px tolerances must not expand. No per-view hiding, warping, rescaling, image-based compensation, or altered source pixels.

## Limitations and stopping condition

H/G/N665 are existing development views, not fresh independent validation. 650/658/1103 have uncalibrated new cameras. Cross-time common rigid chair pose over roughly 436 seconds remains conditional. 872 does not resolve that gap. No claimed real-world metric dimensions or uniquely recovered hidden topology are justified.

A coarse C25 family should stop for review if it still cannot deliver the visible broad-band/narrow-post hierarchy without a lower-lobe or silhouette regression. Do not continue adding local folds to force the old closure. Revisit the camera/pose or structural family explicitly.

## Review files

The files `H_source_native_crop.png`, `H_C23_native_crop.png`, `1103_native_crop.png`, `658_native_crop.png`, `650_native_crop.png`, and `872_native_crop.png` are exact native crops. Their sources, crop boxes and SHA-256 values are recorded in `review_manifest.json`.
