"""Compose the fixed-body sticker from its Sunburst drawings and the partner's timings."""
import hashlib
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SHOT = HERE.parent.parent
REFS = SHOT.parent / "references"
RESAMPLE = Image.Resampling.LANCZOS
WHITE = (255, 255, 255)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def isolated_cell(rgb):
    # Flood only near-white pixels connected to the outer edge. Whites inside
    # the hair, eyes and headband mascot belong to the drawing.
    pixels = np.asarray(rgb, dtype=np.uint8)
    low = pixels.min(axis=2)
    outside = (low > 192).astype(np.uint8)
    cv2.floodFill(outside, None, (0, 0), 2)
    exterior = outside == 2
    opacity = np.ones(low.shape, dtype=np.float32)
    opacity[exterior] = np.clip((253.0 - low[exterior]) / 200.0, 0, 1)
    colors = 255 - (255.0 - pixels) / np.maximum(opacity[..., None], 1 / 255)
    alpha = np.uint8(np.round(opacity * 255))
    cut = Image.fromarray(np.dstack((np.uint8(np.clip(colors, 0, 255)), alpha)))
    # Exclude near-white paper noise from the registration box.
    box = cut.getchannel("A").point(lambda p: 255 if p >= 128 else 0).getbbox()
    return cut.crop((box[0]-1, box[1]-1, box[2]+1, box[3]+1))


def match_reference_paints(layer, material):
    """Grade only the sampled paints, leaving near-white reflections and ink intact."""
    rgb = np.array(layer.convert("RGB"), dtype=np.float32)
    red, green, blue = rgb.transpose(2, 0, 1).copy()
    def ramp(value, low, high):
        return np.clip((value - low) / (high - low), 0, 1)
    def shift(mask, delta):
        rgb[:] += mask[..., None] * np.asarray(delta, dtype=np.float32)
    if material == "head":
        # The source's silver is nearly neutral and the highlights stay white.
        silver = (ramp(blue-red, -1, 4) * (1-ramp(blue-green, 20, 38))
                  * ramp(red, 95, 155) * (1-ramp(red, 218, 251)))
        shift(silver, (-5, -2, -7))
        y, x = np.mgrid[:layer.height, :layer.width]
        y, x = y / layer.height, x / layer.width
        eyes = (y > .57) & (y < .81) & (x > .18) & (x < .83)
        shift(eyes * ramp(blue-red, 20, 75) * ramp(blue-green, 10, 38)
              * ramp(red, 38, 95), (-27, 0, 20))
        cheeks = (y > .69) & (y < .88) & ((x < .38) | (x > .63))
        shift(cheeks * ramp(red-green, 48, 90) * ramp(red-blue, 44, 88)
              * ramp(red, 176, 220), (-7, -3, 7))
    else:
        # Lift the light periwinkle fabric without touching rose shirt, skin or fur.
        periwinkle = (ramp(blue-red, 9, 33) * ramp(blue-green, 6, 29)
                      * ramp(red, 125, 190) * (1-ramp(red, 222, 250)))
        shift(periwinkle, (7, 9, 3))
    result = Image.fromarray(np.uint8(np.clip(np.round(rgb), 0, 255)))
    result.putalpha(layer.getchannel("A"))
    return result


