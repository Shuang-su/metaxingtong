"""Extract the actual native GIF keys and prepare Nailu-style full-pose inbetween sheets."""
from pathlib import Path
import hashlib, json
from PIL import Image, ImageDraw
from prepare_design import white
HERE = Path(__file__).resolve().parent

def main():
    src = HERE / 'sources'; jobs = HERE / 'jobs'; keys_dir = HERE / 'keys'; keys_dir.mkdir(exist_ok=True)
    story = json.loads((HERE / 'storyboard.json').read_text())
    keys = []; rows = []
    with Image.open(src / 'native-nine-r1.gif') as gif:
        assert gif.format == 'GIF' and gif.size == (512, 512) and gif.n_frames == 9 and gif.info.get('loop') == 0
        for i in range(9):
            gif.seek(i); key = white(gif); keys.append(key); key.save(keys_dir / f'{i+1:02}.png')
            rows.append({'key': i+1, 'source_frame': i, 'duration_ms': gif.info['duration'], 'rgb_sha256': hashlib.sha256(key.tobytes()).hexdigest()})
    assert len({r['rgb_sha256'] for r in rows}) == 9
    review = Image.new('RGB', (1536, 3 * 540), 'white'); draw = ImageDraw.Draw(review)
    for j, key in enumerate(keys):
        review.paste(key, (j % 3 * 512, j // 3 * 540)); draw.text((j % 3 * 512 + 8, j // 3 * 540 + 516), f'key {j+1}', fill='black')
    review.save(HERE / 'native-nine-review.jpg', quality=95)
    for index, triple in enumerate([(1, 2, 3), (3, 4, 5), (5, 6, 7), (7, 8, 9), (9, 1, 2)]):
        a, b, c = triple; guide = Image.new('RGB', (1536, 2048), 'white')
        for row, key_id in enumerate([a, b, b, c]):
            for column in range(3):
                guide.paste(keys[key_id-1], (column*512, row*512))
        guide.save(src / f'sheet-{index}-guide.png')
        prompt = ('Act as a senior 2D inbetween animator. Return ONE production sheet with EXACTLY THREE columns and FOUR rows, TWELVE equal complete 512x512 square frames, total 1536x2048. Read left-to-right, top-to-bottom. No borders, labels, grid lines or text. '
                  'Image 1 has four endpoint rows A, B, B, C. Draw SIX different complete inbetween poses from A toward B across the top two rows, and SIX from B toward C across the bottom two rows. '
                  'The six progress amounts in EACH interval are 10%,26%,42%,58%,74%,90%. Neither endpoint is copied into these cells: actual endpoint frames are supplied separately in the final GIF. Every cell must show a distinct successive small action. '
                  'Image 2 is the character model/style guide; maintain the exact design visible in image 1. Xingtong, BLUE eyes, SILVER-GRAY bob, broad bangs, small bent ahoge, plain PURPLE headband WITHOUT a mascot. Pale blue-lavender oversized cardigan and complete ribbed cuffs, restrained white fur collar and pink inner shirt. '
                  'Use the same simple Nailu chibi linework, compact proportions, block hair shading, colors, head size, white margins, square close-up and fixed camera as the supplied endpoints. Do not add hair strands, ornaments, flowers, green streaks, animals, text or motion symbols. '
                  'Animate the entire coherent figure in every cell: face, short continuous neck, collar, shoulders, both small fists, complete cuffs and sleeves. Head leads; the two hands compensate independently; the shoulders follow softly; the bob hair lags slightly. The fists stay gently close to the lower cheeks/collar. '
                  'Never rotate the complete body as one rigid slab, paste a separate face onto a stationary body, double a hand, detach the jaw, create a long neck, put hair across the neck front, leave a cuff fragment or a diagonal blank wedge at the bottom. '
                  'Keep all hair, ahoge and both hands inside their own cell, with the same opaque WHITE background and no camera zoom. Draw only one Xingtong in each frame. '
                  f'A = key {a}: {story["poses"][a-1]}\nB = key {b}: {story["poses"][b-1]}\nC = key {c}: {story["poses"][c-1]}\n'
                  'Follow the ACTUAL supplied illustrated endpoints for the precise positions, expression, costume, and anatomy; the descriptions explain intent. Bridge from one actual pose to the next naturally. Return only the complete 3x4 production sheet.')
        (jobs / f'sheet-{index}-r1.txt').write_text(prompt + '\n')
        job = {'name': f'complete-pose-inbetweens-{a}-{b}-{c}-r1',
               'images': [f'sources/sheet-{index}-guide.png', 'sources/style-r1.png'],
               'prompt': f'jobs/sheet-{index}-r1.txt', 'output': f'sources/sheet-{index}-r1.png',
               'parameters': {'size': '1536x2048', 'quality': 'medium', 'output_format': 'png', 'background': 'opaque', 'n': 1, 'extra_body': {'complexity': 'high'}}}
        (jobs / f'sheet-{index}-r1.json').write_text(json.dumps(job, indent=2) + '\n')
    (HERE / 'native-key-records.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(json.dumps({'native_frames': 9, 'different_frames': 9, 'prepared_sheets': 5}))

if __name__ == '__main__':
    main()
