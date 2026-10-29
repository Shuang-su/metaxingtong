# C30 conditional bed-deck height diagnostic

Sources identify the visible bed covering outline with high confidence, but identify it with the exact current bare mattress far-y boundary only with medium confidence. The visible endboard is not assumed to be the headboard. User context: camera is lying in the hospital bed.

One fitted degree of freedom: joint G/N642 top-height delta, about +0.13542 in uncalibrated scene units. H/665 are excluded from fitting and are previously seen check views, not blind tests. G/N residual disagreement remains.

Preserve mattress thickness and assembly-relative offsets by translating mattress, tray, two rails and the inferred low bumper equally upward. Keep endboard, inset, recess, wheels, crossmembers, chairs and every camera fixed. Extend the upper section of four existing supports to preserve their connection to the tray while keeping lower support geometry fixed. Support shape and hidden construction are explicit completion assumptions, not observed evidence.

This is an isolated trial. Reject if check-view bed outline or endboard openings regress materially. Do not modify cameras, expand mattress width/length, or secretly tune parameters to check views. Full-scene acceptance and physical dimensions remain unresolved.
