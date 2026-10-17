# Independent C23 → C25_v2 review

REJECTED_GEOMETRY_AND_SOURCE

## Geometry and shared scene

Shared-scene invariance: PASS; permitted mesh objects: Chair • narrow curved wraparound back, Chair • slim back support.

- Chair • narrow curved wraparound back: 20882 vertices, 41760 triangles; 0 nonmanifold vertices; 0 nonmanifold edges; orientation edge defects 0; signed volume 0.000358754594; nonadjacent numerical intersections 0.
- Chair • slim back support: 142324 vertices, 284552 triangles; 0 nonmanifold vertices; 0 nonmanifold edges; orientation edge defects 0; signed volume 0.000139201608; nonadjacent numerical intersections 0.

## Fixed-source errors

All values below are full-scene geometrically visible errors in native pixels. Panel rows use Euclidean distance on the named physical branch; support rows use directed x-at-observed-y. Return rows are kept per object, with no best-object union.

| Branch / object | Tolerance | C23 RMS / max (scored/total) | Candidate RMS / max (scored/total) | Candidate within tolerance |
|---|---:|---:|---:|---:|
| H_C_TOP | 2.5 | 3.032 / 7.327 (10/10) | 3.290 / 8.105 (10/10) | 7/10 |
| H_C_R_SHOULDER | 2.5 | 2.043 / 3.524 (9/9) | 2.005 / 3.528 (9/9) | 6/9 |
| H_C_LOWER | 2.5 | 2.917 / 7.193 (9/9) | 3.521 / 8.641 (9/9) | 7/9 |
| G_C_TOP | 3 | 4.566 / 8.691 (5/5) | 5.052 / 9.645 (5/5) | 2/5 |
| G_C_R_SHOULDER | 3 | 2.116 / 3.569 (8/8) | 2.123 / 3.567 (8/8) | 6/8 |
| N665_C_TOP_SLIVER | 3 | 0.381 / 0.696 (4/4) | 0.588 / 1.034 (4/4) | 4/4 |
| N665_C_LOWER_SLIVER | 3 | 0.345 / 0.473 (4/4) | 0.845 / 0.960 (4/4) | 4/4 |
| H_C_L_RETURN_OUTER | 3 | 0.964 / 1.342 (2/8) | 1.748 / 3.171 (7/8) | 6/8 |
| H_C_L_SUPPORT_INNER | 3 | 0.247 / 0.420 (3/3) | 0.278 / 0.477 (3/3) | 3/3 |
| H_C_R_SUPPORT_INNER | 3 | 3.980 / 7.895 (4/4) | 3.980 / 7.895 (4/4) | 3/4 |
| H_C_R_SUPPORT_OUTER | 3 | 0.338 / 0.586 (4/4) | 0.338 / 0.586 (4/4) | 4/4 |
| N665_C_L_SUPPORT_OUTER | 3 | 0.311 / 0.526 (4/4) | 0.418 / 0.702 (4/4) | 4/4 |
| N665_C_L_SUPPORT_INNER | 3 | 0.412 / 0.795 (4/4) | 0.480 / 0.940 (4/4) | 4/4 |
| H_C_L_RETURN_OUTER / panel-only diagnostic | 3 | 7.952 / 10.657 (6/8) | 30.609 / 37.093 (2/8) | 0/8 |

## Boundaries of this evidence

- No pixel-error threshold is relaxed. Missing/invisible original points remain failures; RMS with missing points must not be presented as an aggregate acceptance score.
- G and 665 are previous training/regression views, not independent holdouts.
- New semantic groups are declared construction evidence, constrained by actual H silhouette orientation; they are not independent source observations.
- No person/foreground occluder is synthesized, and source cuts are never extended. Full-scene visibility treats opaque evaluated mesh geometry, not alpha/transmission.
- Numerical BVH + double-precision triangle tests are not exact rational certification. Adjoining triangles sharing a mesh vertex are excluded from nonadjacent intersection checks.
- Contact intersections demonstrate overlap between separate objects, not mechanical joining or physically plausible hidden completion.
- White-copy invariance and native render appearance are separate parent checks.

The JSON artifacts retain each original source point, tolerance, exact target, directed branch, numerical error, ray first hits, and input hashes. No model or camera was saved by verification.

## Supplemental white-copy and non-chair collision checks

White copy: PASS. 385 objects and 35 cameras compared. Geometry, transforms, visibility, and other serialized scene state match exactly after exempting intentional material replacements. Unexpected differences: 0.

Full-scene scan: 678 panel/frame versus non-chair pairs per model, including hidden geometry. No numerical surface intersections or sampled containment were found in either C23 or C25 v2. Therefore no new room/sofa collisions were found. AABB-overlapping pairs were further tested with BVH, triangle narrow phase and three-direction parity probes. This is bounded numerical evidence, not exact certification.

## Fixed composite left-return comparison

C23 ownership is fixed to the panel for the first six source records (y=906–1020), and the left support for the last two (y=1048/1070). C25 v2 ownership is fixed to the continuous left frame/support for all eight. This is a declared construction ledger, with no per-point best-object selection. The per-object diagnostics above remain valid; their unequal visible coverage must not be compared as if they scored the same eight points.

| Original source point | C23 owner | C23 error px | C25 v2 owner | C25 v2 error px |
|---|---|---:|---|---:|
| [440, 906] | panel | 6.696 | left frame/support | MISSING |
| [440, 927] | panel | 6.295 | left frame/support | 0.109 |
| [435, 951] | panel | 5.688 | left frame/support | 3.171 |
| [433, 975] | panel | 7.152 | left frame/support | 2.386 |
| [433, 1000] | panel | 9.893 | left frame/support | 0.189 |
| [434, 1020] | panel | 10.657 | left frame/support | 2.000 |
| [432, 1048] | left support | 0.235 | left frame/support | 0.326 |
| [430, 1070] | left support | 1.342 | left frame/support | 1.218 |

C23 has 8/8 geometrically visible points under this ledger. C25 v2 has 7/8; missing points remain failures, and its RMS/max use only the scored subset. C23 RMS/max: 6.904/10.657 px, 2/8 within 3 px. C25 v2 RMS/max: 1.748/3.171 px, 6/8 within 3 px. Both fail the unchanged source tolerance.
