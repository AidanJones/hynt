import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'test-results';OUT.mkdir(exist_ok=True)
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8001'
with sync_playwright() as p:
    browser=p.chromium.launch(args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist'] if sys.platform=='win32' else ['--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(URL+'/#y=117&l=polity&rank=1',wait_until='networkidle');page.wait_for_function('window.atlas?.map.loaded()',timeout=60000)
    assert page.locator('#ranking-list button').count()==10
    page.locator('#ranking-list button').filter(has_text='Roman Empire').click()
    page.wait_for_function('!window.atlas.map.isMoving()')
    assert page.locator('#entity-lifespan svg').count()==1
    assert 'Peak mapped extent' in page.locator('#entity-lifespan').inner_text()
    page.locator('#details .close').click()
    page.locator('#focus-filters>summary').click()
    for id,value in [('west','-6'),('south','50'),('east','2'),('north','56')]:page.locator('#box-'+id).fill(value)
    page.locator('#apply-box').click()
    assert 'touching window' in page.locator('#feature-count').inner_text()
    assert page.evaluate('window.atlas.state.bounds')==[-6,50,2,56]
    assert 'literal' in page.evaluate('JSON.stringify(window.atlas.map.getFilter("polity-fill"))')
    page.locator('#confidence-filter').select_option('unknown')
    page.reload(wait_until='networkidle');page.wait_for_function('window.atlas?.map.loaded()')
    assert page.evaluate('window.atlas.state.bounds')==[-6,50,2,56]
    assert page.locator('#confidence-filter').input_value()=='unknown'
    page.screenshot(path=str(OUT/'ranking-focus-desktop.png'))
    page.locator('#focus-filters>summary').click()
    page.locator('#box-west').fill('20');page.locator('#box-east').fill('-20');page.locator('#apply-box').click()
    assert 'west < east' in page.locator('#box-error').inner_text()
    page.locator('#clear-box').click();assert page.evaluate('window.atlas.state.bounds') is None
    page.locator('#draw-box').click();page.mouse.move(800,250);page.mouse.down();page.mouse.move(1000,450,steps=8);page.mouse.up()
    assert page.evaluate('window.atlas.state.bounds') is not None
    assert page.locator('#draw-box').get_attribute('aria-pressed')=='false'
    page.locator('#clear-box').click()
    page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.screenshot(path=str(OUT/'ranking-focus-mobile.png'))
    assert not errors,errors
    print('Territorial leaderboard, lifespan, spatial/confidence filters, reload and mobile passed.')
    browser.close()
