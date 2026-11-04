#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2
mkdir -p qa/r06 renders/r06/source renders/r06/checks renders/r06/main renders/r06/white renders/r06/white-source renders/r06/white-checks
# verify_delivery was already run against the exact preflighted files; do not repeat this expensive unchanged check.
/usr/bin/blender -b -t 1 --python-exit-code 10 --python scripts/restore_glb_cameras_r06.py > qa/restore-glb-cameras-r06.log 2>&1
/usr/bin/blender -b -t 1 --python-exit-code 10 --python scripts/verify_camera_export_r06.py > qa/verify-camera-r06.log 2>&1
/usr/bin/blender -b -t 1 --python-exit-code 10 --python scripts/verify_restored_cameras_r06.py > qa/verify-restored-cameras-r06.log 2>&1
/usr/bin/blender -b -t 1 --python-exit-code 10 --python scripts/verify_vein_footprints_r06.py > qa/verify-vein-footprints-r06.log 2>&1
python scripts/verify_r06_diff.py
/usr/bin/blender -b models/lakeleaf-r06-material.blend -t 2 --python-exit-code 10 --python scripts/render_cameras.py -- --output renders/r06/source --cameras SOURCE_092142973_SIDE SOURCE_100762992_TOP SOURCE_108755584_OBLIQUE AUX_006585758_REAR --samples 16 --threads 2 --percentage 100 > qa/render-r06-source.log 2>&1
/usr/bin/blender -b models/lakeleaf-r06-material.blend -t 2 --python-exit-code 10 --python scripts/render_cameras.py -- --output renders/r06/checks --cameras CHECK_01 CHECK_02 CHECK_03 CHECK_04 CHECK_05 CHECK_06 CHECK_07 CHECK_08 --samples 12 --threads 2 --percentage 100 > qa/render-r06-checks.log 2>&1
/usr/bin/blender -b models/lakeleaf-r06-material.blend -t 2 --python-exit-code 10 --python scripts/render_cameras.py -- --output renders/r06/main --cameras HERO --samples 32 --threads 2 --percentage 100 > qa/render-r06-main.log 2>&1
/usr/bin/blender -b models/lakeleaf-r06-white.blend -t 2 --python-exit-code 10 --python scripts/render_cameras.py -- --output renders/r06/white --cameras HERO --samples 12 --threads 2 --percentage 100 > qa/render-r06-white.log 2>&1
python scripts/assemble_evidence_r06.py
/usr/bin/blender -b models/lakeleaf-r06-white.blend -t 2 --python-exit-code 10 --python scripts/render_cameras.py -- --output renders/r06/white-source --cameras SOURCE_092142973_SIDE SOURCE_100762992_TOP SOURCE_108755584_OBLIQUE AUX_006585758_REAR --samples 16 --threads 2 --percentage 100 > qa/render-r06-white-source.log 2>&1
/usr/bin/blender -b models/lakeleaf-r06-white.blend -t 2 --python-exit-code 10 --python scripts/render_cameras.py -- --output renders/r06/white-checks --cameras CHECK_01 CHECK_02 CHECK_03 CHECK_04 CHECK_05 CHECK_06 CHECK_07 CHECK_08 --samples 12 --threads 2 --percentage 100 > qa/render-r06-white-checks.log 2>&1
python scripts/assemble_white_evidence_r06.py
