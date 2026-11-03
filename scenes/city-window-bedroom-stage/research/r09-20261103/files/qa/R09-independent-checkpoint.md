# R09 camera-only independent checkpoint

Baseline SHA256: edb6d27130bc42f8f2a9ecb4e2149439ff07459a1a4d7b91a88270e058d2f4e5

Trial SHA256: f85d0130a917180c2b9db291cbaf3111ad5bfaab32dbf7e8631daee8d1678359

Fit JSON SHA256: 03f3a4c03d22b4fffafbd474372f223f20f375494fb0be6df5565264431d761d

Independent Blender 4.3.2 read: all world mesh coordinates/topology hashes exactly unchanged; only SOURCE_D_low/E_oblique/F_fan4k camera definitions differ. A/B/C and CHECK cameras unchanged. No hidden mesh flags. All 1542 tested ring/line samples per fitted camera are in front (minimum depths 5.1445, 4.0587, 5.5362 working units). Blender projection versus unclamped analytic pinhole differs by less than 0.00016 px. See R09-independent-check.json.

Reviewed complete 51 first annotations (D20/E13/F18), including actual annotated native images. The script preserves all original entries and uses the same training constraints before/after. It fits 10/6/9 scalar residuals with six pose parameters and fixed focal length. E is saturated and its near-zero residual is not independent calibration. Local rank/condition uses chosen parameter scaling and subjective pixel uncertainties. Non-fitted diagnostics have already been seen and cannot be called blind validation.

- SOURCE_D_low: same-set reported mean 105.072 → 1.617px; max after 4.820px.
- SOURCE_E_oblique: same-set reported mean 153.731 → 0.000px; max after 0.000px.
- SOURCE_F_fan4k: same-set reported mean 327.689 → 6.491px; max after 22.434px.

The line residual is point-to-infinite-projected-line, not a fabricated world-height match. E/F line midpoint training discards width as a fitting constraint but original left/right edge residuals are preserved explicitly, showing remaining width mismatch. Circle residual is nearest projected polyline of named hypothesized rings, not exact entire visible object silhouette. Top rim r=.315 z=.903 differs from wider outer profile ring r=.322 z=.882; source silhouette identification can bias fit. Waist is also a ring approximation, not a rigorous silhouette validation.

F09 right base annotation is ambiguous at the contact-line/shadow intersection. Native unscaled crop F-base-native-crop.png uses box [1950,1870,2400,2090]. Initial overview suggested shadow; native crop does not establish it is definitely erroneous. Source worker recheck requested. Preserve original and its result before any documented correction. F base residuals remain 16.03/15.45/22.43 px; F04 worsens .89 → 1.33 px. Do not summarize every point as improved.

Actual D direct50 viewed: stool/vertical line alignment visibly improves, but curtain, bar/stools, lower sill and skyline remain obviously mismatched. Overall source fidelity remains FAILED. Remaining E/F pixel comparison and any new-annotation revision pending. No production files changed by reviewer.
