"""Composite API edits on their original frame and flatten PNG transparency correctly."""
from pathlib import Path
import argparse, json, hashlib
import cv2 as cv
import numpy as np
from PIL import Image
from prepare_keys import frame, register
from prepare_keys import protect_face

HERE = Path(__file__).resolve().parent

def white_rgb(path):
    rgba = Image.open(path).convert('RGBA')
    white = Image.new('RGBA', rgba.size, 'white')
    white.alpha_composite(rgba)
    return white.convert('RGB')

def inset_weight(support):
    distance = cv.distanceTransform(np.uint8(support > 0), cv.DIST_L2, 5)
    t = np.clip(distance / 4., 0, 1)
    return t * t * (3 - 2 * t)

def aligned(image, base):
    source = np.array(image.resize((768, 768), Image.Resampling.LANCZOS))
    target = np.array(base.resize((768, 768), Image.Resampling.LANCZOS))
    matrix, report = register(source, target)
    matrix[:, 2] *= 1024 / 768
    result = cv.warpAffine(np.array(image), matrix, (1024, 1024), flags=cv.INTER_CUBIC, borderValue=(255, 255, 255))
    return Image.fromarray(result), {'matrix_1024': matrix.tolist(), **report}

def contact_warp(image, original):
    """Use the two actual jaw profiles to fit the lower drawing to the protected face."""
    donor = np.array(image.resize((768, 768), Image.Resampling.LANCZOS))
    faces = [protect_face(a) for a in (original, donor)]
    xs = np.arange(170, 481, 10)
    profiles = []
    for face in faces:
        profiles.append(np.array([np.where(face[:, x])[0][-1] if face[:, x].any() else np.nan for x in xs]))
    good = np.isfinite(profiles[0]) & np.isfinite(profiles[1])
    shift = np.interp(np.arange(768), xs[good], (profiles[0] - profiles[1])[good])
    shift = cv.GaussianBlur(shift[None].astype('float32'), (0, 0), 14)[0]
    shift = np.clip(shift, 0, 50)
    y, x = np.mgrid[:768, :768].astype('float32')
    warped = cv.remap(donor, x, y - shift[None], cv.INTER_CUBIC, borderMode=cv.BORDER_REPLICATE)
    return Image.fromarray(warped).resize((1024, 1024), Image.Resampling.LANCZOS), {'jaw_profile_displacement_x170_480': shift[170:481:10].tolist()}

