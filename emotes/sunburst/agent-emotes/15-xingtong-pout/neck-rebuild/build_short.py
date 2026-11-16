"""Build the F11–25 review from cached API keys; this script makes no API calls."""
from pathlib import Path
import json, hashlib
import cv2 as cv
import numpy as np
from PIL import Image, ImageDraw
from prepare_keys import frame, register, ornament_mapping, protect_face
from compose_keys import inset_weight

HERE = Path(__file__).resolve().parent
OUT = HERE / 'short-review'
Y, X = np.mgrid[:768, :768].astype('float32')

def read(path):
    return np.array(Image.open(path))

def affine(a, matrix, mask=False):
    return cv.warpAffine(a, matrix, (768, 768), flags=cv.INTER_LINEAR if mask else cv.INTER_CUBIC,
                         borderMode=cv.BORDER_CONSTANT, borderValue=0 if mask else (255, 255, 255))

def flow(a, b):
    detector = cv.DISOpticalFlow_create(cv.DISOPTICAL_FLOW_PRESET_MEDIUM)
    return detector.calc(cv.cvtColor(a, cv.COLOR_RGB2GRAY), cv.cvtColor(b, cv.COLOR_RGB2GRAY), None)

def inverse_flow(f, amount):
    mx, my = X.copy(), Y.copy()
    for _ in range(5):
        sampled = cv.remap(f, mx, my, cv.INTER_LINEAR, borderMode=cv.BORDER_REPLICATE)
        mx, my = X - amount * sampled[:, :, 0], Y - amount * sampled[:, :, 1]
    return mx, my

def remap(a, maps):
    return cv.remap(a, *maps, cv.INTER_CUBIC, borderMode=cv.BORDER_REPLICATE)

def save_gif(images, path, durations):
    images[0].save(path, save_all=True, append_images=images[1:], duration=durations, loop=0, disposal=1, optimize=False)

