from pathlib import Path
import json,difflib
r=Path('/workspace/shared/ferris-cabin-build-20261030/scenes/ferris-wheel-cabin');p=r/'scripts/strict_aperture_audit.py';old=p.read_text();poly=json.loads((r/'qa/r09/shared-width-dependencies.json').read_text())['poly'];new=old.replace(old.splitlines()[7],old.splitlines()[7])
start=new.index('POLY=');end=new.index('\n',start);new=new[:start]+'POLY='+repr([tuple(x) for x in poly])+new[end:]
lo=min(x[0] for x in poly);hi=max(x[0] for x in poly)
new=new.replace('x=-1.62+3.24*(j+.5)/100;',f'x={lo!r}+{hi-lo!r}*(j+.5)/100;')
new=new.replace("['ferris_cabin_material.blend','ferris_cabin_r06_material.blend']","['ferris_cabin_r09_material.blend']").replace('qa/strict-aperture-audit.json','qa/strict-aperture-audit-r09.json')
new=new.replace("report={'method':", "report={'r09_sampling_note':'Polygon and slab x bounds updated to actual expanded R09 footprint. Same 100x120 samples per wall, 100x100 slab grid before polygon filtering, 8192 isotropic directions. World sample coordinates differ; polygon-filtered sample count can differ. Aperture and structural filters unchanged.','method':")
(r/'scripts/strict_aperture_audit_r09.py').write_text(new)
(r/'qa/strict-aperture-audit-r09-script.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='strict_aperture_audit.py',tofile='strict_aperture_audit_r09.py')))
