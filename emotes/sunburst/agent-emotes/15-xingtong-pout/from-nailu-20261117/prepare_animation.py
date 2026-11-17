"""Prepare the native nine-pose loop and full-frame inbetween production sheets."""
from pathlib import Path
import json
from PIL import Image
from prepare_design import white

HERE = Path(__file__).resolve().parent
POSES = [
    'Front and relaxed, tiny closed pout, eyes toward the viewer, both small fists softly beside the collar.',
    'Cheeks inflate halfway; glance slightly toward viewer-left and lift the two fists a little with a gentle shoulder squeeze.',
    'Cheeks fully puffed; tilt the head about 10 degrees toward viewer-left. The hands compensate independently beside the lower cheeks, shoulders remain nearly level and hair trails slightly toward viewer-right.',
    'Rock back through the center with cheeks still puffed. The fists ease to a balanced position; hair catches up a fraction later.',
    'Tilt the head about 10 degrees toward viewer-right, cheeks puffed, eyes glancing that way. Reverse the hand compensation while keeping a short connected neck and complete cuffs.',
    'A tiny rebound about 3 degrees toward viewer-left with a brief soft blink; cheek puff and softly closed fists remain visible.',
    'Return to center, reopen bright blue eyes, part the small lips to release the cheek puff. Hands ease slightly down; no drawn cloud or motion symbol.',
    'Cheeks relaxed with a very small relieved smile. Shoulders and fists relax and the bob hair settles; keep both hands visible.',
    'Nearly the opening pose, with a tiny residual 2-degree viewer-right tilt and fists beginning to lift/close. End close enough to pose 1 for a smooth little return, without duplicating pose 1.'
]

def main():
    jobs = HERE / 'jobs'; src = HERE / 'sources'
    timings = json.loads((src / 'nailu-workflow-manifest.json').read_text())['frame_durations_ms']
    storyboard = {'title': '星瞳·鼓脸晃头（奶绿画风重新编排）', 'style': 'Actual Nailu 10-pout rendering and complete-pose workflow.',
                  'identity_references': ['sources/xingtong-native-front.png', 'sources/xingtong-native-hands.png'],
                  'accessory': 'Plain purple headband, deliberately no blue-white mascot.', 'poses': POSES,
                  'source_workflow': 'Native nine-frame GIF -> full-frame inbetween sheets -> 54-frame exposure sheet.',
                  'native_gif': {'frame_count': 9, 'size': [512, 512], 'frame_duration_ms': 200},
                  'delivery_durations_ms': timings, 'delivery_duration_ms': sum(timings)}
    (HERE / 'storyboard.json').write_text(json.dumps(storyboard, ensure_ascii=False, indent=2) + '\n')
    prompt = ('Create a NEW original seamless chibi animated GIF of Xingtong in the exact simple linework, compact proportions, soft cel shading and low detail level of the provided new design. '
              'Image 1 is the locked Xingtong model drawing, image 2 shows the Nailu animation drawing style. Keep Xingtong\'s identity and costume from image 1 throughout: SILVER-GRAY short bob, broad bangs and simple highlights, small bent ahoge, bright BLUE eyes, plain PURPLE headband with NO mascot, pale blue-lavender oversized knit cardigan and full ribbed cuffs, small white fur collar trim and pink inner neckline. '
              'No green eyes, green hair stripe, flowers, twin tails, heart cowlick, extra accessory or neck rings. Use the SAME hair length, face proportions, clothing, scale and fixed waist-up camera for every frame. '
              'Draw every frame as a COMPLETE coherent character: the head, short neck, collar, shoulders, arms, fists and whole cuffs act together naturally. Do not animate a separate head over a frozen body; do not make the shoulders and fists one stiff rotating slab. '
              'The head leads, soft shoulders follow slightly, the two complete fist-and-cuff units compensate independently, the silver bob lags a little, and the neck remains short and connected. No floating jaw, hair crossing the neck front, cut sleeves, white wedges or double contours. '
              'Both fists remain visible gently beside the lower cheeks/collar. White background, no text, effects, symbols, motion lines or added props. Keep complete hair and ahoge inside consistent white margins. '
              'Make one playful puff-cheek left/right head-rock loop in exactly NINE successive complete poses, read as the following performance:\n' +
              '\n'.join(f'{i+1}. {pose}' for i, pose in enumerate(POSES)) +
              '\nFrame 9 returns smoothly to frame 1. Keep the acting gentle, cute and legible in a 112px sticker. All nine frames must be different drawn moments, with no camera zoom, crossfade, duplicated face or extra hand. Return a single 512x512 animated GIF with nine frames, 200ms per frame and an infinite seamless loop.')
    (jobs / 'native-nine-r1.txt').write_text(prompt + '\n')
    job = {'name': 'new-complete-Xingtong-nine-pose-loop-r1',
           'images': ['sources/style-r1.png', 'sources/nailu-actual-style-guide.png'], 'prompt': 'jobs/native-nine-r1.txt',
           'output': 'sources/native-nine-r1.gif',
           'parameters': {'size': '512x512', 'quality': 'medium', 'output_format': 'gif', 'background': 'opaque', 'n': 1,
                          'extra_body': {'frame_count': 9, 'frame_duration_ms': 200, 'complexity': 'high'}}}
    (jobs / 'native-nine-r1.json').write_text(json.dumps(job, indent=2) + '\n')

if __name__ == '__main__':
    main()
