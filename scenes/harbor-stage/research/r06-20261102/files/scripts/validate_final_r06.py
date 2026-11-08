"""Fail closed on missing final images, stale hashes, resized overlays, or local crop drift."""
import hashlib, json, struct
from pathlib import Path
from PIL import Image, ImageChops

R = Path(__file__).resolve().parents[1]
O = R / 'stages/r06-review-candidate'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda name: json.loads((O / name).read_text())
cfgs = read('source-cameras.json')
renders = read('render-manifest.json')
overlays = read('overlay-manifest.json')
crops = read('object-crops-manifest.json')
assert len(cfgs) == 7 and len(renders) == 32 and len(overlays) == 14 and len(crops) == 8
expected = {f'source-renders/{c["id"]}/{s}.png' for c in cfgs for s in ('white', 'material')}
expected |= {f'checks/{s}/check-{i:02d}.png' for s in ('white', 'material') for i in range(1, 9)}
expected |= {'checks/white/CHECK_LOW_CONTACT.png', 'checks/white/CHECK_ENVIRONMENT_OVERVIEW.png'}
assert set(x['output'] for x in renders) == expected
assert len({x['output'] for x in renders}) == len(renders)
for c in cfgs:
    p = R / c['file']
    assert sha(p) == c['source_sha256'] and p.stat().st_size == c['source_bytes']
    with Image.open(p) as im:
        im.load()
        assert list(im.size) == c['size']
for row in renders:
    p = O / row['output']
    assert p.stat().st_size == row['bytes'] and sha(p) == row['sha256']
    assert sha(R / row['input']) == row['input_sha256']
    with Image.open(p) as im:
        im.load()
        assert list(im.size) == row['dimensions']
for c in cfgs:
    pair = [next(x for x in renders if x['output'] == f'source-renders/{c["id"]}/{s}.png') for s in ('white', 'material')]
    assert pair[0]['camera_matrix_world'] == pair[1]['camera_matrix_world']
    assert pair[0]['lens'] == pair[1]['lens'] and pair[0]['shift'] == pair[1]['shift']
for row in overlays:
    for key in ('source', 'render', 'overlay'):
        assert sha(R / row[key]) == row[key + '_sha256']
    a, b, actual = [Image.open(R / row[k]).convert('RGB') for k in ('source', 'render', 'overlay')]
    assert a.size == b.size == actual.size == tuple(row['dimensions'])
    assert ImageChops.difference(Image.blend(a, b, .5), actual).getbbox() is None
for row in crops:
    box = row['crop_xyxy']
    source = Image.open(R / row['source']).convert('RGB').crop(box)
    actual = Image.open(R / row['source_crop']).convert('RGB')
    assert ImageChops.difference(source, actual).getbbox() is None
    assert sha(R / row['source_crop']) == row['source_crop_sha256']
    for state in ('white', 'material'):
        target = Image.open(O / f'source-renders/preview-front/{state}.png').convert('RGB').crop(box)
        for key in ('render_crop', 'overlay'):
            assert sha(R / row[state][key]) == row[state][key + '_sha256']
        actual_target = Image.open(R / row[state]['render_crop']).convert('RGB')
        actual_overlay = Image.open(R / row[state]['overlay']).convert('RGB')
        assert ImageChops.difference(target, actual_target).getbbox() is None
        assert ImageChops.difference(Image.blend(source, target, .5), actual_overlay).getbbox() is None
for state in ('white', 'material'):
    p = O / ('harbor-r06-' + state + '.glb')
    magic, version, size = struct.unpack('<4sII', p.read_bytes()[:12])
    assert magic == b'glTF' and version == 2 and size == p.stat().st_size
    assert (O / ('harbor-r06-' + state + '.blend')).read_bytes().startswith(b'BLENDER')
report = {'source_pngs_native_grid_verified': 7, 'final_render_pngs_verified': 32,
          'native_source_renders': 14, 'arbitrary_eight_angle_pairs': 8, 'extra_white_diagnostics': 2,
          'direct_overlays_pixel_exact_encoded_RGB_alpha_0_5': 14,
          'local_object_crop_groups_pixel_exact_no_resampling': 8, 'crop_png_count': 40,
          'white_material_source_camera_matrices_lenses_shifts_exact': True,
          'render_inputs_byte_hashes_verified': True,
          'geometry_source_delivery_gates_separate': True,
          'source_acceptance': 'NOT_PASSED', 'user_acceptance': 'NOT_RECEIVED',
          'remote_archive_or_issue_image_visibility': 'not tested by this local validation'}
(O / 'qa/final-artifact-validation.json').write_text(json.dumps(report, indent=2))
print('FINAL_ARTIFACT_VALIDATION_OK', json.dumps(report))
