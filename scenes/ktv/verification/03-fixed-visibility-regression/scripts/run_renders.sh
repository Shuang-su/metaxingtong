#!/usr/bin/env bash
set -euo pipefail
cd /workspace/scratch/fa58bfcf0425
R=ktv_fixed_visibility_20261010
for view in Empty_Stage Telescope_Detail; do
  for pair in 'legacy historical_hidden' 'legacy fixed' 'current fixed' 'current_white fixed'; do
    read -r model state <<< "$pair"
    tag="${model}_${view}_${state}"
    flock /tmp/metaxingtong-render.lock /usr/bin/blender -b -t 2 --python "$R/scripts/render_regression.py" -- "$model" "$view" "$state" > "$R/logs/$tag.log" 2>&1
    echo "$tag complete"
  done
done
