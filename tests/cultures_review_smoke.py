import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'test-results';OUT.mkdir(exist_ok=True)
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8001'
with sync_playwright() as p:
    browser=p.chromium.launch(args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist'] if sys.platform=='win32' else ['--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(URL+'/#y=-5000&l=cultures&c=30,40,2.2',wait_until='networkidle');page.wait_for_function('window.atlas?.map.loaded()',timeout=60000)
    page.wait_for_function('document.querySelector("#culture-count").textContent.startsWith("3 selected")')
    page.locator('#culture-explorer>details>summary').click()
    page.locator('#culture-list button').filter(has_text='Ubaid').click();page.wait_for_function('!window.atlas.map.isMoving()')
    assert 'display assumption' in page.locator('#details').inner_text()
    assert page.locator('#details a[href="data/cultures/LICENSE.txt"]').count()==1
    assert page.locator('#details a[href*="metmuseum.org"]').count()==1
    page.wait_for_function('window.atlas.map.queryRenderedFeatures({layers:["culture-fill"]}).length>0')
    page.screenshot(path=str(OUT/'cultures-desktop.png'))
    page.locator('#details .close').click();page.reload(wait_until='networkidle');page.wait_for_function('window.atlas?.map.loaded()')
    assert page.locator('#culture-kind').input_value()=='culture:ubaid'
    page.locator('#year-input').fill('4000 BCE');page.locator('#year-input').press('Enter')
    assert page.locator('#culture-count').inner_text().startswith('0 selected')
    page.locator('#culture-kind').select_option('all');page.locator('#culture-tour').click()
    page.set_viewport_size({'width':390,'height':844});page.locator('#culture-tour').click();page.locator('#controls-toggle').click()
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.screenshot(path=str(OUT/'cultures-mobile.png'))
    page.goto(URL+'/review.html',wait_until='networkidle');page.locator('#review-kind').select_option('references')
    page.locator('#review-filter').select_option('corrected');assert page.locator('#review-results article').count()>0
    assert page.locator('#review-results a[href*="oldid="]').count()>0
    assert 'NaN' not in page.locator('#review-results').inner_text()
    page.locator('#review-filter').select_option('all');page.locator('#review-kind').select_option('temporal');page.locator('#review-filter').select_option('identical footprint')
    assert 'identical footprint' in page.locator('#review-results').inner_text()
    assert not errors,errors
    print('Culture polygons, provenance, timeline/filter state, mobile and classified review queue passed.')
    browser.close()
