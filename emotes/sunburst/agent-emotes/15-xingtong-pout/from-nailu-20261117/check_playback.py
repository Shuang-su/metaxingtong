"""Verify real timed playback using sandboxed Chromium; requires local server on 8768."""
from pathlib import Path
import asyncio, hashlib, json
from playwright.async_api import async_playwright
HERE = Path(__file__).resolve().parent

async def main():
    out = HERE / 'delivery'
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, chromium_sandbox=True, args=['--disable-dev-shm-usage'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 1050}, device_scale_factor=1)
        await page.goto('http://127.0.0.1:8768/delivery/playback.html')
        await page.wait_for_function("window.__playbackReport && window.__playbackReport.status", timeout=30000)
        report = await page.evaluate('window.__playbackReport')
        assert report['status'] == 'completed' and report['visited_frames_per_cycle'] == [54, 54, 54]
        assert not report['document_hidden_during_playback']
        report['browser_mode'] = 'headless Chromium, sandbox enabled'
        report['played_sha256'] = {name: hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ['chat.gif','review-112.gif']}
        report['displayed_comparison_sha256'] = hashlib.sha256((out/'paired.gif').read_bytes()).hexdigest()
        (out/'browser-playback.json').write_text(json.dumps(report, indent=2)+'\n')
        await page.screenshot(path=str(out/'browser-playback-complete.png'), full_page=True)
        print(json.dumps(report)); await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
