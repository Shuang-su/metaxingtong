#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=6
# 2026-11-04 03:04 UTC: original session 72936 unknown; no process; log stopped at 03:03:27 UTC.
# All 16 completed images decoded and matched their JSON SHA. Do not re-render them.
/usr/bin/blender -b models/lakeleaf-r06-white.blend -t 6 --python-exit-code 10 --python scripts/render_cameras.py -- --output renders/r06/white-source --cameras SOURCE_108755584_OBLIQUE AUX_006585758_REAR --samples 16 --threads 6 --percentage 100 > qa/render-r06-white-source-resume1.log 2>&1
/usr/bin/blender -b models/lakeleaf-r06-white.blend -t 6 --python-exit-code 10 --python scripts/render_cameras.py -- --output renders/r06/white-checks --cameras CHECK_01 CHECK_02 CHECK_03 CHECK_04 CHECK_05 CHECK_06 CHECK_07 CHECK_08 --samples 12 --threads 6 --percentage 100 > qa/render-r06-white-checks.log 2>&1
python scripts/assemble_white_evidence_r06.py
python scripts/audit_final_image_delivery_r06.py
/usr/bin/blender -b models/lakeleaf-r06-material.blend -t 6 --python-exit-code 10 --python scripts/render_low_diagnostic_r06.py > qa/render-r06-low-diagnostic.log 2>&1
