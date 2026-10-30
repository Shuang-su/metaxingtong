# Shared material candidate — conditional reconstruction

This is a finite 3D courtyard candidate, not accepted source reconstruction. Four native source frames were actually decoded and viewed. One geometry and one daylight/material state serves every source camera and all inspection cameras. There are no camera-dependent object toggles, scene-photo billboards, character meshes, image warps or per-view geometry changes.

The final candidate contains 128 mesh assemblies: finite L-shaped facade shells, 76 candidate facade openings including one entrance, recessed frames and panes, roof rails, stepped entrance/landing, partial track and sports surfaces, two tree beds, seven volumetric trees, shrubs/flower beds, four curved lamps, four benches, three goal frames, court net, three basketball stands, a three-ball rack, bins, exterior switchback stair and connected landing guard returns. Counts in hidden/occluded repeats are inferred. The scene does not assert a measured 400m track, full regulation basketball court or complete campus.

All world units are arbitrary. Each window repeat has a stable candidate ID; exact source instance correspondence remains unresolved. Tread solids have stable per-flight IDs and vertex ranges in `qa/stair_tread_instances.csv`. Exterior stair dimensions, hidden flights, structural joints and landing details are provisional. Models contain real geometry and openings, not a whole-scene image texture.

Initial failures are retained under `research/`: unavailable denoiser; reversed east-wing shell; insufficient rotational camera guesses; tree/bench placement and landing-rail continuity corrections. These were actual stages, with actual saved BLEND/GLB and completed renders. Interrupted renders are not counted as final checks. All final views are rerendered from the corrected shared scene.

SRC02 and SRC04 use a bounded manual-landmark fit. The fit hit height/focal bounds and is underconstrained by approximate image picks. The same picks are used to report fit residuals: they are not independent validation. SRC01 and SRC03 are manual estimates. No camera is declared calibrated. Foreground character occlusion, source sharpening/chromatic aberration and blur remain in every original and every overlay.

`renders/MAIN.png` is a normal daylight overview for review. `renders/SRC01..04.png` are 1920×1080 conditional source views. `renders/CHECK*.png` are eight internal geometry checks at 1280×720, including overhead, back and stair views; they are not eight additional source baselines. `comparison/` contains direct full-resolution 50% blends and labelled strips, plus ten native-coordinate crop groups. Strips/contact sheets are separately labelled display reductions.

Remaining source work: joint camera/geometry solve, facade/window proportions and repeat identity, track curvature, court extent, furniture spacing, canopy silhouette/density, bark/paving material scale, source sunlight/shadows, hidden support/extension uncertainty and later other-replay same-scene validation. No user acceptance has been received. The four source images all come from one BV. Live-rendered versus prerecorded status remains unknown.

Geometry, source, file delivery and user acceptance are separate gates. The limited tests in `qa/` do not certify untested intersections, every passage, real-scale accessibility or structural safety.
