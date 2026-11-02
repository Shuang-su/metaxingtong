# r05 LED display-face correction preflight

All394 mesh world geometry, all old cameras and lights remain unchanged. Four display objects now assign imagery only to outward cylinder faces (rear rail uses inward-facing display); caps and backfaces are metal. Angular UV seams are unwrapped and inward rail U reverses so its text reads correctly. White and material mesh geometry hashes match.

Actual low-resolution front/outer-front/outer-back/inner-crown inspection shows the reverse inner text is gone and exterior letters read in the correct direction. However curve-band UVs inherited from r02 still place small labels across the band width, with mirrored/reversed reading. This is a remaining technical texture-coordinate error, so r06 will correct band orientation without moving geometry, lamps or source cameras.

Eight new elevated diagnostic camera positions were added without changing any existing camera; checks03/04/06/07 were visually inspected after the old views were heavily blocked by palms. No palm is hidden or moved. These are diagnostic angles, never additional source/holdout evidence. White contrast and partial natural occlusion remain, but central crown/stage structure is visible rather than covered by foreground palm crowns.

These8 low-cost images are preflight only; the complete final suite must use the corrected material stage.
