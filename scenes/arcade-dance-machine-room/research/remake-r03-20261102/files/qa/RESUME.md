# R02 resumable rendering (disk truth, not old session ID)
Current task was launched with 2 Blender CPU threads, denoise disabled. Never start another Blender render while this one is active.

1. Check `ps -eo pid,args | grep '[b]lender.*render_delivery.py'` and `qa/render_delivery.log` for progress. A log's Finished text alone is NOT image validation.
2. Run `python scripts/check_render_resume.py` from any cwd. It actually opens, verifies and fully decodes each expected PNG and checks exact dimensions; records per-image SHA256 in `qa/render_completion.json` and only valid names in `qa/valid_delivery_pngs.txt`.
3. If no current render process and items are missing/invalid, run `OMP_NUM_THREADS=2 blender -b -t 2 --python scripts/render_delivery.py > qa/render_delivery_resume.log 2>&1` from repo root. The renderer skips exactly the validated names and writes only missing/invalid images; preserved stage models are reopened read-only and not saved over.
4. After completion repeat validation, then `python scripts/direct_overlays.py` to form direct RGB 50% old/new-source diagnostic overlays. New-source overlays retain uncalibrated camera label and never imply fitting/acceptance.
5. Preserve all failed logs, do independent pixels, normal new Git commit. Do not rewrite old history or treat recovered source images as recovered old model bytes.
