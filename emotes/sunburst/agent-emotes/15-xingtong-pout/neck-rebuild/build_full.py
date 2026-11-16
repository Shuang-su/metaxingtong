"""Extend the verified short review to the original 54-frame timeline, offline."""
from pathlib import Path
import hashlib, json
import cv2 as cv
import numpy as np
from PIL import Image, ImageDraw
from prepare_keys import frame, register, ornament_mapping, protect_face
from compose_keys import inset_weight
from build_short import affine, save_gif

HERE = Path(__file__).resolve().parent
OUT = HERE / 'full-review'

def indexed_exact(image, original):
    colors = np.unique(original.reshape(-1, 3), axis=0)
    assert len(colors) <= 256
    palette = Image.new('P', (1, 1))
    palette.putpalette(np.pad(colors, ((0, 256 - len(colors)), (0, 0)), mode='edge').ravel().tolist())
    indices = np.array(image.quantize(palette=palette, dither=Image.Dither.NONE))
    pack = np.array([65536, 256, 1], dtype='uint32')
    exact = np.searchsorted(colors.astype('uint32') @ pack, original.astype('uint32') @ pack).astype('uint8')
    same = np.all(np.array(image) == original, axis=2); indices[same] = exact[same]
    result = Image.fromarray(indices); result.putpalette(palette.getpalette())
    return result

def main():
    OUT.mkdir(exist_ok=True)
    original_path = HERE.parent / 'versions/01-original/master.gif'
    originals = {i: frame(original_path, i) for i in range(1, 55)}
    keys = {i: np.array(Image.open(HERE / f'keys/{i:02}-clean-768.png')) for i in [1, 25]}
    supports = {i: np.array(Image.open(HERE / f'keys/{i:02}-support-used-768.png')) for i in keys}
    hand_masks = {i: np.array(Image.open(HERE / f'keys/{i:02}-foreground-hands-768.png')) for i in keys}
    for support in supports.values():
        support[:500] = 0
    images, rows = [], []
    with Image.open(original_path) as gif:
        durations = []
        for j in range(54):
            gif.seek(j); durations.append(gif.info['duration'])
    for i, original in originals.items():
        if 11 <= i <= 25:
            result = np.array(Image.open(HERE / f'short-review/frame-{i:02}.png'))
            support = np.array(Image.open(HERE / f'short-review/allowed-{i:02}.png'))
            row = {'frame': i, 'source': 'verified-short-review'}
        else:
            source = 1 if i <= 10 or i >= 42 else 25
            matrix, registration = register(originals[source], original)
            candidate = affine(keys[source], matrix)
            support = affine(supports[source], matrix, True)
            hand_support = affine(hand_masks[source], matrix, True)
            face = protect_face(original)
            band = np.zeros((768, 768), np.uint8)
            for x in range(170, 550):
                ys = np.where(face[:, x])[0]
                if len(ys) and ys[-1] > 570:
                    bottom = int(ys[-1]); band[bottom - 20:bottom + 14, x] = 255
            support[face & (band == 0) & (hand_support < 100)] = 0
            weight = inset_weight(support)
            result = np.uint8(np.rint(original * (1 - weight[..., None]) + candidate * weight[..., None]))
            ornament_matrix = ornament_mapping(originals[source], original)
            ornament_support = np.array(Image.open(HERE / f'keys/{source:02}-ornament-768.png'))
            ornament_support = affine(ornament_support, ornament_matrix, True)
            ornament_support = cv.dilate(ornament_support, np.ones((9, 9), np.uint8))
            distance = cv.distanceTransform(np.uint8(ornament_support > 0), cv.DIST_L2, 5)
            z = np.clip(distance / 12, 0, 1); weight = z * z * (3 - 2 * z)
            donor = affine(keys[source], matrix)
            result = np.uint8(np.rint(result * (1 - weight[..., None]) + donor * weight[..., None]))
            support = np.maximum(support, ornament_support)
            row = {'frame': i, 'source_key': source, 'head_matrix': matrix.tolist(),
                   'registration': registration, 'ornament_matrix': ornament_matrix.tolist()}
        # Preserve the original gaze and facial animation independently of geometric supports.
        result[320:540, 100:560] = original[320:540, 100:560]
        support[320:540, 100:560] = 0
        assert np.array_equal(result[support == 0], original[support == 0])
        Image.fromarray(result).save(OUT / f'frame-{i:02}.png')
        Image.fromarray(support).save(OUT / f'allowed-{i:02}.png')
        row.update(duration_ms=durations[i-1], protected_pixel_changes=0, eye_roi_changes=0,
                   rgb_sha256=hashlib.sha256(result.tobytes()).hexdigest())
        rows.append(row); images.append(Image.fromarray(result))
    save_gif([indexed_exact(image, originals[i]) for i, image in enumerate(images, 1)], OUT / 'master.gif', durations)
    chats = [image.resize((320, 320), Image.Resampling.LANCZOS) for image in images]
    save_gif(chats, OUT / 'chat.gif', durations)
    save_gif([image.resize((112, 112), Image.Resampling.LANCZOS) for image in images], OUT / 'review-112.gif', durations)
    paired = []; triples = []
    sheet = Image.new('RGB', (960, 54 * 346), 'white'); draw = ImageDraw.Draw(sheet)
    contact = Image.new('RGB', (9 * 160, 6 * 180), 'white'); contact_draw = ImageDraw.Draw(contact)
    for j, (image, chat) in enumerate(zip(images, chats)):
        reference = Image.fromarray(frame(HERE.parent.parent / '10-pout/master.gif', j+1)).resize((320, 320), Image.Resampling.LANCZOS)
        pair = Image.new('RGB', (640, 320), 'white'); pair.paste(chat, (0, 0)); pair.paste(reference, (320, 0)); paired.append(pair)
        triple = Image.new('RGB', (960, 320), 'white'); triple.paste(Image.fromarray(originals[j+1]).resize((320, 320), Image.Resampling.LANCZOS), (0, 0)); triple.paste(pair, (320, 0)); triples.append(triple)
        sheet.paste(triple, (0, j * 346)); draw.text((6, j*346+324), f'F{j+1:02}  {durations[j]} ms  original / candidate / Nailu', fill='black')
        contact.paste(image.resize((160, 160), Image.Resampling.LANCZOS), (j % 9 * 160, j // 9 * 180)); contact_draw.text((j % 9 * 160+4, j // 9 * 180+163), f'F{j+1:02}', fill='black')
    save_gif(paired, OUT / 'paired.gif', durations)
    save_gif(triples, OUT / 'comparison.gif', durations)
    sheet.save(OUT / 'pose-comparison.jpg', quality=94); contact.save(OUT / 'contact-sheet.jpg', quality=95)
    (OUT / 'construction.json').write_text(json.dumps({'status': 'REVIEW_CANDIDATE_NOT_ADOPTED',
        'range': [1, 54], 'duration_ms': sum(durations), 'durations_ms': durations, 'frames': rows,
        'method': 'Images API key drawings at F1/11/17/25; corrected-key morph for F11–17, local pose registration elsewhere, independent ornament masks, original head base with lower-cheek contact/hand occlusion exceptions. No additional API calls by this script.'}, indent=2) + '\n')
    print(json.dumps({'status': 'REVIEW_CANDIDATE_NOT_ADOPTED', 'frames': 54, 'duration_ms': sum(durations)}))

if __name__ == '__main__':
    main()
