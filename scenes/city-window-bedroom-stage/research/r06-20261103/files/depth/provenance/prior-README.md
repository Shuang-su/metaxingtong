# Relative-depth technical validation, 2026-11-02

This is NOT a new scene and NOT source-reconstruction acceptance. One recovered historical native camp frame was hash-verified and analyzed using the official Apache-2.0 Depth Anything V2 Small safetensors model. It is relative inverse-depth-like prediction, not luminance grayscale or metric truth. Native reference 1920x1080; actual model tensor/output 924x518; bicubic source-grid display is marked derived.

See `camp-tool-validation/report.json` for source identity, package versions, masks, range, files/SHA and actual visual failures. `run_depth.py` is the full reproducible script. The unchanged historical source remains in the adjacent recovery repository at the exact path/hash recorded in report; it is not recreated. Install logs and package freeze preserved. Model cache is local, weights excluded from this tool-evidence Git; exact revision/SHA in model-artifact-manifest.json. No external push was performed here.

Manually drawn exclusion ROIs are conservative and incomplete, not semantic instance segmentation. 255 in confidence-unknown mask means unknown everywhere, NEVER high confidence. Sky and subtitle are especially invalid for reconstructing real geometry. No confidence head, absolute scale, static contact, hidden geometry, or unique camera established. Per-image normalization cannot compare metric distance across views.

The reported elapsed time covers inference and initial output encoding, not isolated model forward benchmarking. CPU only; no CUDA packages. Blender 4.3.2 background startup tested successfully; no Blender connector available in tool registry.

