import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'test-results';OUT.mkdir(exist_ok=True)
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8001'
with sync_playwright() as p:
    browser=p.chromium.launch(args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist'] if sys.platform=='win32' else ['--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(URL+'/review.html',wait_until='networkidle');page.wait_for_selector('#review-results article')
    page.locator('#review-search').fill('Han Dynasty');assert page.locator('#review-results article').count()==0
    page.locator('#review-search').fill('');page.locator('#review-kind').select_option('temporal')
    assert 'concurrent records' in page.locator('#review-results').inner_text()
    page.locator('#review-kind').select_option('spatial');assert page.locator('#review-results article a').first.get_attribute('href').startswith('./#y=')
    page.goto(URL+'/#y=117&l=polity',wait_until='networkidle');page.wait_for_function('window.atlas?.map.loaded()')
    page.locator('#search').fill('Han Dynasty');page.locator('#search-results button').first.click()
    page.wait_for_function('!window.atlas.map.isMoving()')
    assert page.evaluate('window.atlas.state.focus')=='Q7209'
    assert 'Reviewed identity correction' in page.locator('#details').inner_text() or 'REVIEWED IDENTITY CORRECTION' in page.locator('#details').inner_text()
    assert page.locator('#details a[href="https://www.wikidata.org/wiki/Q7209"]').count()>=1
    page.locator('#details .close').click()
    page.locator('#focus-filters>summary').click();page.locator('#draw-box').click();page.keyboard.press('Escape')
    assert page.locator('#draw-box').get_attribute('aria-pressed')=='false'
    page.locator('#year-slider').focus();page.keyboard.press('ArrowRight')
    assert page.evaluate('window.atlas.state.year')==118
    page.set_viewport_size({'width':390,'height':844})
    page.locator('#controls-toggle').click();assert page.locator('#map-controls').is_hidden()
    page.locator('#controls-toggle').click();assert page.locator('#map-controls').is_visible()
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.screenshot(path=str(OUT/'polish-mobile.png'))
    assert not errors,errors
    print('Source review, corrected identity, keyboard timeline, draw cancellation and mobile controls passed.')
    browser.close()
