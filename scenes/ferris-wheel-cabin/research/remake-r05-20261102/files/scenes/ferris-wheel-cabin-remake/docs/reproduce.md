# Reproduce / editable files

Blender 4.3.2, CPU 2 threads, Cycles; optional OIDN unavailable and disabled (not an error to work around). Images are raw noisy renders, no AI enhancement. Model files contain procedural simple Principled materials, no missing texture-image dependencies.

Current material/white original: `models/ferris_remake_R03_{material,white}.blend`.
Current GLB exports: same basename `.glb`.

Actual history: `scripts/build_remake.py` R01; `scripts/build_remake_R02.py` adds round-to-rectangle door opening transitions; `scripts/repair_normals_R03_if_needed.py` loads actual R02 and corrects closed-solid orientation preserving world vertices and cameras. To recreate current geometry, run R02 then R03 with `blender -b -t 2 --python <script>`. Files are new implementation, not recovered historical R08b source.

QA: validate_R03.py (white equality, GLB fresh import, local rays), additional_audit_R03.py (actual inner-loop central rays, per-object orientation/edge incidence, cream visibility), compare_R02_R03.py (worldvertex SHA, camera equality and all nine old misclassified rays), verify_actual_glb_R03.py (actual imported GLB orientation/position-seam edge checks). Validation must retain every observed failure and report, not just final PASS counters. Structural ray checks use closed local shell bounds only as test domain, never as source dimensions proof.

Final images: render_native_R03.py; all four source poses use same scene and fixed area lights, then separate persisted white original. Check images are internal diagnostics, not newly acquired source baselines. The supplementary `DIAGNOSTIC_support_fill` explicitly changes camera/fill light only to see underside; not used as source view or ordinary lighting acceptance.

Depth tool: `scripts/depth_analysis.py` requires external installed Python environment torch/transformers/Pillow/numpy and official local Depth Anything V2 Small-hf cache from the separately maintained `depth-validation-20261102/` tool evidence. Exact model revision, weight SHA, processor and package versions are in `qa/depth/report.json`; weight binaries and Python venv are not shipped in this scene. This is an explicit external analysis runtime dependency, not a missing BLEND/GLB material dependency. No network execution/remote-code trust during inference. The analyzed raw numerical outputs/masks are included, so results can be inspected without the model runtime.

No LFS. All files are ordinary Git blobs. Local readback audit is not remote verification; parent publishes via authorized file receipt and normal Git, then separately verifies actual fetched remote bytes. Model/preview backups must not be deleted before this verification.
