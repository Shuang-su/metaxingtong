"""Verify the full candidate's two decoders, source timeline and allowed edits."""
from pathlib import Path
import hashlib, json, subprocess
import numpy as np
from PIL import Image
from prepare_keys import frame

HERE = Path(__file__).resolve().parent
OUT = HERE / 'full-review'

def main():
    plan = json.loads((OUT / 'construction.json').read_text()); results = {}
    for name, size in [('master.gif', (768, 768)), ('chat.gif', (320, 320)), ('paired.gif', (640, 320)),
                       ('review-112.gif', (112, 112)), ('comparison.gif', (960, 320))]:
        path = OUT / name; pixels = hashlib.sha256(); durations = []; unique = set()
        with Image.open(path) as gif:
            assert gif.size == size and gif.n_frames == 54 and gif.info['loop'] == 0
            for j in range(54):
                gif.seek(j); a = np.array(gif.convert('RGB')); raw = a.tobytes()
                pixels.update(raw); unique.add(hashlib.sha256(raw).hexdigest()); durations.append(gif.info['duration'])
                if name == 'master.gif':
                    original = frame(HERE.parent / 'versions/01-original/master.gif', j+1)
                    support = np.array(Image.open(OUT / f'allowed-{j+1:02}.png')) > 0
                    assert np.array_equal(a[~support], original[~support]), ('protected GIF pixels changed', j+1)
                    assert np.array_equal(a[320:540, 100:560], original[320:540, 100:560]), ('eye ROI changed', j+1)
                    png = np.array(Image.open(OUT / f'frame-{j+1:02}.png'))
                    assert np.array_equal(png[~support], original[~support]), ('protected PNG pixels changed', j+1)
        assert durations == plan['durations_ms'] and sum(durations) == 4560
        process = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True)
        other = hashlib.sha256(process.stdout).hexdigest(); assert other == pixels.hexdigest(), name
        results[name] = {'size': list(size), 'frames': 54, 'duration_ms': sum(durations), 'loop': 0,
                         'unique_frames': len(unique), 'decoded_rgb_sha256': pixels.hexdigest(), 'ffmpeg_rgb_sha256': other,
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    archive_map = json.loads((HERE / 'keys/input-archives/input-version-map.json').read_text())
    aliases = {value['sha256']: HERE / value['archive'] for value in archive_map.values()}
    receipts = [HERE / 'frame17-api-receipt.json', *sorted((HERE / 'keys').glob('*.receipt.json'))]
    for path in receipts:
        receipt = json.loads(path.read_text()); assert receipt['status'] == 'completed'
        for name, digest in receipt['inputs'].items():
            original_path = HERE / ('sources/' + name if path.name == 'frame17-api-receipt.json' else name)
            if not original_path.exists() or hashlib.sha256(original_path.read_bytes()).hexdigest() != digest:
                original_path = aliases[digest]
            assert hashlib.sha256(original_path.read_bytes()).hexdigest() == digest
        png_path = HERE / receipt.get('output', receipt.get('output_file'))
        assert hashlib.sha256(png_path.read_bytes()).hexdigest() == receipt['output_sha256']
        with Image.open(png_path) as im:
            im.load(); assert im.format == 'PNG' and im.size == (1024, 1024)
    report = {'status': 'passed', 'scope': 'Technical checks; user visual acceptance remains separate.',
              'source_timeline_equal': True, 'protected_native_png_changes': 0, 'protected_native_gif_changes': 0,
              'eye_roi_changes': 0, 'decoders': ['Pillow', 'FFmpeg'], 'verified_API_receipts': len(receipts), 'outputs': results}
    (OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
