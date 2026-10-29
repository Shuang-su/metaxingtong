# Independent read-only pixel review

Reviewer: existing delegated agent `campus_readonly_pixel_qa`. No files or model changed. Source review and rendered-result review were separate actual viewing steps.

## Source review

The reviewer opened the new 1920×1080 source and full supplied note, and inspected Stage03 CHECK07-overhead, CHECK04-north, CHECK05-east and object list, with earlier MAIN/SRC04 viewing context. Source bytes/hash matched the handoff. Native-coordinate picks are preserved in `independent_pixel_picks.json`.

The reviewer rejected inventing four blue-court corners: the near-left corner is out of frame and far-right is occluded. Only a fragment of the central black hoop base is visible; its fragment centre is not the whole base centre. Stair rail/landing fragments are visible on the left, but precise landing identity is unknown. Repeated goals, lamps and benches cannot be assigned by identical design alone.

## Completed render review

The reviewer actually opened both contact previews, both F35 full-resolution renders, and both F35 full-resolution direct overlays. All six camera trials fail as acceptance evidence, but do not prove that every possible camera is impossible.

1. Forward F35 mean fitted-point error 3.51 px conceals incorrect occlusion: ENTRY-STEPS blocks the blue near-right corner and FLOWERBED-01 blocks the left net-foot target. The close facade, steps and planter occupy areas that appear open in the source.
2. Surrounding relations fail together: forward F35 places the entire stair behind the camera and all three goals at negative image x. Reverse F35 has mean fitted-point error 6.45 px but projects the stair on the right at x1647–1945, while the source stair fragments are left. This conclusion is conditional on the tested instance mapping and poses.
3. Reverse F35 has paving foreground, a distant narrow green strip, a multistorey repeated-window wall and unmatched central hoop/lamp-bench composition. Source foreground has green/red paint and arcs with a low background facade.

The reviewer explicitly cautioned that COURT-NE ray hits at net-foot samples z=.10 can arise because the surface top is z=.11; these are not independent strong occlusion evidence. The far-left-corner residual is also conditional on a candidate corner identity. Both cautions are included in REPORT.md.

The black forward F20 and foreground-obstructed forward F50 are retained. The F20 black result is consistent with the separately recorded six-axis ENTRY interior probes. The reviewer compared the before/reloaded JSON state records but did not independently reopen BLEND; the author performed that actual saved-file reopen.

Status: independent read-only review completed. Earlier cross-session diagnostic, not later-replay validation or source acceptance.
