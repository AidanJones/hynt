import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'test-results';OUT.mkdir(exist_ok=True)
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8001'
with sync_playwright() as p:
    browser=p.chromium.launch(args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist'] if sys.platform=='win32' else ['--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(URL+'/#y=1066&l=events',wait_until='networkidle');page.wait_for_function('window.atlas?.map.loaded()',timeout=60000)
    assert page.locator('[data-event="hastings"]').count()==1
    assert page.locator('[data-event="stamford-bridge"]').count()==1
    assert page.locator('[data-event="harald-1066"]').count()==1
    page.locator('#campaign-day').fill('268');page.locator('#campaign-day').dispatch_event('input')
    assert page.locator('[data-event="hastings"]').count()==0
    assert page.locator('[data-event="stamford-bridge"]').count()==1
    page.reload(wait_until='networkidle');page.wait_for_function('window.atlas?.map.loaded()')
    assert page.locator('#campaign-day').input_value()=='268'
    page.locator('#event-explorer>details>summary').click()
    page.locator('#event-list button').filter(has_text='William · landing').click()
    assert 'Dated anchors' in page.locator('#details').inner_text() or 'DATED ANCHORS' in page.locator('#details').inner_text()
    assert page.locator('#details a[href*="historicengland.org.uk"]').count()>0
    page.screenshot(path=str(OUT/'events-desktop.png'))
    page.locator('#details .close').click()
    page.locator('#event-list button').filter(has_text='Western imperial office').click()
    assert page.evaluate('window.atlas.state.year')==476
    assert 'Italy' in page.locator('#details').inner_text()
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.screenshot(path=str(OUT/'events-mobile.png'))
    assert not errors,errors
    print('1066 dated campaigns/events, 476 relation, sources, mobile and reload passed.')
    browser.close()
