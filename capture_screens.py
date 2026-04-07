"""Capture all 34 storyboard screens as PNG screenshots with focus outlines suppressed."""
import asyncio
from playwright.async_api import async_playwright

SCREENS = {
    "sc-mvp-01": [1, 2, 3, 4, 5, 6, 7, 8],
    "sc-mvp-02": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
    "sc-mvp-03": [20, 21, 22, 23, 24, 25, 26, 27, 28],
    "sc-mvp-04": [29, 30, 31, 32, 33, 34],
}

ORDERED = []
for scenario, ids in SCREENS.items():
    for idx, screen_id in enumerate(ids, 1):
        ORDERED.append((scenario, idx, screen_id))

URL = "http://localhost:63417/index.html"
OUT = r"C:\Users\brady.redfearn\Projects\jft-sdp-storyboard\screenshots"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto(URL, wait_until="networkidle")

        # Suppress ALL focus outlines globally
        await page.add_style_tag(content="*:focus, *:focus-visible { outline: none !important; box-shadow: none !important; border-color: inherit !important; }")

        for scenario, step, screen_id in ORDERED:
            await page.evaluate(f"goToScreen({screen_id})")
            # Blur any focused element to remove outline
            await page.evaluate("document.activeElement?.blur()")
            await page.wait_for_timeout(300)
            fname = f"{OUT}/{scenario}_step{step:02d}_screen{screen_id:02d}.png"
            await page.screenshot(path=fname, full_page=False)
            print(f"Captured: {fname}")

        await browser.close()
        print(f"\nDone — {len(ORDERED)} screenshots recaptured to {OUT}")

asyncio.run(main())
