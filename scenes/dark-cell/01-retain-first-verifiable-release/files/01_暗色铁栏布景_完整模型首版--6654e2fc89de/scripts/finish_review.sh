#!/bin/bash
set -e
python dark_cell_v1/scripts/denoise.py dark_cell_v1/renders/08_门铰链近景_white.png
python - <<'PY'
from pathlib import Path
import hashlib,json
R=Path('dark_cell_v1');p=R/'qa/render_manifest.json';a=json.loads(p.read_text());a=[x for x in a if not(x['variant']=='white' and x['view']=='08_门铰链近景')];a.append({'variant':'white','view':'08_门铰链近景','model_sha256':hashlib.sha256((R/'models/dark_cell_white.blend').read_bytes()).hexdigest(),'render_sha256':hashlib.sha256((R/'renders/08_门铰链近景_white.png').read_bytes()).hexdigest(),'supplement':'同机位白模补充五金检查'});p.write_text(json.dumps(a,ensure_ascii=False,indent=2))
PY
python dark_cell_v1/scripts/build_review.py
