"""Register limited edit supports to each original pose, without generating images."""
from pathlib import Path
import argparse, hashlib, json
import cv2 as cv
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
SHOT = HERE.parent

def frame(path, index):
    with Image.open(path) as im:
        im.seek(index - 1)
        return np.array(im.convert('RGB'))

def register(source, target):
    detector = cv.SIFT_create(nfeatures=4000)
    region = np.zeros(source.shape[:2], np.uint8)
    region[30:530, :570] = 255
    k1, d1 = detector.detectAndCompute(cv.cvtColor(source, cv.COLOR_RGB2GRAY), region)
    k2, d2 = detector.detectAndCompute(cv.cvtColor(target, cv.COLOR_RGB2GRAY), None)
    matches = [m for m, n in cv.BFMatcher().knnMatch(d1, d2, k=2) if m.distance < .72 * n.distance]
    a = np.float32([k1[m.queryIdx].pt for m in matches])
    b = np.float32([k2[m.trainIdx].pt for m in matches])
    matrix, inside = cv.estimateAffinePartial2D(a, b, method=cv.RANSAC, ransacReprojThreshold=3)
    assert matrix is not None and inside.sum() >= 15
    error = np.linalg.norm(cv.transform(a[:, None], matrix)[:, 0] - b, axis=1)[inside[:, 0] > 0]
    return matrix, {'inliers': int(inside.sum()), 'median_residual_px': float(np.median(error))}

def protect_face(a):
    r, g, b = a.astype('int16').transpose(2, 0, 1)
    skin = np.uint8((r - g > 10) & (g - b > 0) & (r > 180) & (g > 100))
    _, labels, stats, _ = cv.connectedComponentsWithStats(skin)
    face = np.uint8(labels == 1 + np.argmax(stats[1:, 4]))
    return cv.dilate(face, np.ones((3, 3), np.uint8)) > 0

def ornament_anchors(a):
    r, g, b = a.astype('int16').transpose(2, 0, 1)
    blue = np.uint8((b - r > 35) & (g - r > 10) & (b > 170))
    blue[330:] = 0; blue[:, :430] = 0
    _, _, stats, centers = cv.connectedComponentsWithStats(blue)
    parts = sorted([(s[4], c) for s, c in zip(stats[1:], centers[1:]) if s[4] > 100], reverse=True, key=lambda v: v[0])
    assert len(parts) >= 2
    return np.array([parts[0][1], parts[1][1]])

def ornament_mapping(source, target):
    a, b = ornament_anchors(source), ornament_anchors(target)
    da, db = a[1] - a[0], b[1] - b[0]
    z = complex(*db) / complex(*da)
    rot = np.array([[z.real, -z.imag], [z.imag, z.real]])
    return np.column_stack((rot, b[0] - rot @ a[0]))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('frames', type=int, nargs='+')
    args = parser.parse_args()
    out = HERE / 'keys'; out.mkdir(exist_ok=True)
    original = SHOT / 'versions/01-original/master.gif'
    base = frame(original, 17)
    body = 255 - np.array(Image.open(HERE / 'sources/mask-17-1024.png').getchannel('A').resize((768, 768), Image.Resampling.NEAREST))
    ornament = 255 - np.array(Image.open(HERE / 'sources/mask-17-mascot-removal-1024.png').getchannel('A').resize((768, 768), Image.Resampling.NEAREST))
    report_path = out / 'prepared-keys.json'
    report = json.loads(report_path.read_text()) if report_path.exists() else {}
    for i in args.frames:
        target = frame(original, i)
        try:
            matrix, registration = register(base, target)
        except AssertionError:
            middle = frame(original, 25)
            first, r1 = register(base, middle)
            second, r2 = register(middle, target)
            matrix = (np.vstack([second, [0, 0, 1.]]) @ np.vstack([first, [0, 0, 1.]]))[:2]
            registration = {'via_frame': 25, 'inliers': min(r1['inliers'], r2['inliers']),
                            'median_residual_px': r1['median_residual_px'] + r2['median_residual_px']}
        body_mask = cv.warpAffine(body, matrix, (768, 768), flags=cv.INTER_NEAREST)
        # Sleeves extend naturally to the bottom; do not leave a truncated patch.
        body_mask = cv.dilate(body_mask, np.ones((25, 25), np.uint8))
        body_mask = np.maximum.accumulate(body_mask, axis=0)
        body_mask = np.maximum.accumulate(body_mask[:, ::-1], axis=1)[:, ::-1]
        body_mask[protect_face(target)] = 0
        ornament_matrix = ornament_mapping(base, target)
        ornament_mask = cv.warpAffine(ornament, ornament_matrix, (768, 768), flags=cv.INTER_NEAREST)
        ornament_mask = cv.dilate(ornament_mask, np.ones((9, 9), np.uint8))
        opened = np.maximum(body_mask, ornament_mask)
        for name, arr in [('body', body_mask), ('ornament', ornament_mask), ('support', opened)]:
            Image.fromarray(arr).save(out / f'{i:02}-{name}-768.png')
        mask = Image.new('RGBA', (1024, 1024), (255, 255, 255, 255))
        mask.putalpha(Image.fromarray(255 - opened).resize((1024, 1024), Image.Resampling.NEAREST))
        mask.save(out / f'{i:02}-mask-1024.png')
        for name, arr in [('original', target), ('nailu', frame(SHOT.parent / '10-pout/master.gif', i))]:
            Image.fromarray(arr).resize((1024, 1024), Image.Resampling.LANCZOS).save(out / f'{i:02}-{name}-1024.png')
        weight = opened.astype('float32') / 255 * .4
        tint = np.full_like(target, [255, 45, 65])
        review = np.uint8(np.rint(target * (1 - weight[..., None]) + tint * weight[..., None]))
        Image.fromarray(review).save(out / f'{i:02}-mask-review.png')
        text = (HERE / 'frame17-prompt.txt').read_text().split('The unwanted blue-white')[0]
        text += ('\nImage 3 is the approved local repair of Xingtong at frame 17, used only for consistent cuff, hand, choker and fur design. '
                 'Keep those details and line weight consistent while fitting the ORIGINAL pose and anatomy of image 1. '
                 'Inside the separate upper-right open area, remove the complete blue-white animal mascot, paws and ears from the headband. '
                 'Reconstruct the continuous purple headband, silver hair and white background beneath it. Do not add any ornament. '
                 'Preserve all unmasked head and face pixels. The head may tilt while the complete sleeve-and-fist units compensate independently. '
                 'The neck stays short and continuous, with no hair crossing its front. Keep the shoulders relaxed, the fists close to the lower cheeks, '
                 'and complete sleeves continuing to the lower canvas edge. Return a 1024x1024 PNG of image 1.\n')
        (out / f'{i:02}-prompt.txt').write_text(text)
        job = {'name': f'frame{i:02}-neck-fists-and-ornament-r1',
               'images': [f'keys/{i:02}-original-1024.png', f'keys/{i:02}-nailu-1024.png', 'keys/17-clean-1024.png'],
               'mask': f'keys/{i:02}-mask-1024.png', 'prompt': f'keys/{i:02}-prompt.txt', 'output': f'keys/{i:02}-api.png'}
        (out / f'{i:02}-job.json').write_text(json.dumps(job, indent=2) + '\n')
        report[str(i)] = {'original17_to_frame': matrix.tolist(), 'ornament_matrix': ornament_matrix.tolist(), **registration,
                          'editable_pixels_768': int((opened > 0).sum()), 'original_rgb_sha256': hashlib.sha256(target.tobytes()).hexdigest()}
    (out / 'prepared-keys.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
