#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(git rev-parse --show-toplevel)"
asset_dir="$repo_dir/emotes/sunburst/agent-emotes/15-xingtong-pout/neck-follow"
venv_dir="${RUNNER_TEMP:-/tmp}/pout-neck-follow-venv"
python3 -m venv "$venv_dir"
"$venv_dir/bin/pip" install -r "$asset_dir/requirements.txt"
cp "$asset_dir/SHA256SUMS" "$venv_dir/expected-sha256sums"
cd "$repo_dir"
"$venv_dir/bin/python" docs/changes/20261108-pout-neck-follow/verify_inputs.py > docs/changes/20261108-pout-neck-follow/cloud-input.json
"$venv_dir/bin/python" "$asset_dir/generate.py"
"$venv_dir/bin/python" "$asset_dir/verify.py"
cmp "$venv_dir/expected-sha256sums" "$asset_dir/SHA256SUMS"
(cd "$asset_dir" && sha256sum -c SHA256SUMS)
