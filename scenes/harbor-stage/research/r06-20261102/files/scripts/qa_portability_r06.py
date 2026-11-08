"""Open byte-identical originals in an isolated temporary directory with no adjacent textures."""
import bpy, hashlib, json, shutil, tempfile
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'stages/r06-review-candidate'
rows = []
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='harbor-r06-portable-') as directory:
    isolated = Path(directory)
    for state in ('white', 'material'):
        source = O / ('harbor-r06-' + state + '.blend')
        target = isolated / source.name
        shutil.copyfile(source, target)
        assert sha(source) == sha(target)
        bpy.ops.wm.open_mainfile(filepath=str(target))
        mesh_count = sum(ob.type == 'MESH' for ob in bpy.context.scene.objects)
        assert mesh_count == 394
        images = []
        for im in bpy.data.images:
            if im.type != 'IMAGE':
                continue
            dimensions = list(im.size)
            assert im.packed_file is not None, im.name
            assert len(im.pixels) > 0 and min(dimensions) > 0, im.name
            images.append({'name': im.name, 'dimensions': dimensions,
                           'packed_bytes': len(im.packed_file.data),
                           'packed_sha256': hashlib.sha256(im.packed_file.data).hexdigest(),
                           'pixel_buffer_decoded': True})
        rows.append({'state': state, 'file': source.name, 'bytes': source.stat().st_size,
                     'sha256': sha(source), 'temporary_copy_exact': True,
                     'opened_from_isolated_directory': True, 'mesh_count': mesh_count,
                     'images': images})
report = {'blender': bpy.app.version_string, 'checks': rows,
          'scope': 'Native files load and packed image buffers decode without adjacent texture files. '
                   'The temporary directory is not an OS filesystem isolation sandbox; packed payload presence and '
                   'decode are explicitly checked. Does not claim portability of Blender lights/world through GLB.'}
(O / 'qa/native-portability.json').write_text(json.dumps(report, indent=2))
print('NATIVE_PORTABILITY_VERIFIED', len(rows))
