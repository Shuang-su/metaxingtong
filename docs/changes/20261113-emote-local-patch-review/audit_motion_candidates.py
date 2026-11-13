#!/usr/bin/env python3
"""Audit delivered GIF bytes, independent of the patch construction code."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import csv, hashlib, json
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
DOC = Path(__file__).resolve().parent
SELECTION = {'02-butterfly': 'dynamic-candidate', '03-awake': 'dynamic-candidate-r1'}
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_gif(path):
    frames, durations = [], []
    with Image.open(path) as gif:
        loop = gif.info.get('loop')
        for n in range(gif.n_frames):
            gif.seek(n)
            frames.append(gif.convert('RGB'))
            durations.append(gif.info['duration'])
    return frames, durations, loop

def main():
    original_files = json.loads((ROOT/'handoff-manifest.json').read_text())['files']
    for item in original_files:
        p = ROOT/item['path']
        assert p.stat().st_size == item['size'] and sha(p) == item['sha256'], p
    result = {'source_snapshot_files_verified': len(original_files),
              'original_snapshot_unchanged': True,
              'browser_runtime_playback': 'unverified; previous ERR_BLOCKED_BY_ADMINISTRATOR route not retried',
              'pixel_guarantee_scope': '768px master only; 112px and side-by-side GIFs are resampled display derivatives',
              'emotes': {}}
    audit_rows = []
    for name, version in SELECTION.items():
        source = ROOT/'emotes/sunburst/agent-emotes'/name
        base = source/'versions/20261113-local-patch-review'
        out = base/'v6-contour-and-motion'/version
        expected = json.loads((source/'manifest.json').read_text())['frame_durations_ms']
        originals, original_durations, _ = read_gif(source/'master.gif')
        assert original_durations == expected
        actual, durations, loop = read_gif(out/'CANDIDATE-master-768.gif')
        assert durations == expected and loop == 0
        files = {}
        for fname, size in [('CANDIDATE-master-768.gif',(768,768)),
                            ('CANDIDATE-preview-112.gif',(112,112)),
                            ('comparison-motion-320.gif',(640,344))]:
            frames, times, gif_loop = read_gif(out/fname)
            assert times == expected and len(frames) == len(expected)
            assert gif_loop == 0 and all(frame.size == size for frame in frames)
            files[fname] = {'size': list(size), 'bytes': (out/fname).stat().st_size,
                           'sha256': sha(out/fname), 'frame_count': len(frames),
                           'duration_ms': sum(times), 'every_frame_duration_matches': True,
                           'loop': gif_loop}
        changed_frames = []
        for i, (original, candidate) in enumerate(zip(originals, actual), 1):
            mask_path = out/f'allowed-mask-{i:02d}.png'
            mask = np.array(Image.open(mask_path)) > 0 if mask_path.exists() else np.zeros((768,768),bool)
            protected_path = out/f'protected-{i:02d}.png'
            protected = np.array(Image.open(protected_path)) > 0 if protected_path.exists() else np.zeros((768,768),bool)
            diff = np.any(np.array(original) != np.array(candidate), axis=-1)
            outside = int((diff & ~mask).sum())
            protected_changes = int((diff & protected).sum())
            assert outside == 0 and protected_changes == 0
            if diff.any(): changed_frames.append(i)
            audit_rows.append({'emote': name, 'frame': i, 'duration_ms': expected[i-1],
                               'changed_pixels': int(diff.sum()), 'allowed_pixels': int(mask.sum()),
                               'outside_mask_changes': outside, 'protected_region_changes': protected_changes,
                               'original_rgb_sha256': hashlib.sha256(original.tobytes()).hexdigest(),
                               'candidate_rgb_sha256': hashlib.sha256(candidate.tobytes()).hexdigest()})
        assert changed_frames == (list(range(24,29)) if name == '02-butterfly' else list(range(1,34)))
        # This sheet uses bytes decoded from the delivered 112px GIF, not an
        # unencoded resize. Each candidate tile is exactly 112 by 112 pixels.
        preview, _, _ = read_gif(out/'CANDIDATE-preview-112.gif')
        ids = list(range(23,30)) if name == '02-butterfly' else list(range(1,35))
        cols = 4; tw, th = 224, 134
        sheet = Image.new('RGB',(cols*tw, ((len(ids)+cols-1)//cols)*th),'#eee')
        d = ImageDraw.Draw(sheet)
        for k, n in enumerate(ids):
            x, y = k%cols*tw, k//cols*th
            d.text((x+2,y+3),f'F{n}: original | GIF candidate',fill='black',font=FONT)
            sheet.paste(originals[n-1].resize((112,112),Image.Resampling.LANCZOS),(x,y+22))
            sheet.paste(preview[n-1],(x+112,y+22))
        sheet.save(out/'comparison-decoded-112.png')
        result['emotes'][name] = {'selected_version': version,
                                 'original_master_sha256': sha(source/'master.gif'),
                                 'files': files, 'changed_frames': changed_frames,
                                 'changed_frames_duration_ms': sum(expected[i-1] for i in changed_frames),
                                 'outside_mask_changes': 0, 'protected_region_changes': 0,
                                 'unaltered_frames': len(expected)-len(changed_frames)}
    with (DOC/'v6-frame-audit.csv').open('w') as f:
        writer = csv.DictWriter(f,fieldnames=list(audit_rows[0]));writer.writeheader();writer.writerows(audit_rows)
    (DOC/'v6-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
