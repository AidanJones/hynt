"""Check worker decode errors, retries and out-of-order era responses."""
import asyncio
import sys
from playwright.async_api import async_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8001'

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist'])
        page=await browser.new_page(viewport={'width':1440,'height':1000})
        await page.goto(URL,wait_until='networkidle')
        await page.wait_for_function('window.atlas?.map.loaded()',timeout=60000)
        async def delayed(route):
            await asyncio.sleep(1)
            await route.continue_()
        await page.route('**/era_1700_1800.json.gz*',delayed)
        async def year(value):
            await page.locator('#year-input').fill(str(value));await page.locator('#year-input').press('Enter')
        await year(1750);await year(1920)
        await page.wait_for_function('window.atlas.state.year===1920&&window.atlas.features.length>0&&!document.querySelector("#status").textContent.startsWith("Loading")')
        await asyncio.sleep(1.5)
        assert await page.evaluate('window.atlas.features.every(f=>f.properties.from<1950&&f.properties.to>1900)')
        assert 'y=1920' in page.url
        await page.route('**/era_1500_1600.json.gz*',lambda route:route.fulfill(status=200,body=bytes([31,139,0,1])))
        await year(1550)
        await page.wait_for_function('!document.querySelector("#retry").hidden')
        assert await page.evaluate('window.atlas.features.length===0')
        await page.unroute('**/era_1500_1600.json.gz*')
        await page.locator('#retry').click()
        await page.wait_for_function('document.querySelector("#retry").hidden&&window.atlas.features.length>0&&window.atlas.map.loaded()')
        assert await page.evaluate('window.atlas.map.queryRenderedFeatures({layers:["polity-fill"]}).length>0')
        print('Cross-era race, corrupt worker decode and retry passed.')
        await browser.close()

asyncio.run(main())
