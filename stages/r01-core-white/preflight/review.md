# r01 preflight review (not final 8-angle acceptance)

All 87 core meshes individually closed/manifold, no degenerate faces, positive signed volume. Actual GLB import ran successfully:87 mesh identities retained, no missing/extra, maximum world-bounds delta4.76837158203125e-7 model units. This is file/geometry survival, not source acceptance.

Eight512×320 CPU Cycles8-sample angular renders and one640×360 provisional source-front render were visually inspected. They expose the whole core from8 azimuths, but noise is heavy:these are low-cost preflight only, not final high-quality8-angle evidence. Platform, true chevron openings and open upper rings are visible. Backside rests on only the2 observed supports; extra legs were not invented. Exact rear construction remains unknown.

Assembly uses actual world-space triangle BVHs plus vertex containment, not just OBB overlap.86 contact/intersection candidates require classification. Observed source companion120.140741 shows support tips at the floor, but does not establish whether hidden roots are embedded. The0.037 strip-foot penetration and0.13 lower-base/step overlap may be plausible embedded/solid joints, not automatically source defects. r02 will make an explicit alternative flush construction hypothesis rather than falsely declaring zero-overlap=truth. Tiny ring-tie intersections and central-bar joints are intentional inferred joins; they are not automatically errors. Crown lower-lip one-vertex containment is not reliable proof by itself.

Clear implementation issue:top inferred radial ties atz6.55 sit above bars ending6.42; this is an unintended0.13 gap and will be fixed. Source-front camera is too elevated, exposing too much platform ellipse, so it will be lowered; this is global camera fitting only, no local warp or camera-specific geometry.

Rendering first failed because this Blender build has no OpenImageDenoise. Failure log kept as preflight-denoise-unavailable.log. Retried with Cycles denoising disabled, succeeded; no further OIDN attempts.

The13.767175 relative-depth result was actually viewed: water/sky are globally far, palm silhouettes nearer than the sea, but mirrored platform becomes a smooth foreground mass, structural leg/band separation is smeared, and luminous rings appear flattened. Its numeric depth does not determine topology/contact or establish unique geometry.
