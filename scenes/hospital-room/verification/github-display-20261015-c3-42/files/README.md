# Issue 4: 42 new images visually checked

Checked on 2026-10-15, 05:35:57.324–05:42:46.608 UTC, in the dot cloud Chromium browser.

Result: 42/42 new inline images visibly rendered, with full image content and bottom edges inspected. No broken image, partial load or collapsed image was observed.

- D comment 6147605558: newly added 8 only. Old 15 were excluded.
- C2 comment 6185128438: 8.
- C3 comment 6185156544: 26.
- 44 clean PNG screenshot files: 40 single-viewport full-image captures plus two overlapping top/bottom pairs for G top-connection and N640 pillar-fold comparison boards.

Each image was scrolled into the actual Issue page viewport and visually inspected through browser screenshots. No HTTP response or naturalWidth-only check was used as a substitute. The manifest includes exact image and comment URLs, per-image UTC time, dimensions, visible coverage, screenshot paths and SHA256 values. Image 24 was rechecked at 05:42:46.608 UTC because its initial DOM metadata preceded completion of loading; the final visible image and final metadata passed. The original intermediate DOM observation is retained in the manifest. Raw image URLs were recorded from the comments, not separately visited.

Screenshots are cropped only to remove personal account/sidebar UI. No rescaling, compositing, retouching, sharpening or alteration of evidence content. The browser capture is JPEG; clean crops are stored as lossless PNG, preserving the captured crop pixels. Existing focus borders and pointer are browser UI. No ZIP was created.

Display validation does not establish source accuracy, geometry quality, reconstruction acceptance or user approval. D/C2 unaccepted and C3 source-failed states remain unchanged. No GitHub content was edited; Bilibili tab 2 was left untouched and no downloads were deleted.

## Files

- manifest.json: complete per-image evidence and limitations.
- manifest.tsv: compact 42-row URL/time/checklist.
- screenshots/: 44 clean browser captures.
- target-images.json: exact task image list extracted from the three comments.
- SHA256SUMS.txt: hashes for all deliverable files except this checksum file itself.

This directory is prepared for downstream real Git archival. No Git commit or external publication was performed in this verification step.
