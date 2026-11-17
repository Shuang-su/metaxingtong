"""Decode both API sources and deliveries, verify provenance and complete-frame assembly."""
from collections import Counter
from pathlib import Path
import hashlib, json, subprocess
import numpy as np
from PIL import Image
from prepare_design import white

HERE = Path(__file__).resolve().parent
OUT = HERE / 'delivery'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    inventory = json.loads((HERE / 'source-records.json').read_text())
    for name, record in inventory['inputs'].items():
        assert sha(HERE / 'sources' / name) == record['sha256'], name
    manifest = json.loads((OUT / 'manifest.json').read_text()); margin = manifest['uniform_crop_each_edge_px']
    kind = Counter(); descriptors = set()
    # Compare each output PNG with its entire source drawing, without importing production rendering helpers.
    for row in manifest['frame_review']:
        source = row['source']; descriptors.add(json.dumps(source, sort_keys=True))
        if 'key' in source:
            kind['native_keys'] += 1
            with Image.open(HERE / 'sources/native-nine-r1.gif') as gif:
                gif.seek(source['key']-1); source_image = white(gif)
        else:
            kind['drawn_inbetweens'] += 1
            number = int(source['sheet'].split('-')[-1]); cell = source['cell']-1
            source_image = white(Image.open(HERE / f'sources/sheet-{number}-r1.png'))
            x, y = cell % 3*512, cell // 3*512; source_image = source_image.crop((x, y, x+512, y+512))
        expected = np.array(source_image.crop((margin, margin, 512-margin, 512-margin)))
        actual = np.array(Image.open(OUT / f'frame-{row["frame"]:02}.png'))
        assert np.array_equal(expected, actual), row['frame']
        assert hashlib.sha256(actual.tobytes()).hexdigest() == row['rgb_sha256']
    assert kind == {'native_keys': 9, 'drawn_inbetweens': 45} and len(descriptors) == 54
    outputs = {}
    for name, size in [('master-512.gif', (512, 512)), ('master.gif', (768, 768)), ('chat.gif', (320, 320)),
                       ('review-112.gif', (112, 112)), ('paired.gif', (640, 320))]:
        path = OUT / name; pixels = hashlib.sha256(); times = []; unique = set(); colors = set(); corners = []
        with Image.open(path) as gif:
            assert gif.format == 'GIF' and gif.size == size and gif.n_frames == 54 and gif.info['loop'] == 0
            for i in range(54):
                gif.seek(i); im = gif.convert('RGB'); raw = im.tobytes(); pixels.update(raw)
                times.append(gif.info['duration']); unique.add(hashlib.sha256(raw).hexdigest())
                colors.update(color for _, color in im.getcolors(maxcolors=256))
                corners.append(im.getpixel((0, 0)))
        assert times == manifest['durations_ms'] and sum(times) == 4560
        assert len(unique) == 54 and len(colors) <= 256
        assert all(min(corner) >= 250 for corner in corners)
        assert any(b-r > 30 and g-r > 10 and r < 160 for r, g, b in colors), ('Blue irises missing from palette', name)
        other = hashlib.sha256()
        process = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', str(path), '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while chunk := process.stdout.read(1024*1024):
            other.update(chunk)
        error = process.stderr.read(); assert process.wait() == 0, error.decode(errors='replace')
        assert other.hexdigest() == pixels.hexdigest(), name
        outputs[name] = {'size': list(size), 'frames': 54, 'unique_frames': len(unique), 'duration_ms': sum(times),
                         'palette_colors_across_animation': len(colors), 'loop': 0, 'sha256': sha(path),
                         'pillow_rgb_sha256': pixels.hexdigest(), 'ffmpeg_rgb_sha256': other.hexdigest()}
    receipts = sorted((HERE / 'sources').glob('*.receipt.json')); assert len(receipts) == 7
    for path in receipts:
        receipt = json.loads(path.read_text()); assert receipt['status'] == 'completed'
        for name, digest in receipt['inputs'].items():
            assert sha(HERE / name) == digest, name
        assert sha(HERE / receipt['output']) == receipt['output_sha256']
    with Image.open(HERE / 'sources/native-nine-r1.gif') as gif:
        assert gif.size == (512, 512) and gif.n_frames == 9 and gif.info['loop'] == 0
        times = []
        for i in range(9):
            gif.seek(i); times.append(gif.info['duration'])
        assert times == [200]*9
    with Image.open(OUT/'chat.gif') as chat, Image.open(OUT/'paired.gif') as paired:
        a = np.array(chat.convert('RGB')).astype('int16')
        b = np.array(paired.convert('RGB'))[:, 320:].astype('int16')
        r, g, blue = a.transpose(2, 0, 1)
        eye = (blue-r > 30) & (g-r > 10) & (r < 160)
        eye[:100] = False; eye[240:] = False; eye[:, :65] = False; eye[:, 260:] = False
        mean = b[eye].mean(axis=0)
        assert eye.sum() > 300 and mean[1] > mean[0]+5 and mean[2] > mean[1]+20, ('Comparison iris color shifted', mean)
    report = {'status': 'passed', 'complete_drawing_sources': dict(kind), 'unique_source_drawings': 54,
              'verified_original_source_files': len(inventory['inputs']),
              'whole_frame_png_source_match': True, 'verified_API_receipts': len(receipts), 'automatic_API_retries': 0,
              'comparison_preserves_blue_irises': True,
              'timings_equal_Nailu_exposure_sheet': True, 'decoders': ['Pillow', 'FFmpeg'], 'outputs': outputs,
              'scope': 'Technical/provenance checks. Visual review is separate; matching palette and hashes does not prove animation quality.'}
    (OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
