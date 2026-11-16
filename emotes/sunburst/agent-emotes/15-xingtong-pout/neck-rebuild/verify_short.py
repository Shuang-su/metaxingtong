"""Independently decode deliveries and verify timing, source preservation and checksums."""
from pathlib import Path
import hashlib, json, subprocess
import numpy as np
from PIL import Image
from prepare_keys import frame

HERE = Path(__file__).resolve().parent
OUT = HERE / 'short-review'

def main():
    plan = json.loads((OUT / 'construction.json').read_text())
    results = {}
    for name, size in [('candidate-768.gif', (768, 768)), ('candidate-320.gif', (320, 320)),
                       ('candidate-112.gif', (112, 112)), ('comparison-320.gif', (960, 320))]:
        path = OUT / name; pixels = hashlib.sha256(); durations = []; unique = set()
        with Image.open(path) as gif:
            assert gif.size == size and gif.n_frames == 15 and gif.info['loop'] == 0
            for j in range(gif.n_frames):
                gif.seek(j); a = np.array(gif.convert('RGB')); raw = a.tobytes()
                durations.append(gif.info['duration']); pixels.update(raw); unique.add(hashlib.sha256(raw).hexdigest())
                if name == 'candidate-768.gif':
                    original = frame(HERE.parent / 'versions/01-original/master.gif', j + 11)
                    allowed = np.array(Image.open(OUT / f'allowed-{j+11:02}.png')) > 0
                    assert np.array_equal(a[~allowed], original[~allowed]), ('GIF protected area changed', j+11)
                    assert np.array_equal(a[320:540, 100:560], original[320:540, 100:560])
                    png = np.array(Image.open(OUT / f'frame-{j+11:02}.png'))
                    assert np.array_equal(png[~allowed], original[~allowed])
        assert durations == plan['durations_ms'] and sum(durations) == 1300
        process = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True)
        ffmpeg_hash = hashlib.sha256(process.stdout).hexdigest()
        assert ffmpeg_hash == pixels.hexdigest(), name
        results[name] = {'size': list(size), 'frames': 15, 'duration_ms': sum(durations), 'loop': 0,
                         'unique_frames': len(unique), 'decoded_rgb_sha256': pixels.hexdigest(),
                         'ffmpeg_rgb_sha256': ffmpeg_hash, 'file_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    report = {'status': 'passed', 'scope': 'technical checks only; visual acceptance remains separate',
              'native_gif_changed_protected_pixels': 0, 'native_png_changed_protected_pixels': 0,
              'eye_roi_changed_pixels': 0, 'timelines_match_original_F11_F25': True,
              'decoders': ['Pillow', 'FFmpeg'], 'outputs': results}
    (OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
