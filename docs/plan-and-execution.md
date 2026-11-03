# Executed stages

- Preflight: read main reconstruction standard, enumerate existing issues rather than only main scene directories, verify no render process, check archival owner via parent.
- R01: actual first model, material/white and GLB; early Space backup before long rendering. First topology check failed 10 curve-cap seams, one degenerate glazing polygon, winding, lamp annulus. Low-resolution source and check previews retained.
- R02: weld coincident cap vertices, remove degeneracy, outward normals. Lamp annulus still failed, retained.
- R02b: replace lamp shade with genuine closed hollow annular wall. Single-mesh topology audit passes; not a contact/source pass.
- R03: shared larger and offset arched opening/curtain zone, proportional central-seat reduction, two source camera guesses and one fixed light rig update. R01 reflected giant area disk failed and is retained. Source scene still visibly mismatched.
- R04: close introduced rear top shell gap, ground stool-leg vertices and lamp base, inferred lamp/curtain supports, bed-frame joints, add conditional low/oblique/fan cameras. Actual relative-depth files and their failures included.
- R05: fixed-geometry bounded camera-only fit for A/B/C. Mean manual training errors 22.29 / 16.82 / 27.97 native pixels, max 43.52 / 33.72 / 74.53. Not accepted; D/E/F cameras are uncalibrated diagnostic guesses. Same shared mesh and lights in all images. Final suite rendering in progress when this record was created.

Depth outputs are relative inverse-depth estimates, not brightness grayscale or measured distance. Dark pixels, characters, transparent windows, city imagery, light pools and shadows are unreliable. Cross-view ordering fails for E; do not treat per-image normalization as consistent depth or use shadow boundaries as solid geometry.

## R06 continuous bar section and final comparison suite
R06 replaces three separate rounded slabs with a single extruded U-profile waterfall bar. The bend, thickness, depth and right termination remain inferred, not measured. All other R05 geometry and cameras are retained. Original failed stages remain in ordinary Git history and as editable model files.

The final fixed-scene suite uses six source-view hypotheses (five official 1920×1080 and one fan 3840×2160) and eight diagnostic cameras, in both shared-geometry material and white variants. CPU Cycles 32 samples, adaptive threshold .05, six threads; no denoiser (installed build's actual denoising capability test failed and is retained). Rendering does not change or hide per-view objects. The exact original dimensions are used for direct 50% comparisons; visual aids/crops are labeled separately.

Native 4K pertains only to the separate same-day fan upload BV1q711BqE4K P1. Decode evidence proves 3840×2160 availability, not the upstream artistic source's absence of upscaling. The official upload BV1ic12BMEk6 reaches 1920×1080. No later different-date replay has been verified; source acquisition evidence and failed bounded follow-up are recorded.
