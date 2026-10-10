#!/bin/bash
set -euo pipefail
BASE="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:?Pass the cloud workspace containing ktv_fullroom}"
for state in furnished unfurnished; do
  # Each single image owns and releases the shared lock separately.
  flock /tmp/metaxingtong-render.lock /usr/bin/blender -b -t 2 --python "$BASE/scripts/render_states.py" -- "$WORKSPACE" "$state" > "$BASE/logs/render_$state.log" 2>&1
done
