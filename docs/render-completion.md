# Actual 32-sample rendering completion
20 actual full-frame PNGs completed: 2 source cameras +8 meaningful check directions in each material and white mode. Each1192×671, Cycles32 samples, denoising false. Render logs and validated manifests record exact model SHA, camera, elapsed seconds and output byte SHA. No missing or pending frame counted complete.

Four direct50 PNG overlays were generated and decoded back: source03/04 × material/white. Each uses all2,399,496 RGB channel values at1192×671, floor average of source and render bytes, with zero difference in complete-array verification. No crop, warp, local alignment, mask or color manipulation. This proves arithmetic, not alignment.

Material and white sheets were actually visually reviewed: CHECK00/01 opposing front diagonals,02/03 opposing back diagonals,04 rear,05 elevated front,06 top,07 right side. All show meaningful geometry, none is a black placeholder. Some views intentionally crop foreground/side extremities while exposing arch backs, wall depth, pavilion posts, or umbrella/chair arrangement. They are internal model diagnostics, not new source views. Model backs and support/depth remain inferred.

The source03 material/white and source04 material images were actually viewed at original size; source04 overlay shows remaining arch/profile/prop/lighting deviations rather than hiding them. Main proposed preview is renders/material-SOURCE03.png. Delivery does not imply acceptance.

Support limitation, carefully bounded: each arch endpoint has lowest z=.38, while the rear apron top is z0, so the endpoint-to-that-apron vertical separation is .38 model units. The model has not established/verified a complete arch support chain. This scalar fact does not prove the entire arch has no connection elsewhere to a wall or another object; no global floating/disconnected claim is made without that check. Source support construction also remains unknown. No invented footings added to disguise this limitation.
