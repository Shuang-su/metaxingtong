"""Prepare original identity references and the actual Nailu animation style guide."""
from pathlib import Path
import json
from PIL import Image
HERE = Path(__file__).resolve().parent

def white(im):
    a = im.convert('RGBA'); b = Image.new('RGBA', a.size, 'white'); b.alpha_composite(a)
    return b.convert('RGB')

def main():
    src = HERE / 'sources'; jobs = HERE / 'jobs'; jobs.mkdir(exist_ok=True)
    for name in ['front', 'hands']:
        white(Image.open(src / f'xingtong-native-{name}.png')).resize((512, 512), Image.Resampling.LANCZOS).save(src / f'xingtong-{name}-white.png')
    with Image.open(src / 'nailu-native-nine.gif') as gif:
        board = Image.new('RGB', (1536, 512), 'white')
        for j, i in enumerate([0, 3, 6]):
            gif.seek(i); board.paste(white(gif).resize((512, 512)), (j * 512, 0))
    board.save(src / 'nailu-actual-style-guide.png')
    job = {'name': 'native-Xingtong-in-Nailu-style-r1',
           'images': ['sources/xingtong-front-white.png', 'sources/xingtong-hands-white.png', 'sources/nailu-actual-style-guide.png'],
           'prompt': 'jobs/style-r1.txt', 'output': 'sources/style-r1.png',
           'parameters': {'size': '1024x1024', 'quality': 'medium', 'output_format': 'png', 'background': 'opaque', 'n': 1, 'extra_body': {'complexity': 'high'}}}
    (jobs / 'style-r1.json').write_text(json.dumps(job, indent=2) + '\n')

if __name__ == '__main__':
    main()
