# Final bounded repair: source / C23 / v1 / v2 / v2b

Final status: numerical geometry checks pass; source acceptance fails.

## Final verification

- Panel and left frame/post are each one closed, consistently oriented manifold component with positive signed volume, no degenerate triangles, and no detected nonadjacent BVH self-intersections. The unchanged right post was also independently checked and has no detected nonadjacent self-intersections.
- Shared-scene invariance passes against C23, with only the declared panel and left-support mesh changes. Right support, seat, room, sofa, all cameras, transforms, materials and visibility remain unchanged.
- The final white copy matches geometry, cameras, transforms and visibility across 385 objects and 35 cameras; only intentional material replacements differ.
- Both posts intersect the panel and seat at their joints. They remain separate overlapping objects.
- All 678 panel/frame-versus-non-chair pairs were scanned for C23 and v2b, including hidden geometry. No room/sofa surface collisions or sampled containment were detected.
- All 49 panel nearest feet pass full-scene geometric visibility probes.

## Fixed native source errors

RMS / maximum in native pixels, followed by scored/original record count. Tolerances are unchanged. Panel errors use the named physical branch; supports use directed x-at-source-y. Missing original points remain failures.

| Source branch | Tolerance / original count | C23 | v1 | v2 | v2b final |
|---|---:|---:|---:|---:|---:|
| H_C_TOP | 2.5 px / 10 | 3.032 / 7.327 (10/10) | 3.290 / 8.105 (10/10) | 3.290 / 8.105 (10/10) | 3.290 / 8.106 (10/10) |
| H_C_R_SHOULDER | 2.5 px / 9 | 2.043 / 3.524 (9/9) | 2.005 / 3.528 (9/9) | 2.005 / 3.528 (9/9) | 2.005 / 3.528 (9/9) |
| H_C_LOWER | 2.5 px / 9 | 2.917 / 7.193 (9/9) | 3.521 / 8.641 (9/9) | 3.521 / 8.641 (9/9) | 3.521 / 8.641 (9/9) |
| G_C_TOP | 3 px / 5 | 4.566 / 8.691 (5/5) | 5.052 / 9.645 (5/5) | 5.052 / 9.645 (5/5) | 5.053 / 9.646 (5/5) |
| G_C_R_SHOULDER | 3 px / 8 | 2.116 / 3.569 (8/8) | 2.123 / 3.567 (8/8) | 2.123 / 3.567 (8/8) | 2.123 / 3.567 (8/8) |
| N665_C_TOP_SLIVER | 3 px / 4 | 0.381 / 0.696 (4/4) | 0.588 / 1.034 (4/4) | 0.588 / 1.034 (4/4) | 0.588 / 1.033 (4/4) |
| N665_C_LOWER_SLIVER | 3 px / 4 | 0.345 / 0.473 (4/4) | 0.845 / 0.960 (4/4) | 0.845 / 0.960 (4/4) | 0.843 / 0.958 (4/4) |
| H_C_L_RETURN_OUTER | 3 px / 8 | 0.964 / 1.342 (2/8) | 5.618 / 8.486 (8/8) | 1.748 / 3.171 (7/8) | 1.748 / 3.171 (7/8) |
| H_C_L_SUPPORT_INNER | 3 px / 3 | 0.247 / 0.420 (3/3) | 3.392 / 4.073 (3/3) | 0.278 / 0.477 (3/3) | 0.278 / 0.477 (3/3) |
| H_C_R_SUPPORT_INNER | 3 px / 4 | 3.980 / 7.895 (4/4) | 3.980 / 7.895 (4/4) | 3.980 / 7.895 (4/4) | 3.980 / 7.895 (4/4) |
| H_C_R_SUPPORT_OUTER | 3 px / 4 | 0.338 / 0.586 (4/4) | 0.338 / 0.586 (4/4) | 0.338 / 0.586 (4/4) | 0.338 / 0.586 (4/4) |
| N665_C_L_SUPPORT_OUTER | 3 px / 4 | 0.311 / 0.526 (4/4) | 0.418 / 0.702 (4/4) | 0.418 / 0.702 (4/4) | 0.418 / 0.702 (4/4) |
| N665_C_L_SUPPORT_INNER | 3 px / 4 | 0.412 / 0.795 (4/4) | 0.480 / 0.940 (4/4) | 0.480 / 0.940 (4/4) | 0.480 / 0.940 (4/4) |

## Fixed composite-return ownership

C23 uses the panel for the first six observations (y=906–1020) and left post for the last two (1048/1070). Every C25 version uses the left frame/post for all eight. This is explicit construction attribution, not source-proven ownership and not error-minimizing object choice. Existing per-object diagnostics are retained.

| Eight original return observations | C23 | v1 | v2 | v2b final |
|---|---:|---:|---:|---:|
| RMS / max (scored/8) | 6.904 / 10.657 (8/8) | 5.618 / 8.486 (8/8) | 1.748 / 3.171 (7/8) | 1.748 / 3.171 (7/8) |

The final return misses its designated frame boundary at (440,906). Its 1.748/3.171 px RMS/max therefore score only seven of eight original records. Six of eight are within 3 px; one exceeds 3 px and one is missing. The separate panel boundary at the missing observation is 8.733 px away and is not substituted.

## Limits and stopping point

- The final cleanup and backing extension are declared construction repairs, not new source observations.
- Numerical BVH/triangle/ray checks are not exact rational or exhaustive containment certificates; shared-vertex triangle pairs are excluded from self-intersection checks.
- Visibility uses opaque evaluated mesh first hits. Material alpha/transmission and absent person/foreground occluders are not simulated. Source cuts are unchanged.
- G and 665 are prior training/regression views, not holdouts.
- V2b fixes the prior numerical cleanup defects. Remaining shape and native-render mismatches are not overruled by these numerical results.
- The verifier did not modify any model, camera or light. This bounded verification is complete.
