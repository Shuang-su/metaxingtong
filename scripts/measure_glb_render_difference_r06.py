"""Non-acceptance pixel diagnostic for the actual same-rig GLB render pair."""
import json
from pathlib import Path
import numpy as np
from PIL import Image

Q = Path(__file__).resolve().parents[1] / 'stages/r06-review-candidate/qa/glb-render'
a = np.asarray(Image.open(Q / 'native-same-rig.png').convert('RGB'), dtype=np.int16)
b = np.asarray(Image.open(Q / 'actual-glb-import-same-rig.png').convert('RGB'), dtype=np.int16)
assert a.shape == b.shape
d = np.abs(a - b)
p = Q / 'report.json'
j = json.loads(p.read_text())
j['encoded_RGB_pixel_difference_diagnostic'] = {
    'mean_absolute_channel_0_255': float(d.mean()),
    'p99_absolute_channel_0_255': float(np.quantile(d, .99)),
    'max_absolute_channel_0_255': int(d.max()),
    'fraction_pixels_any_channel_above_8': float((d.max(axis=2) > 8).mean()),
    'interpretation': 'Not an acceptance threshold. Float/triangulation/normal/render differences '
                      'and low-sample noise remain. Images must be reviewed side by side.'}
p.write_text(json.dumps(j, indent=2))
print(j['encoded_RGB_pixel_difference_diagnostic'])
