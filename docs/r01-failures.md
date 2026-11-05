# r01 post-freeze failures
Independent r00 contact QA found umbrella shaft→ribs ~.302 and shaft→canopy ~.310 unit gaps. r01 retained same missing hub relation despite height changes. Do not claim structural pass. Formal render job interrupted after completed files only; qa/render-material.json gives actual completed subset. Pending white/source views not counted complete.

Actual factory-restored low render visually differed from the saved BLEND camera: generator captured matrix_world before dependency update after aiming changes. Corrected sidecar is captured from actual saved BLEND, and build.py adds view_layer.update. r01 restored renders were thus wrong camera comparisons, despite successful import.
