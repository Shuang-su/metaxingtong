# First source landmark diagnosis

All coordinates use original PNG pixels, not the image viewer thumbnail. D/E: 1920×1080; F: 3840×2160. All sources already used for fitting. These annotations are not independent/held-out validation.

## Fitting guidance
- Prefer visible rim contour, silhouette and mullion line constraints. Sampled line pixels have no asserted world height.
- Ellipse image centers are estimates, not exact projections of 3D disk centers. Partial base centers are especially weak. Do not use them as hard landmarks.
- Bar tangencies are broad curve regions, not exact corners or persistent material points.
- Occlusion from hands/boots, dark saturation, blooming and possible source lens effects are error hypotheses. Numeric radii are subjective uncertainty, not calibrated confidence.
- D shows only the right mullion/sill junction, not center. E base is outside frame. F mullion bottom is bar-occluded and tie is too dark. No points supplied for these unavailable features.

## Full initial point list (no selection by fit residual)

### D
- D01 seat_left: [875, 750], ±9 px, partial_contour. Hand overlaps outer rim; visible endpoint is uncertain.
- D02 seat_right: [1012, 751], ±9 px, partial_contour. Hand overlaps endpoint.
- D03 seat_rear: [942, 744], ±5 px, contour. Visible back rim near screen middle.
- D04 seat_front: [942, 763], ±4 px, contour. Visible front rim.
- D05 seat_ellipse_center: [943, 753], ±10 px, inferred_2d. Ellipse image-center estimate, NOT guaranteed projected 3D circle center.
- D06 waist_left: [916, 880], ±4 px, contour. Apparent silhouette minimum; not fixed material point.
- D07 waist_right: [954, 880], ±4 px, contour. Apparent silhouette minimum.
- D08 base_left: [847, 1009], ±8 px, partial_contour. Left rim partly merged with dark shoe/shadow.
- D09 base_right: [1019, 1009], ±8 px, partial_contour. Right rear shape contaminated by shoe/shadow.
- D10 base_front: [934, 1024], ±4 px, contour. Bright lower front rim; apparent extremum.
- D11 base_center_estimate: [934, 1008], ±17 px, inferred_2d. Approximate projected ellipse center; rear rim not fully visible.
- D12 mullion_right_a: [1005, 100], ±3 px, line_only. Same visible straight edge; no assigned 3D height.
- D13 mullion_right_b: [1005, 360], ±3 px, line_only. Same visible straight edge.
- D14 mullion_right_c: [1005, 821], ±4 px, line_only. Visible above sill, partly actor-occluded elsewhere.
- D15 mullion_sill_right: [1005, 839], ±6 px, junction_partial. Visible RIGHT edge at sill, not center of mullion and not wall-floor contact.
- D16 left_tie_center: [83, 381], ±23 px, inferred_2d. Dark band broad; only low-weight appearance region.
- D17 wood_seat_center: [1773, 740], ±22 px, inferred_2d. Dark wood seat apparent ellipse center; weak outline.
- D18 bar_outer_horizontal_tangent: [1420, 595], ±28 px, curve_region. Rounded transition has no unique physical vertex.
- D19 bar_outer_vertical_tangent: [1360, 658], ±25 px, curve_region. Contour tangent region, not homologous 3D point.
- D20 bar_inner_horizontal_tangent: [1603, 613], ±27 px, curve_region. Dark inner curve transition, weak.

### E
- E01 seat_left: [970, 829], ±8 px, contour. Leftmost apparent rim; boot near but endpoint visible.
- E02 seat_right: [1197, 833], ±7 px, contour. Rightmost apparent rim.
- E03 seat_rear: [1082, 815], ±5 px, contour. Back rim center region.
- E04 seat_front: [1082, 855], ±6 px, contour. Front rim dark but discernible.
- E05 seat_ellipse_center: [1083, 835], ±10 px, inferred_2d. 2D ellipse center only; projection does not preserve circle center.
- E06 waist_left: [1053, 997], ±7 px, contour. Silhouette minimum in dark region.
- E07 waist_right: [1096, 997], ±8 px, contour. Silhouette minimum in dark region.
- E08 mullion_left_a: [1400, 150], ±4 px, line_only. No 3D height correspondence.
- E09 mullion_left_b: [1400, 700], ±4 px, line_only. No 3D height correspondence.
- E10 mullion_right_a: [1458, 150], ±4 px, line_only. No 3D height correspondence.
- E11 mullion_right_b: [1458, 700], ±4 px, line_only. No 3D height correspondence.
- E12 mullion_sill_left: [1400, 938], ±9 px, junction_partial. Sill junction visible but very dark.
- E13 mullion_sill_right: [1458, 944], ±9 px, junction_partial. Sill junction, not floor.

### F
- F01 seat_left: [1963, 1500], ±14 px, partial_contour. Hand over left end; native coordinates.
- F02 seat_right: [2328, 1508], ±12 px, partial_contour. Right endpoint visible beyond hand.
- F03 seat_rear: [2150, 1481], ±9 px, contour. Back rim.
- F04 seat_front: [2150, 1521], ±10 px, contour. Front rim partly hand-occluded to right.
- F05 seat_ellipse_center: [2147, 1502], ±20 px, inferred_2d. Image ellipse center only, not physical center correspondence.
- F06 waist_left: [2121, 1770], ±7 px, contour. Apparent silhouette minimum.
- F07 waist_right: [2196, 1770], ±7 px, contour. Apparent silhouette minimum.
- F08 base_left: [2027, 1978], ±10 px, contour. Visible left end of base.
- F09 base_right: [2334, 2024], ±22 px, partial_contour. Dark rim merges shadow to right.
- F10 base_front: [2180, 2010], ±11 px, contour. Lower front rim on slanted apparent ellipse, not global y-extremum.
- F11 base_center_estimate: [2180, 1989], ±30 px, inferred_2d. Rear base obscured; rough center only, not strong camera fitting point.
- F12 mullion_left_a: [3020, 350], ±5 px, line_only. Visible edge; no fixed 3D height.
- F13 mullion_left_b: [3020, 1100], ±5 px, line_only. Visible edge.
- F14 mullion_right_a: [3112, 350], ±5 px, line_only. Visible edge.
- F15 mullion_right_b: [3112, 1100], ±5 px, line_only. Visible edge.
- F16 wood_seat_center: [3404, 1655], ±28 px, inferred_2d. Dark wood seat apparent center; no clean rear boundary.
- F17 bar_outer_horizontal_tangent: [3075, 1266], ±45 px, curve_region. Blurred rounded transition; no unique 3D corner.
- F18 bar_outer_vertical_tangent: [2887, 1400], ±35 px, curve_region. Outer contour transition region.
