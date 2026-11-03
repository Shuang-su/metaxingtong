# Relative depth analysis, 2026-11-03

Depth Anything V2 Small official Hugging Face safetensors model, revision `5426e4f0f36572d16453bbda7a8389317b1bef99`. All four downloaded model files match the SHA256 and sizes recorded in yesterday's archived PR96 manifest. The 99,173,660-byte weights have SHA256 `3152477ce0d8d6978d76b995120de97cb5b928701fd0f817769f59e249a16b70`.

The CPU-only Python environment was restored from official PyTorch/PyPI distributions. Actual versions and install logs are in `provenance/`. No remote model code is enabled. `run_depth_frame.py` is the complete inference and report script; it expects an original source image and its metadata JSON. The model weights and virtual environment are operational caches, not project artifacts, and should not be committed.

The script preserves float32 model-grid relative inverse-depth-like prediction and a 16-bit grayscale display. White/larger generally means nearer, black/smaller generally farther. Source-grid `.npy` and 8-bit PNG are explicitly bicubic-derived for comparison, never claimed as independent native-resolution depth. Each report includes source hash, size, source time metadata, exact method, package versions, tensor sizes, normalization range and output hashes.

Manual masks mark conservative character, text, sky, reflection or other suspect regions only when actually inspected. Zero in these masks is unlabelled, not certified valid. The all-255 confidence-unknown mask means the model supplies no calibrated confidence; it is never a high-confidence map. Numerical nonfinite mask is separate. Occluded/hidden structures have no observed depth, and depth inference is not measured distance, metric scale, contact evidence or geometry acceptance.

`recovery-test/` uses a historical camp frame solely to verify restored tooling. It is NOT a new scene or new source validation. Actual inference completed at model-grid 924×518 with no nonfinite values. Visual inspection shows plausible rough foreground/background ordering but incorrectly gives subtitle graphics depth; the subtitle exclusion is required. This is evidence of tool execution, not scene reconstruction quality.

Production-source outputs, when present, are separate directories with their own metadata and limitations. A successful inference never replaces multi-view native references or direct 50% unwarped overlays.
