"""Check real GIF decoding and three timed cycles in sandboxed headless Chromium."""
from pathlib import Path
import argparse, asyncio, hashlib, json
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent

async def check(full):
    folder = 'full-review' if full else 'short-review'
    out = HERE / folder
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                                          chromium_sandbox=True, args=['--disable-dev-shm-usage'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 960}, device_scale_factor=1)
        await page.goto(f'http://127.0.0.1:8767/{folder}/playback.html')
        await page.wait_for_function('window.__playbackReport !== undefined', timeout=30000)
        report = await page.evaluate('window.__playbackReport')
        assert report['status'] == 'completed' and report['cycles'] == 3
        assert report['visited_frames_per_cycle'] == [54 if full else 15] * 3
        assert not report['document_hidden_during_playback']
        report['mode'] = 'headless Chromium with sandbox enabled'
        names = ['review-112.gif', 'chat.gif'] if full else ['candidate-112.gif', 'candidate-320.gif']
        report['played_file_sha256'] = {name: hashlib.sha256((out / name).read_bytes()).hexdigest() for name in names}
        await page.screenshot(path=str(out / 'browser-playback-complete.png'), full_page=True)
        (out / 'browser-playback.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report)); await browser.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--full', action='store_true'); args = parser.parse_args()
    asyncio.run(check(args.full))