def main():
    OUT.mkdir(exist_ok=True)
    originals = {i: frame(HERE.parent / 'versions/01-original/master.gif', i) for i in range(11, 26)}
    keys = {i: read(HERE / f'keys/{i:02}-clean-768.png') for i in [11, 17, 25]}
    masks = {i: read(HERE / f'keys/{i:02}-support-used-768.png') for i in keys}
    hands = {i: read(HERE / f'keys/{i:02}-foreground-hands-768.png') for i in keys}
    for mask in masks.values():
        mask[:500] = 0
    ab, ba = flow(keys[11], keys[17]), flow(keys[17], keys[11])
    end, _ = register(originals[11], originals[17])
    end_angle = np.arctan2(end[1, 0], end[0, 0])
    final_frames, allowed, records = [], [], []
    for i, original in originals.items():
        if i <= 17:
            current, registration = register(originals[11], original)
            angle = np.arctan2(current[1, 0], current[0, 0])
            t = float(np.clip(angle / end_angle, 0, 1))
            ma, mb = inverse_flow(ab, t), inverse_flow(ba, 1 - t)
            candidate = np.uint8(np.clip(np.rint(remap(keys[11], ma) * (1 - t) + remap(keys[17], mb) * t), 0, 255))
            support = np.maximum(remap(masks[11], ma), remap(masks[17], mb))
            hand_support = np.maximum(remap(hands[11], ma), remap(hands[17], mb))
            scale = 1 + (np.linalg.norm(end[:, 0]) - 1) * t
            expected = np.array([[scale * np.cos(t * end_angle), -scale * np.sin(t * end_angle), t * end[0, 2]],
                                 [scale * np.sin(t * end_angle), scale * np.cos(t * end_angle), t * end[1, 2]], [0, 0, 1.]])
            adjustment = (np.vstack([current, [0, 0, 1.]]) @ np.linalg.inv(expected))[:2]
            candidate = affine(candidate, adjustment)
            support = affine(support, adjustment, True)
            hand_support = affine(hand_support, adjustment, True)
            source_key = 11 if t < .5 else 17
        else:
            source_key = 17 if i <= 21 else 25
            current, registration = register(originals[source_key], original)
            candidate = affine(keys[source_key], current)
            support = affine(masks[source_key], current, True)
            hand_support = affine(hands[source_key], current, True)
            t = None
        face = protect_face(original)
        band = np.zeros((768, 768), np.uint8)
        for x in range(170, 510):
            ys = np.where(face[:, x])[0]
            if len(ys) and ys[-1] > 570:
                bottom = int(ys[-1]); band[bottom - 20:bottom + 14, x] = 255
        support[face & (band == 0) & (hand_support < 100)] = 0
        weight = inset_weight(support)
        result = np.uint8(np.rint(original * (1 - weight[..., None]) + candidate * weight[..., None]))
        ornament_transform = ornament_mapping(originals[source_key], original)
        ornament_mask = read(HERE / f'keys/{source_key:02}-ornament-768.png')
        ornament_mask = affine(ornament_mask, ornament_transform, True)
        ornament_mask = cv.dilate(ornament_mask, np.ones((9, 9), np.uint8))
        head_transform, _ = register(originals[source_key], original)
        ornament = affine(keys[source_key], head_transform)
        distance = cv.distanceTransform(np.uint8(ornament_mask > 0), cv.DIST_L2, 5)
        z = np.clip(distance / 12., 0, 1); weight = z * z * (3 - 2 * z)
        result = np.uint8(np.rint(result * (1 - weight[..., None]) + ornament * weight[..., None]))
        support = np.maximum(support, ornament_mask)
        assert np.array_equal(result[support == 0], original[support == 0])
        # Keep a broad eye/upper-face ROI exact, independently of the mask assertion.
        assert np.array_equal(result[320:540, 100:560], original[320:540, 100:560])
        Image.fromarray(result).save(OUT / f'frame-{i:02}.png')
        Image.fromarray(support).save(OUT / f'allowed-{i:02}.png')
        final_frames.append(Image.fromarray(result)); allowed.append(support)
        records.append({'frame': i, 'source_key': source_key, 'morph_11_17': t,
                        'registration': registration, 'head_matrix': current.tolist(), 'ornament_matrix': ornament_transform.tolist(),
                        'ornament_donor_head_matrix': head_transform.tolist(),
                        'outside_allowed_changes': 0, 'eye_roi_changes': 0,
                        'rgb_sha256': hashlib.sha256(result.tobytes()).hexdigest()})
    with Image.open(HERE.parent / 'versions/01-original/master.gif') as original:
        durations = []
        for i in range(11, 26):
            original.seek(i - 1); durations.append(original.info['duration'])
    indexed = []
    for i, image, edit_support in zip(range(11, 26), final_frames, allowed):
        colors = np.unique(originals[i].reshape(-1, 3), axis=0)
        assert len(colors) <= 256
        palette = Image.new('P', (1, 1))
        palette.putpalette(np.pad(colors, ((0, 256 - len(colors)), (0, 0)), mode='edge').ravel().tolist())
        quantized = np.array(image.quantize(palette=palette, dither=Image.Dither.NONE))
        packed_colors = colors.astype('uint32') @ np.array([65536, 256, 1], dtype='uint32')
        packed_original = originals[i].astype('uint32') @ np.array([65536, 256, 1], dtype='uint32')
        exact_indices = np.searchsorted(packed_colors, packed_original).astype('uint8')
        same = np.all(np.array(image) == originals[i], axis=2)
        quantized[same] = exact_indices[same]
        exact_image = Image.fromarray(quantized); exact_image.putpalette(palette.getpalette())
        indexed.append(exact_image)
    save_gif(indexed, OUT / 'candidate-768.gif', durations)
    chats = [im.resize((320, 320), Image.Resampling.LANCZOS) for im in final_frames]
    save_gif(chats, OUT / 'candidate-320.gif', durations)
    save_gif([im.resize((112, 112), Image.Resampling.LANCZOS) for im in final_frames], OUT / 'candidate-112.gif', durations)
    comparisons = []
    sheet = Image.new('RGB', (960, len(records) * 346), 'white'); draw = ImageDraw.Draw(sheet)
    for r, (i, im) in enumerate(zip(range(11, 26), chats)):
        comparison = Image.new('RGB', (960, 320), 'white')
        for c, image in enumerate([Image.fromarray(originals[i]), im, Image.fromarray(frame(HERE.parent.parent / '10-pout/master.gif', i))]):
            comparison.paste(image.resize((320, 320), Image.Resampling.LANCZOS), (c * 320, 0))
        comparisons.append(comparison); sheet.paste(comparison, (0, r * 346))
        draw.text((8, r * 346 + 324), f'F{i:02}  {durations[r]} ms  original / candidate / Nailu', fill='black')
    save_gif(comparisons, OUT / 'comparison-320.gif', durations)
    sheet.save(OUT / 'frames-comparison.jpg', quality=94)
    (OUT / 'construction.json').write_text(json.dumps({'status': 'SHORT_REVIEW_CANDIDATE_NOT_ADOPTED', 'frames': records,
        'duration_ms': sum(durations), 'durations_ms': durations, 'range': [11, 25],
        'method': 'Cached API key drawings; bidirectional morph between corrected keys 11/17; local registration within each original pose family; separate ornament tracking; original head/eye base with lower cheek occlusion/contact exceptions.'}, indent=2) + '\n')
    print(json.dumps({'frames': 15, 'duration_ms': sum(durations), 'status': 'SHORT_REVIEW_CANDIDATE_NOT_ADOPTED'}))

if __name__ == '__main__':
    main()
