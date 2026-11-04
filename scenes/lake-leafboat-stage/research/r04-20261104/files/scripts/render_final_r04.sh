#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2
mkdir -p qa/r04 renders/r04/source renders/r04/checks renders/r04/main renders/r04/white
/usr/bin/blender -b -t 1 --python scripts/verify_delivery.py -- r04 > qa/verify-r04.log 2>&1
/usr/bin/blender -b models/lakeleaf-r04-material.blend -t 2 --python scripts/render_cameras.py -- --output renders/r04/source --cameras SOURCE_092142973_SIDE SOURCE_100762992_TOP SOURCE_108755584_OBLIQUE AUX_006585758_REAR --samples 16 --threads 2 --percentage 100 > qa/render-r04-source.log 2>&1
/usr/bin/blender -b models/lakeleaf-r04-material.blend -t 2 --python scripts/render_cameras.py -- --output renders/r04/checks --cameras CHECK_01 CHECK_02 CHECK_03 CHECK_04 CHECK_05 CHECK_06 CHECK_07 CHECK_08 --samples 12 --threads 2 --percentage 100 > qa/render-r04-checks.log 2>&1
/usr/bin/blender -b models/lakeleaf-r04-material.blend -t 2 --python scripts/render_cameras.py -- --output renders/r04/main --cameras HERO --samples 32 --threads 2 --percentage 100 > qa/render-r04-main.log 2>&1
/usr/bin/blender -b models/lakeleaf-r04-white.blend -t 2 --python scripts/render_cameras.py -- --output renders/r04/white --cameras HERO --samples 12 --threads 2 --percentage 100 > qa/render-r04-white.log 2>&1
python scripts/assemble_evidence.py