def draw(canvas_size, body, head, angle, bob):
    ratio = canvas_size / 768
    def px(value):
        return round(value * ratio)
    canvas = Image.new("RGBA", (canvas_size, canvas_size), "white")
    canvas.alpha_composite(body.resize((px(668), px(668)), RESAMPLE), (px(50), px(103)))
    # Rotate around the base of the skull. Torso, cuffs and fingers never move.
    face = Image.new("RGBA", canvas.size)
    h = px(513)
    w = round(head.width * h / head.height)
    face.alpha_composite(head.resize((w, h), RESAMPLE), ((canvas_size - w) // 2, px(37 + bob)))
    face = face.rotate(-angle, Image.Resampling.BICUBIC, center=(px(384), px(510)))
    canvas.alpha_composite(face)
    return canvas.convert("RGB")


def index_colors(frames):
    # Downweight common colors so small coral cheek marks and saturated irises
    # survive alongside silver gradients. Use one fixed table for every frame.
    samples = np.concatenate([np.asarray(frame)[::4, ::4].reshape(-1, 3) for frame in frames[::3]])
    bins = (samples.astype(np.int32) // 8) @ np.array([1024, 32, 1])
    counts = np.bincount(bins, minlength=32768)
    used = counts > 0
    means = np.column_stack([np.bincount(bins, weights=samples[:, k], minlength=32768)[used] /
                             counts[used] for k in range(3)])
    representatives = np.repeat(np.uint8(np.round(means)), np.ceil(np.sqrt(counts[used])).astype(int), axis=0)
    training = Image.fromarray(representatives.reshape(1, -1, 3))
    paint = [(255,255,255), (197,194,201), (160,157,170), (225,222,227),
             (74,141,233), (58,96,184), (90,169,250), (44,97,197), (117,201,255),
             (219,220,253), (180,178,244), (242,176,196), (245,128,104),
             (236,115,89), (249,233,226), (252,144,117)]
    adaptive = training.quantize(256-len(paint), method=Image.Quantize.MEDIANCUT).getpalette()
    palette = np.uint8(paint + list(zip(adaptive[::3], adaptive[1::3], adaptive[2::3])))[:256]
    # Index a 6-bit lattice with actual nearest palette entries. This also makes
    # common areas of a paired animation match between repeated exposures.
    lattice = np.indices((64, 64, 64), dtype=np.float32).reshape(3, -1).T.copy() * 4 + 1.5
    _, nearest = cv2.batchDistance(lattice, palette.astype(np.float32), cv2.CV_32F, K=1)
    lookup = nearest.reshape(64, 64, 64).astype(np.uint8)
    lookup[-1,-1,-1] = 0
    indexed = []
    for frame in frames:
        r, g, b = (np.asarray(frame) // 4).transpose(2, 0, 1)
        img = Image.fromarray(lookup[r, g, b])
        img.putpalette(palette.ravel().tolist())
        indexed.append(img)
    return indexed


def encode(path, frames, width, timings):
    thumbs = [frame if frame.width == width else frame.resize((width, width), RESAMPLE) for frame in frames]
    indexed = index_colors(thumbs)
    indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=timings,
                    loop=0, disposal=1, optimize=False)
    return dict(file=path.name, size=[width, width], bytes=path.stat().st_size, sha256=digest(path.read_bytes()))


def render():
    samples = read(HERE / "motion-input.json")["samples"]
    times = [sample["duration_ms"] for sample in samples]
    observed = []
    for sample in samples:
        a, b = sample["eyes"]
        observed.append(math.degrees(math.atan2(b[1]-a[1], b[0]-a[0])))
    # Smooth the measured tilt over neighbouring exposures; wrap across the loop.
    weights = [1, 2, 3, 4, 3, 2, 1]
    angles = [sum(w * observed[(i+j-3) % len(samples)] for j, w in enumerate(weights))
              / sum(weights) * .88 for i in range(len(samples))]
    sheet = Image.open(HERE / "faces.png").convert("RGB")
    heads = [isolated_cell(sheet.crop((x, y, x+512, y+512)))
             for y in (0, 512, 1024) for x in (0, 512, 1024)]
    heads = [match_reference_paints(head, "head") for head in heads]
    body = Image.open(HERE / "body.png").convert("RGBA")
    body.putalpha(body.getchannel("A").point(lambda a: 0 if a < 4 else min(255, round(a*255/254))))
    body = match_reference_paints(body, "body")
    # Puff, hold with a side glance, exhale in an O, then return to the first pout.
    boundaries = [0, 5, 9, 14, 21, 30, 36, 42, 48]
    poses = []
    frames = []
    review = []
    for i, sample in enumerate(samples):
        key = max(k for k, start in enumerate(boundaries) if start <= i)
        phase = sum(times[:i]) / sum(times) * math.tau
        bob = 1.6 * math.sin(phase - .4)
        frames.append(draw(768, body, heads[key], angles[i], bob))
        source = dict(head_cell=key+1, clockwise_deg=round(angles[i], 5), vertical_px=round(bob, 3))
        if i in boundaries:
            source["key"] = key + 1
        poses.append(dict(frame=i+1, reference_frame=i+1, nailu_eyes=sample["eyes"], **source))
        review.append(dict(frame=i+1, file=f"frames/{i+1:02}.png", source=source, duration_ms=times[i]))
    portrait = draw(1024, body, heads[0], angles[0], 1.6 * math.sin(-.4))
    portrait.save(REFS / "xingtong-detailed.png")
    assets = [encode(SHOT / name, frames, width, times) for name, width in (("master.gif", 768), ("chat.gif", 320))]
    contact = Image.new("RGB", (128*8, 148*7), "#edeae7")
    pen = ImageDraw.Draw(contact)
    with Image.open(SHOT / "master.gif") as gif:
        assert gif.n_frames == len(frames)
        for i, r in enumerate(review):
            gif.seek(i)
            frame = gif.convert("RGB")
            frame.save(SHOT / r["file"])
            r["pixel_sha256"] = digest(frame.tobytes())
            x, y = i % 8 * 128, i // 8 * 148
            contact.paste(frame.resize((128, 128), RESAMPLE), (x, y))
            pen.text((x+4, y+130), f'{i+1:02}  {times[i]} ms', fill="#313039")
    contact.save(SHOT / "frames.jpg", quality=94)
    save(SHOT / "matched-motion.json", dict(partner="10-pout", method="眼线取奶绿原帧，循环平滑后绕星瞳颈部旋转头层。衣身、双袖与平放的双手全程使用同一底图。", frames=poses))
    provenance = {}
    for name in ("head", "body", "faces"):
        receipt = read(HERE / (name + ".json"))
        receipt["file"] = str((HERE / (name + ".png")).relative_to(SHOT))
        provenance[name] = receipt
    save(SHOT / "manifest.json", dict(title="星瞳·鼓脸晃头", file="master.gif", chat_file="chat.gif",
        sha256=assets[0]["sha256"], size=[768, 768], frames=len(frames),
        different_frames=len({r["pixel_sha256"] for r in review}), total_ms=sum(times),
        loop=0, frame_durations_ms=times, assets=assets, sync_source="10-pout",
        storyboard="storyboard.json", source_reference=str((HERE / "original-color-guide.png").relative_to(SHOT)),
        images_api=provenance, frame_review=review, native_cell_px=512, body_native_px=1024,
        method="九张完整头部表情原画按时值切换，叠在一张固定衣身和双手原画上。以颈点为轴做头部刚性旋转，白底，全片统一调色板。"))
    save(REFS / "xingtong-detailed.json", dict(file="xingtong-detailed.png",
        sha256=digest((REFS / "xingtong-detailed.png").read_bytes()), size=[1024, 1024],
        model=provenance["head"]["model"], method="第一张头部表情与平放双手底图合成",
        source_receipts="../15-xingtong-pout/manifest.json", sources=["lavender-hands.png", "lavender-front.png"]))


if __name__ == "__main__":
    render()
