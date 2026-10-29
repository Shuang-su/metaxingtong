# Independent C23 → C25 review

REJECTED_GEOMETRY_AND_SOURCE

## Geometry and shared scene

Shared-scene invariance: PASS; permitted mesh objects: Chair • narrow curved wraparound back, Chair • slim back support, Chair • slim back support.001.

- Chair • narrow curved wraparound back: 16562 vertices, 33120 triangles; 0 nonmanifold vertices; 0 nonmanifold edges; orientation edge defects 0; signed volume -0.000424539742; nonadjacent numerical intersections 238.
- Chair • slim back support: 136948 vertices, 273892 triangles; 0 nonmanifold vertices; 0 nonmanifold edges; orientation edge defects 0; signed volume 0.000199136217; nonadjacent numerical intersections 0.
- Chair • slim back support.001: 54794 vertices, 109584 triangles; 0 nonmanifold vertices; 0 nonmanifold edges; orientation edge defects 0; signed volume 6.75924946e-05; nonadjacent numerical intersections 0.

## Fixed-source errors

All values below are full-scene geometrically visible errors in native pixels. Panel rows use Euclidean distance on the named physical branch; support rows use directed x-at-observed-y. Return rows are kept per object, with no best-object union.

| Branch / object | Tolerance | C23 RMS / max (scored/total) | Candidate RMS / max (scored/total) | Candidate within tolerance |
|---|---:|---:|---:|---:|
| H_C_TOP | 2.5 | 3.032 / 7.327 (10/10) | 3.713 / 8.675 (10/10) | 7/10 |
| H_C_R_SHOULDER | 2.5 | 2.043 / 3.524 (9/9) | 1.989 / 3.566 (9/9) | 7/9 |
| H_C_LOWER | 2.5 | 2.917 / 7.193 (9/9) | 4.666 / 9.867 (9/9) | 5/9 |
| G_C_TOP | 3 | 4.566 / 8.691 (5/5) | 5.741 / 10.423 (5/5) | 1/5 |
| G_C_R_SHOULDER | 3 | 2.116 / 3.569 (8/8) | 2.145 / 3.493 (8/8) | 6/8 |
| N665_C_TOP_SLIVER | 3 | 0.381 / 0.696 (4/4) | 1.375 / 1.906 (4/4) | 4/4 |
| N665_C_LOWER_SLIVER | 3 | 0.345 / 0.473 (4/4) | 1.670 / 1.783 (4/4) | 4/4 |
| H_C_L_RETURN_OUTER | 3 | 0.964 / 1.342 (2/8) | 5.562 / 8.486 (8/8) | 3/8 |
| H_C_L_SUPPORT_INNER | 3 | 0.247 / 0.420 (3/3) | 3.392 / 4.072 (3/3) | 1/3 |
| H_C_R_SUPPORT_INNER | 3 | 3.980 / 7.895 (4/4) | 6.279 / 12.489 (4/4) | 3/4 |
| H_C_R_SUPPORT_OUTER | 3 | 0.338 / 0.586 (4/4) | 0.398 / 0.722 (4/4) | 4/4 |
| N665_C_L_SUPPORT_OUTER | 3 | 0.311 / 0.526 (4/4) | 0.418 / 0.702 (4/4) | 4/4 |
| N665_C_L_SUPPORT_INNER | 3 | 0.412 / 0.795 (4/4) | 0.480 / 0.940 (4/4) | 4/4 |
| H_C_L_RETURN_OUTER / panel-only diagnostic | 3 | 7.952 / 10.657 (6/8) | missing | 0/8 |

## Boundaries of this evidence

- No pixel-error threshold is relaxed. Missing/invisible original points remain failures; RMS with missing points must not be presented as an aggregate acceptance score.
- G and 665 are previous training/regression views, not independent holdouts.
- New semantic groups are declared construction evidence, constrained by actual H silhouette orientation; they are not independent source observations.
- No person/foreground occluder is synthesized, and source cuts are never extended. Full-scene visibility treats opaque evaluated mesh geometry, not alpha/transmission.
- Numerical BVH + double-precision triangle tests are not exact rational certification. Adjoining triangles sharing a mesh vertex are excluded from nonadjacent intersection checks.
- Contact intersections demonstrate overlap between separate objects, not mechanical joining or physically plausible hidden completion.
- White-copy invariance and native render appearance are separate parent checks.

The JSON artifacts retain each original source point, tolerance, exact target, directed branch, numerical error, ray first hits, and input hashes. No model or camera was saved by verification.
