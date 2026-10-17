# Source / C23 / C25 v1 / C25 v2: bounded independent comparison

Final status: source-unaccepted. V1 passes the tested numerical geometry checks. V2 additionally fails numerical geometry cleanup because the left-frame object has 24 components (one main solid, 23 tiny remnants) and two degenerate triangles. Neither version adds detected room/sofa collisions.

Both material/white pairs match geometrically and retain all 35 cameras, transforms and visibility. Both retain all C23 scene state except the declared panel and left-support mesh changes.

## Native source errors

RMS / maximum in pixels, followed by scored/original record count. Panel errors are restricted to the named physical branch; support errors are directed x-at-original-y. Missing points remain failures.

| Source branch | Source tolerance/count | C23 | C25 v1 | C25 v2 |
|---|---:|---:|---:|---:|
| H_C_TOP | 2.5 px / 10 | 3.032 / 7.327 (10/10) | 3.290 / 8.105 (10/10) | 3.290 / 8.105 (10/10) |
| H_C_R_SHOULDER | 2.5 px / 9 | 2.043 / 3.524 (9/9) | 2.005 / 3.528 (9/9) | 2.005 / 3.528 (9/9) |
| H_C_LOWER | 2.5 px / 9 | 2.917 / 7.193 (9/9) | 3.521 / 8.641 (9/9) | 3.521 / 8.641 (9/9) |
| G_C_TOP | 3 px / 5 | 4.566 / 8.691 (5/5) | 5.052 / 9.645 (5/5) | 5.052 / 9.645 (5/5) |
| G_C_R_SHOULDER | 3 px / 8 | 2.116 / 3.569 (8/8) | 2.123 / 3.567 (8/8) | 2.123 / 3.567 (8/8) |
| N665_C_TOP_SLIVER | 3 px / 4 | 0.381 / 0.696 (4/4) | 0.588 / 1.034 (4/4) | 0.588 / 1.034 (4/4) |
| N665_C_LOWER_SLIVER | 3 px / 4 | 0.345 / 0.473 (4/4) | 0.845 / 0.960 (4/4) | 0.845 / 0.960 (4/4) |
| H_C_L_RETURN_OUTER | 3 px / 8 | 0.964 / 1.342 (2/8) | 5.618 / 8.486 (8/8) | 1.748 / 3.171 (7/8) |
| H_C_L_SUPPORT_INNER | 3 px / 3 | 0.247 / 0.420 (3/3) | 3.392 / 4.073 (3/3) | 0.278 / 0.477 (3/3) |
| H_C_R_SUPPORT_INNER | 3 px / 4 | 3.980 / 7.895 (4/4) | 3.980 / 7.895 (4/4) | 3.980 / 7.895 (4/4) |
| H_C_R_SUPPORT_OUTER | 3 px / 4 | 0.338 / 0.586 (4/4) | 0.338 / 0.586 (4/4) | 0.338 / 0.586 (4/4) |
| N665_C_L_SUPPORT_OUTER | 3 px / 4 | 0.311 / 0.526 (4/4) | 0.418 / 0.702 (4/4) | 0.418 / 0.702 (4/4) |
| N665_C_L_SUPPORT_INNER | 3 px / 4 | 0.412 / 0.795 (4/4) | 0.480 / 0.940 (4/4) | 0.480 / 0.940 (4/4) |

## Composite return with fixed ownership

The per-object C23 return score above covers only two visible records. For a comparable whole-chair return score, C23 uses the panel for the first six source records (y=906–1020) and the post for the last two (1048/1070); both C25 versions use the left-frame/post object for all eight. This ledger is declared construction attribution, not source-proven ownership and not error-minimizing object selection.

| Composite source | C23 | C25 v1 | C25 v2 |
|---|---:|---:|---:|
| H return, 8 original points | 6.904 / 10.657 (8/8) | 5.618 / 8.486 (8/8) | 1.748 / 3.171 (7/8) |

V2 has no directed frame boundary at source (440,906), so its 7-point RMS/max must not be treated as an all-eight-point pass. Of the eight original records, C23 has 2 within 3 px, v1 has 3, and v2 has 6; both the missing v2 point and its 3.171 px point fail.

## Verification limits

- Numerical closedness, orientation and BVH checks are not exact rational certification. Adjacent triangles sharing a mesh vertex are excluded from self-intersection checks.
- Separate chair objects overlap at intended joints; these are not one welded physical object.
- Full-scene contact scans test 678 non-chair pairs in each model, including hidden geometry; containment uses bounded three-direction ray-parity samples.
- All 49 nearest panel feet in v1 and v2 pass geometric full-scene visibility probes. Material alpha/transmission and absent person/foreground occluders are not simulated.
- G and 665 are prior training/regression views, not held-out evidence.
- The remaining visual structural mismatches are not overruled by numerical results.
