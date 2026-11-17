"""Nailu's full-drawing workflow: nine native keys plus 45 drawn inbetweens, no body compositing."""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image, ImageDraw
from prepare_design import white

HERE = Path(__file__).resolve().parent
OUT = HERE / 'delivery'

def source_cell(source):
    if 'key' in source:
        return white(Image.open(HERE / f'keys/{source["key"]:02}.png'))
    number = int(source['sheet'].split('-')[-1]); cell = source['cell'] - 1
    sheet = white(Image.open(HERE / f'sources/sheet-{number}-r1.png'))
    assert sheet.size == (1536, 2048)
    x, y = cell % 3 * 512, cell // 3 * 512
    return sheet.crop((x, y, x+512, y+512))

def save_gif(images, path, durations):
    cleaned = []
    for image in images:
        rgb = np.array(image.convert('RGB'))
        rgb[np.min(rgb, axis=2) >= 245] = 255
        cleaned.append(Image.fromarray(rgb))
    images = cleaned
    if images[0].width == 2 * images[0].height:
        # Reserve equal palette capacity for both characters; otherwise the small blue irises
        # can disappear among Nailu's browns/greens and Xingtong's lavender clothing.
        halves = []
        for side in range(2):
            samples = Image.new('RGB', (9*128, 6*128), 'white')
            for j, im in enumerate(images):
                width = im.width // 2
                panel = im.crop((side*width, 0, (side+1)*width, im.height))
                samples.paste(panel.resize((128, 128), Image.Resampling.LANCZOS), (j % 9*128, j // 9*128))
            half = samples.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
            halves.extend(half.getpalette()[:128*3])
        palette = Image.new('P', (1, 1)); palette.putpalette(halves)
    else:
        samples = Image.new('RGB', (9*128, 6*128), 'white')
        for j, im in enumerate(images):
            samples.paste(im.resize((128, 128), Image.Resampling.LANCZOS), (j % 9 * 128, j // 9 * 128))
        palette = samples.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    colors = np.array(palette.getpalette(), dtype='uint8').reshape(-1, 3)
    white_index = int(np.argmax(colors.astype('int32').sum(axis=1)))
    colors[white_index] = 255; palette.putpalette(colors.ravel().tolist())
    frames = []
    for image in images:
        indices = np.array(image.quantize(palette=palette, dither=Image.Dither.NONE))
        indices[np.all(np.array(image) == 255, axis=2)] = white_index
        indexed = Image.fromarray(indices); indexed.putpalette(palette.getpalette()); frames.append(indexed)
    assert len({hashlib.sha256(im.convert('RGB').tobytes()).hexdigest() for im in frames}) == 54
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations, loop=0, disposal=1, optimize=False)

def main():
    OUT.mkdir(exist_ok=True)
    workflow = json.loads((HERE / 'sources/nailu-workflow-manifest.json').read_text())
    sources = [row['source'].copy() for row in workflow['frame_review']]
    selection_path = HERE / 'selection.json'
    if selection_path.exists():
        sources = json.loads(selection_path.read_text())['frames']
    else:
        selection_path.write_text(json.dumps({'method': 'Same complete-frame cell selection as the Nailu production manifest; editable after visual review.', 'frames': sources}, indent=2) + '\n')
    cells = [source_cell(source) for source in sources]
    assert len(cells) == 54
    # Keep one crop for all frames. Preserve the hair/ahoge if a source margin is narrower than 5px.
    margin = 5
    for cell in cells:
        ink = np.min(np.array(cell), axis=2) < 200
        ys, xs = np.where(ink)
        margin = min(margin, int(xs.min()), int(ys.min()), int(511-xs.max()))
    frames = [cell.crop((margin, margin, 512-margin, 512-margin)) for cell in cells]
    records = []
    for j, (im, source) in enumerate(zip(frames, sources)):
        im.save(OUT / f'frame-{j+1:02}.png')
        records.append({'frame': j+1, 'source': source, 'duration_ms': workflow['frame_durations_ms'][j],
                        'size': list(im.size), 'rgb_sha256': hashlib.sha256(im.tobytes()).hexdigest()})
    durations = workflow['frame_durations_ms']
    for size, name in [(512, 'master-512.gif'), (768, 'master.gif'), (320, 'chat.gif'), (112, 'review-112.gif')]:
        save_gif([im.resize((size, size), Image.Resampling.LANCZOS) for im in frames], OUT / name, durations)
    paired = []; comparison = Image.new('RGB', (640, 54*346), 'white'); pen = ImageDraw.Draw(comparison)
    with Image.open(HERE.parents[1] / '10-pout/master.gif') as nailu:
        for j, im in enumerate(frames):
            nailu.seek(j); pair = Image.new('RGB', (640, 320), 'white')
            pair.paste(white(nailu).resize((320, 320), Image.Resampling.LANCZOS), (0, 0))
            pair.paste(im.resize((320, 320), Image.Resampling.LANCZOS), (320, 0)); paired.append(pair)
            comparison.paste(pair, (0, j*346)); pen.text((6, j*346+324), f'F{j+1:02}  {durations[j]} ms   Nailu / new Xingtong', fill='black')
    save_gif(paired, OUT / 'paired.gif', durations)
    comparison.save(OUT / 'pose-comparison.jpg', quality=94)
    contact = Image.new('RGB', (9*160, 6*180), 'white'); pen = ImageDraw.Draw(contact)
    for j, im in enumerate(frames):
        contact.paste(im.resize((160, 160), Image.Resampling.LANCZOS), (j%9*160, j//9*180)); pen.text((j%9*160+4, j//9*180+163), f'F{j+1:02}', fill='black')
    contact.save(OUT / 'contact-sheet.jpg', quality=95)
    manifest = {'status': 'NEW_FULL_DRAWING_CANDIDATE', 'title': '星瞳·鼓脸晃头（统一奶绿画风）',
                'frames': 54, 'unique_source_drawings': len({r['rgb_sha256'] for r in records}),
                'duration_ms': sum(durations), 'durations_ms': durations, 'loop': 0,
                'native_cell_px': 512, 'uniform_crop_each_edge_px': margin,
                'method': 'Nine complete native GIF key drawings plus 45 complete inbetween drawings, using Nailu\'s 3x4 sheet workflow and exposure table. White flattening, uniform crop, scale and global palette encoding only. No old Xingtong frames, body patching, per-part transforms, optical-flow frames or crossfades.',
                'frame_review': records}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'frames': 54, 'unique_drawings': manifest['unique_source_drawings'], 'duration_ms': sum(durations), 'crop_px': margin}))

if __name__ == '__main__':
    main()
