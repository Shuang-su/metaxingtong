# C30 / C30B: real bed-deck trials, both rejected

## Useful result
The original scene omitted much of the foreground bed covering visible in G, N642, H and665. Real mesh changes and actual four-view region renders confirmed that a deck-height change affects this omission. It also exposed a conflict with the existing central endboard recess, so neither trial replaces C29.

## Evidence and exact scope
Native1920x1080 sources identify a bed covering/sheet contour with high confidence. Mapping that contour to the current bare-mattress maximum-y edge has only medium confidence. The user states that the camera is lying in the bed. Every recorded camera position remains horizontally inside the model mattress rectangle, above the trial surface; near-plane condition checks find no intersection with the tested flat top.

G/N642 source points were used for one-height projection diagnosis. H/665 were frozen before candidate image review and excluded from fitting, but are previously seen views, not blind tests. C30B was tested after their C30 outcomes had been seen; it was selected to avoid G recess cutoff, not fit to H/665.

Both actual white/material models translate mattress, tray, side rails and inferred low bumper equally, preserving mattress thickness and assembly offsets. Four upper supports extend to retain tray connection; lower support bases, crossmembers, wheels, visible endboard/recess, chairs, other geometry and cameras stay fixed. Those hidden support shapes are explicit completion assumptions, not measured construction.

## Rejected C30 +0.1354234 scene units
The actual material silhouette residuals (model y minus source y, approximate ±2px render reading) are G[-5,-4,-3],N642[27,22,20],H[-7,-7,-5],665[18,15,12]. Source uncertainties are around±4px forG/N/H and±3px for665. Thus G/H can look close while N/665 still have insufficient coverage.

The visible left handle opening remains intact. However G's central recess/inset lower part is newly obscured by the bed surface, whereas the source retains endboard material beneath it. Reject this variant despite large improvement in a projection proxy.

## Rejected C30B +0.08 scene units
The smaller rise avoids that new direct recess cutoff but leaves the bed covering far too low. Actual readable offsets: G57px; N642112/93px;665158/139px. Remaining frozen sample positions, including all three H points, have no visible mattress edge in frame. Do not treat weak floor gradients as bedding edges or invent coordinates beyond the image.

## Metric correction
four_view_edge_metrics.json computes the analytic line combining AABB z_max and y_max. The rounded mattress may have no real vertex or surface on this line. Its large before/after RMSE reduction is a conditional geometric proxy, not actual image-silhouette accuracy. In665 the proxy and actual C30 contour even have opposite residual signs. Independent actual-render observations and contextual edge rejection are kept in c30_review and c30b_review. N642x1750's strongest gradient was a window/floor line; the true C30 bed edge is y922, not911.

## Remaining evidence needed
Independently inspect the endboard recess's normalized location and shape from unobstructed images; do not move it merely to hide this trial's regression. A side-oriented view showing the bed covering thickness/overhang, side-rail relationship, and endboard lower edge would distinguish surface identity and connections. Current views do not determine support dimensions or physical scale. No extra camera fitting or blind depth estimation resolves this by itself.

## Delivery
All four original trial blends, native annotations, source hashes, scripts, actual region renders, metrics and rejection records are in true Git history and the diagnostic recovery bundle. No model images are generated or retouched. No full-scene render was started for a rejected variant. C29 retains its delivered full white/material/direct50 images. No authenticated remote push has been performed.