def hand_matte(image):
    r, g, b = image.astype('int16').transpose(2, 0, 1)
    skin = np.uint8((r - g > 7) & (g - b > -3) & (r > 165) & (g > 95))
    _, labels, stats, centers = cv.connectedComponentsWithStats(skin)
    matte = np.zeros(skin.shape, np.uint8)
    candidates = [(int(s[4]), j, c) for j, (s, c) in enumerate(zip(stats[1:], centers[1:]), 1)
                  if 3000 < s[4] < 14000 and s[1] > 530 and c[1] > 590]
    selected = []
    for side in [lambda c: c[0] < 300, lambda c: c[0] >= 300]:
        choices = [v for v in candidates if side(v[2])]
        assert choices, candidates
        selected.append(max(choices, key=lambda v: v[0])[1])
    for label in selected:
        component = np.uint8(labels == label) * 255
        component = cv.morphologyEx(component, cv.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        contours, _ = cv.findContours(component, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        cv.drawContours(component, contours, -1, 255, cv.FILLED)
        matte = np.maximum(matte, cv.dilate(component, np.ones((5, 5), np.uint8)))
    return matte

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('frames', type=int, nargs='+'); args = parser.parse_args()
    report = {}
    for i in args.frames:
        original = frame(HERE.parent / 'versions/01-original/master.gif', i)
        support = np.array(Image.open(HERE / f'keys/{i:02}-support-768.png'))
        face = np.uint8(protect_face(original)) * 255
        face = cv.morphologyEx(face, cv.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        contours, _ = cv.findContours(face, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        cv.drawContours(face, contours, -1, 255, cv.FILLED)
        face = cv.dilate(face, np.ones((3, 3), np.uint8))
        support[face > 0] = 0
        contact_band = np.zeros((768, 768), np.uint8)
        if i in (1, 11, 25):
            for x in range(170, 510):
                ys = np.where(face[:, x] > 0)[0]
                if len(ys) and ys[-1] > 570:
                    bottom = int(ys[-1])
                    contact_band[bottom - 20:bottom + 14, x] = 255
            support = np.maximum(support, contact_band)
        Image.fromarray(contact_band).save(HERE / f'keys/{i:02}-jaw-contact-band-768.png')
        Image.fromarray(support).save(HERE / f'keys/{i:02}-support-used-768.png')
        if i == 17:
            main = Image.open(HERE / 'sources/xingtong-17-1024.png').convert('RGB')
            body, body_registration = aligned(white_rgb(HERE / 'sources/frame17-api.png'), main)
            alpha = Image.open(HERE / 'sources/mask-17-1024.png').getchannel('A')
            clean = Image.composite(main, body, alpha)
            ornament, ornament_registration = aligned(white_rgb(HERE / 'keys/ornament17-api.png'), main)
            mask = Image.open(HERE / 'sources/mask-17-mascot-removal-1024.png').getchannel('A')
            clean = Image.composite(clean, ornament, mask)
            hands = np.zeros((768, 768), np.uint8)
            foreground = None
        else:
            main = Image.open(HERE / f'keys/{i:02}-original-1024.png').convert('RGB')
            edited, body_registration = aligned(white_rgb(HERE / f'keys/{i:02}-api.png'), main)
            ornament_registration = body_registration
            foreground = np.array(edited.resize((768, 768), Image.Resampling.LANCZOS))
            hands = hand_matte(foreground)
            mask = Image.open(HERE / f'keys/{i:02}-mask-1024.png').getchannel('A')
            clean = Image.composite(main, edited, mask)
        clean.save(HERE / f'keys/{i:02}-clean-1024.png')
        resized = np.array(clean.resize((768, 768), Image.Resampling.LANCZOS))
        weight = inset_weight(support)
        final = np.uint8(np.rint(original * (1 - weight[..., None]) + resized * weight[..., None]))
        hand_overlap = int(((hands > 0) & (support == 0) & (face > 0)).sum())
        if foreground is not None:
            contact_weight = inset_weight(contact_band)
            final = np.uint8(np.rint(final * (1 - contact_weight[..., None]) + foreground * contact_weight[..., None]))
            hand_weight = np.clip(cv.distanceTransform(np.uint8(hands > 0), cv.DIST_L2, 5) / 1.5, 0, 1)
            final = np.uint8(np.rint(final * (1 - hand_weight[..., None]) + foreground * hand_weight[..., None]))
            support = np.maximum(support, hands)
        Image.fromarray(hands).save(HERE / f'keys/{i:02}-foreground-hands-768.png')
        Image.fromarray(support).save(HERE / f'keys/{i:02}-support-used-768.png')
        assert np.array_equal(original[support == 0], final[support == 0])
        dest = HERE / f'keys/{i:02}-clean-768.png'; Image.fromarray(final).save(dest)
        report[str(i)] = {'changed_protected_pixels': 0, 'editable_pixels': int((support > 0).sum()),
                          'output_sha256': hashlib.sha256(dest.read_bytes()).hexdigest(), 'transparent_png_flattened_on': 'white',
                          'body_registration': body_registration, 'ornament_registration': ornament_registration,
                          'hand_occlusion_pixels_on_original_face': hand_overlap,
                          'jaw_contact_band_pixels': int((contact_band > 0).sum()),
                          'occlusion': 'Original head/face is the base; complete generated hands sit in front of lower cheeks.'}
    (HERE / 'keys/composition-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
