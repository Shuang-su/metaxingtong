# Hospital chair: bounded native-source capture, 2026-10-16

Four genuine browser-saved PNG originals are preserved in `originals/`. Each is 1920×1080. There are no viewport enlargements, resampled originals, annotations, generated images, or ZIP files in this handoff. Full byte counts, SHA-256 checksums, browser media state and download-event paths are in `native_capture_manifest.json`.

## Useful findings

- **658.052095 s**: clearest new early close view. The green rolled/returned region and descending outside boundary sit to the left of the person's arm. The region is visibly part of the chair rather than a person-created edge. The person still conceals much of the panel's interior connection, while the foreground hides the lower chair.
- **650.811153 s**: second early view from a different camera placement. The left rolled/returned region is also exposed and has a bright top edge, a widened vertical side region and a visible inner edge against the dark panel. This is useful for semantic correspondence; it does not identify a hidden mechanical mount.
- **1103.087901 s**: empty-chair view. The back panel and left rolled/returned side are unoccluded by the person; upper parts of both supports are visible. Window and sofa anchors remain in view. The source frame/foreground cuts off lower supports and seat. This is the strongest new late correspondence view.
- **872.246724 s**: deliberately sampled mid-gap context. The same style of green left-side region is visible, but the person overlaps the panel, central support and seat regions. It documents an occlusion limit rather than establishing continuity. Keep it contextual rather than silently adding a new fitting target.

## Source quality and capture method

The hospital source was accessible in the existing logged-in dot cloud browser. The displayed highest option was **1080P 高码率**; the menu offered no 4K. The selected quality label stayed at 1080P 高码率, and the video element reported native 1920×1080 pixels.

Each original came from Chromium's native **将视频帧另存为…** command. The first right click displayed Bilibili's custom menu; a second right click in an uncovered video region exposed the native menu. Full-desktop screenshots were used to see the native menu. Moving the pointer to the save-frame item and pressing Enter triggered a download. All four download events returned actual completed file paths; the files were copied byte-for-byte into this folder, opened as PNGs and checked for 1920×1080 dimensions.

Media current time stayed unchanged across each save, and playback was paused. The manifest records readyState=4 before and after for 650.811153, 872.246724 and 1103.087901. For 658.052095, pre-save paused state, time and dimensions were recorded, but pre-save readyState was not recorded. Its post-save readyState was 4. The missing pre-save field is explicitly null, not inferred.

## What this pass does not establish

The repeated left-side green feature supports a real chair surface/return rather than a person boundary. It still does not decide whether the visible inner transition belongs wholly to a rolled panel return, a separate upright overlapping it, or a molded joint. Do not treat the repeated feature as a recovered hidden mount.

**Unchanged rigid chair pose across 665–1101 s remains unverified.** This pass saved discrete neighboring views and one mid-gap context frame; it did not obtain an uninterrupted record of the chair's room-relative pose. The person and foreground conceal decisive regions in the middle of the gap. Similar design and similar room layout are not proof of identical world pose.

The inspected 645.229417 s view had more person occlusion. The 1107.161461 s view was blurred during a camera swing; 1114.234255 and 1116.241036 s framed the person/bed and offered no clearer left-junction view. These were not saved as native targets.

All new source frames are development/correspondence evidence, not held-out validation. The existing N642 holdout was not opened. No model, camera, branch definition, tolerance, or geometry was changed.

## Handoff

Use the new 658 and 1103 originals first for the panel-return/post ownership ledger. Preserve the competing interpretations if their exact surface ownership remains ambiguous. Keep same-pose assumptions conditional unless a separate pose analysis resolves them.
