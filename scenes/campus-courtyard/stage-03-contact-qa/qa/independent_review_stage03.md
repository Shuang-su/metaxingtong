# Second independent read-only review

Reviewer `/root/campus_readonly_pixel_qa` inspected the corrected stage-03 images independently, with no file/model changes.

- SRC04 lower-right exposed floor side/background has become continuous pavers. The specified ROI missed 1372/1537 rays before and 0/1537 after. This only proves coverage in that region.
- ENTRY close comparison shows flowerbed02 clear of steps; MAIN comparison shows flowerbed03 removed from blue court. AABB tests retain about0.04 and0.89 model-unit separation, respectively. New positions remain inferred.
- BENCH01 gap is filled by foot plates; BENCH02 embedded feet are replaced by plates on the lawn surface; HOOP02 base now shows full thickness. All29 specified support samples agree within1e-5; this is not full-model collision acceptance. Stair underground foundations remain inferred.

Source discrepancies remain: SRC04 board too small, window/facade mismatch, court boundary/red-orange paint/white arcs unconfirmed, crown density/shadows differ. Stage02 and03 camera_parameters.json are identical. Camera-only and paint trials are recorded as not adopted. The new reverse frame was not received or used.

Actually viewed: stage03 MAIN, SRC04, SRC04 comparison strip, floor before/after, all four BENCH01/BENCH02/HOOP02/ENTRY contact pairs; re-viewed stage02 MAIN. Read support data, frozen constraints, both rejection notes. Did not re-view other three stage03 source strips, every eight-angle image, white BLEND or GLB, so those are not claimed as independent visual checks.
