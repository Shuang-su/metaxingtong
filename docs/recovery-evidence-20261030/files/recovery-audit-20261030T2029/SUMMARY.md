# Recovery continuity audit

14 expected Git repository roots are absent in the current mounted filesystem. HEAD/status/fsck/model-manifest comparison cannot run. The previous publication stage-index is also absent.

25 previews/reports survive in current scratch and have freshly computed hashes in continuity.json; these are not models or Git history. No .blend/.glb/.bundle/.pack was located in shared/current scratch. This does not establish permanent deletion: restoring the former shared mount or a platform snapshot may recover original objects. Do not reconstruct a synthetic history from Issue SHA text.

No original branches modified; no external writes, login attempts, rendering or cloud tasks.
