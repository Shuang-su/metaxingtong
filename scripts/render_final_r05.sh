#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2
mkdir -p qa/r05 renders/r05/source renders/r05/checks renders/r05/main renders/r05/white renders/r05/white-source renders/r05/white-checks
/usr/bin/blender -b -t 1 --python-exit-code 10 --python scripts/verify_delivery.py -- r05 > qa/verify-r05.log 2>&1
/usr/bin/blender -b -t 1 --python-exit-code 10 --python scripts/restore_glb_cameras_r05.py > qa/restore-glb-cameras-r05.log 2>&1
/usr/bin/blender -b -t 1 --python-exit-code 10 --python scripts/verify_camera_export_r05.py > qa/verify-camera-r05.log 2>&1
/usr/bin/blender -b -t 1 --python-exit-code 10 --python scripts/verify_restored_cameras_r05.py > qa/verify-restored-cameras-r05.log 2>&1
python scripts/verify_r05_diff.py
/usr/bin/blender -b models/lakeleaf-r05-material.blend -t 2 --python-exit-code 10 --python scripts/render_cameras.py -- --output renders/r05/source --cameras SOURCE_092142973_SIDE SOURCE_100762992_TOP SOURCE_108755584_OBLIQUE AUX_006585758_REAR --samples 16 --threads 2 --percentage 100 > qa/render-r05-source.log 2>&1
/usr/bin/blender -b models/lakeleaf-r05-material.blend -t 2 --python-exit-code 10 --python scripts/render_cameras.py -- --output renders/r05/checks --cameras CHECK_01 CHECK_02 CHECK_03 CHECK_04 CHECK_05 CHECK_06 CHECK_07 CHECK_08 --samples 12 --threads 2 --percentage 100 > qa/render-r05-checks.log 2>&1
/usr/bin/blender -b models/lakeleaf-r05-material.blend -t 2 --python-exit-code 10 --python scripts/render_cameras.py -- --output renders/r05/main --cameras HERO --samples 32 --threads 2 --percentage 100 > qa/render-r05-main.log 2>&1
/usr/bin/blender -b models/lakeleaf-r05-white.blend -t 2 --python-exit-code 10 --python scripts/render_cameras.py -- --output renders/r05/white --cameras HERO --samples 12 --threads 2 --percentage 100 > qa/render-r05-white.log 2>&1
python scripts/assemble_evidence_r05.py
/usr/bin/blender -b models/lakeleaf-r05-white.blend -t 2 --python-exit-code 10 --python scripts/render_cameras.py -- --output renders/r05/white-source --cameras SOURCE_092142973_SIDE SOURCE_100762992_TOP SOURCE_108755584_OBLIQUE AUX_006585758_REAR --samples 16 --threads 2 --percentage 100 > qa/render-r05-white-source.log 2>&1
/usr/bin/blender -b models/lakeleaf-r05-white.blend -t 2 --python-exit-code 10 --python scripts/render_cameras.py -- --output renders/r05/white-checks --cameras CHECK_01 CHECK_02 CHECK_03 CHECK_04 CHECK_05 CHECK_06 CHECK_07 CHECK_08 --samples 12 --threads 2 --percentage 100 > qa/render-r05-white-checks.log 2>&1
python scripts/assemble_white_evidence_r05.py
