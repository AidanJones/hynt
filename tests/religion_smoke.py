import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'test-results';OUT.mkdir(exist_ok=True)
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8001'
with sync_playwright() as p:
    browser=p.chromium.launch(args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist'] if sys.platform=='win32' else ['--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(URL+'/#y=750&l=polity,religion&compare=religion&c=30,30,2.4',wait_until='networkidle')
    page.wait_for_function('window.atlas?.map.loaded()',timeout=60000)
    page.wait_for_function('document.querySelector("#religion-count").textContent.startsWith("2 mapped")')
    assert page.locator('#comparison-map canvas').count()==1
    page.wait_for_function('window.atlas.comparisonMap?.loaded()')
    page.evaluate('window.atlas.map.jumpTo({center:[32,31],zoom:2.5})')
    page.wait_for_function('Math.abs(window.atlas.comparisonMap.getCenter().lng-32)<0.001')
    page.evaluate('window.atlas.comparisonMap.jumpTo({center:[35,32],zoom:2.6})')
    page.wait_for_function('Math.abs(window.atlas.map.getCenter().lng-35)<0.001')
    assert 'Official religion' in page.locator('#religion-mode-label').inner_text()
    page.locator('#religion-list button').filter(has_text='Umayyad').click()
    assert 'majority' in page.locator('#details').inner_text()
    assert page.locator('#details a[href*="metmuseum.org"]').count()==1
    page.screenshot(path=str(OUT/'religion-desktop.png'))
    page.locator('#details .close').click()
    page.locator('#religion-majority-tour').click()
    page.wait_for_function('document.querySelector("#religion-count").textContent.startsWith("1 mapped")')
    page.locator('#religion-list button').click()
    assert '79.8%' in page.locator('#details').inner_text()
    page.locator('#details .close').click()
    page.reload(wait_until='networkidle');page.wait_for_function('window.atlas?.map.loaded()')
    assert page.locator('#religion-kind').input_value()=='majority'
    assert page.locator('#religion-compare').is_checked()
    page.locator('#year-input').fill('2012');page.locator('#year-input').press('Enter')
    page.wait_for_function('document.querySelector("#religion-count").textContent.startsWith("0 mapped")')
    page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.screenshot(path=str(OUT/'religion-mobile.png'))
    page.locator('#religion-compare').uncheck();assert page.locator('#comparison-map').is_hidden()
    assert not errors,errors
    print('Religion type separation, 750 comparison, dated majority, reload and mobile passed.')
    browser.close()
