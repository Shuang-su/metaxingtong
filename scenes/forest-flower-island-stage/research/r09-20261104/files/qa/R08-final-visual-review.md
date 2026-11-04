# R08 final visual and image-integrity review

All 28 final PNGs were fully decoded, dimensioned and SHA256 recorded. All 12 direct50 overlays were independently checked over the entire RGB arrays against floor((source+render)/2): maximum error0 for every output, source/render/overlay hashes all match producer manifest. Source comparisons are1920x1080 native grids; model inspections are1280x720. No resampling or registration is needed for the exact direct50 formula.

Visual review actually performed: all12 full-frame material/white direct50 overlays and all16 original CHECK PNGs, in addition to earlier original source images. This is separate from decoding all28 output PNGs. Both material and white eight-angle sets are nonblank and diagnostically useful:
- CHECK01: foreground leaves partially obscure island but main-tree buttress, vegetation and island placement remain visible; useful for context/occlusion, not full unobstructed flower inventory.
- CHECK02/03/05: clear elevated views from different azimuths showing cup forms, stems, top vegetation, rim and perimeter.
- CHECK04: broad left trunk partly occludes the island but visible right/central layout and trunk-island relation remain useful. Limited for the hidden sector.
- CHECK06: lower side view reveals rim, stems and hanging underside against surrounding trees.
- CHECK07: overhead layout clearly exposes circular bed and eleven modeled giant flowers; layout visibility does not prove correspondence with source instances.
- CHECK08: low view explicitly exposes tapered underside, radiating roots, vegetation and separation from ground. White improves dark underside structure reading.

These eight angles are diagnostic model viewpoints, not eight source-camera observations or accurate-scene acceptance. White images retain Monte Carlo grain; small grass detail cannot be finely accepted from them. No hidden geometry trick was found in technical audit. Not every object backside is independently verified by this finite view set.

All six source alignments remain FAILED in both variants. A/B are early-state/layout auxiliary views and cannot establish a shared unchanging world state. Giant-flower order, dimensions and shapes, peripheral plant placement, root/core silhouette, tree shapes, background density and island/environment height relations differ visibly. F's approximate training point statistics do not resolve the obvious flower and environment discrepancies. E's dark lower mass is not validated as exact soil/root composition. Camera-specific hiding/moving was not used to conceal mismatches.

Technical export/shared geometry and representative clearance evidence are separate reports. Complete object-source mapping, comprehensive scene intersections, exact natural vegetation, physically measured scale, motion reconstruction and independent later replay verification remain unaccepted/not run. The R09 G4K diagnostic will be reviewed separately when its full-size pair is complete.

Evidence: R08-final-image-integrity.json binds this review to exact image hashes; R08-independent-summary.md and its four JSONs bind the models, exports, textures and UVs. R08-representative-clearance.json and R08-independent-landmark-check.json preserve the limited clearance and failed training findings. This review does not claim Git publication or final user acceptance.
