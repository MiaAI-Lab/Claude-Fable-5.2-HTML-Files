"""Capture real browser screenshots, then verify gallery behavior."""
import asyncio
import hashlib
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright
from build_gallery import ROOT, studies


async def main():
    output = ROOT / 'thumbs'
    output.mkdir(exist_ok=True)
    manifest_path = output / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    updated = {}

    def fingerprint(item):
        image = output / (item['stem'] + '.jpg')
        if not image.exists() or image.stat().st_size < 1000:
            return None
        return {'html': hashlib.sha256((ROOT / item['file']).read_bytes()).hexdigest(),
                'image': hashlib.sha256(image.read_bytes()).hexdigest()}

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        semaphore = asyncio.Semaphore(3)

        async def capture(item):
            current = fingerprint(item)
            if '--refresh' not in sys.argv and current and manifest.get(item['stem']) == current:
                updated[item['stem']] = current
                print(f"Verified existing screenshot: {item['file']}", flush=True)
                return
            async with semaphore:
                context = await browser.new_context(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
                try:
                    page = await context.new_page()
                    await page.goto((ROOT / item['file']).as_uri(), wait_until='load', timeout=60000)
                    await page.evaluate('document.fonts.ready')
                    # Let entrance animations and generative canvases finish their first scene.
                    await page.wait_for_timeout(5000)
                    await page.screenshot(path=str(output / (item['stem'] + '.jpg')), type='jpeg', quality=82, timeout=60000)
                    updated[item['stem']] = fingerprint(item)
                    print(f"Captured {item['file']}", flush=True)
                finally:
                    await context.close()

        await asyncio.gather(*(capture(item) for item in studies()))
        context = await browser.new_context(viewport={'width': 1440, 'height': 1000})
        page = await context.new_page()
        await page.goto((ROOT / 'index.html').as_uri())
        assert await page.title() == 'Claude Fable 5.2 HTML Files'
        assert await page.locator('.card').count() == len(studies())
        await page.locator('#q').fill('suminagashi')
        assert await page.locator('.card:visible').count() == 1
        await page.locator('.card:visible .btn-prompt').click()
        assert await page.locator('#prompt-001').is_visible()
        assert await page.locator('.card:visible .btn-prompt').get_attribute('aria-expanded') == 'true'
        await page.locator('#q').fill('no-study-matches-this-query')
        assert await page.locator('#empty').is_visible()
        await page.locator('#q').fill('')
        for width in (1440, 390, 360):
            await page.set_viewport_size({'width': width, 'height': 1000})
            assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow at {width}px'
        for item in studies():
            assert (output / (item['stem'] + '.jpg')).stat().st_size > 1000
        await context.close()
        await browser.close()
        manifest_path.write_text(json.dumps(updated, indent=2) + '\n')
        print('All screenshots captured; title, search, prompt controls, and responsive layout verified.')


if __name__ == '__main__':
    asyncio.run(main())
