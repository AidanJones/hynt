"""Exercise expanded technologies and deep-time stories in a real browser."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'test-results';OUT.mkdir(exist_ok=True)
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8001'

def year(page,text):
    page.locator('#year-input').fill(text);page.locator('#year-input').press('Enter')
    page.wait_for_function('!document.querySelector("#status").textContent.startsWith("Loading")')

with sync_playwright() as p:
    browser=p.chromium.launch(args=['--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(URL,wait_until='networkidle');page.wait_for_function('window.atlas?.map.loaded()',timeout=60000)
    if page.locator('#technology-explorer').get_attribute('open') is None:page.locator('#technology-explorer>summary').click()
    page.locator('#technology-package').select_option('writing');year(page,'1200 BCE')
    assert page.locator('[data-attestation="writing-anyang"]').count()==1
    assert page.locator('[data-attestation="writing-uruk"]').count()==1
    page.locator('#technology-package').select_option('paper');year(page,'950')
    assert page.locator('.technology-marker').count()==2
    page.locator('.technology-journey>summary').click()
    page.locator('#technology-trail button').filter(has_text='Paper cut-out').click()
    assert page.locator('#details a').filter(has_text='1978.546.42').count()==1
    page.locator('#details .close').click()
    page.locator('#technology-toggle').uncheck();page.locator('#britain-toggle').uncheck()
    page.locator('#migration-toggle').check();page.locator('#migration-tour').click()
    page.wait_for_function('window.atlas.state.year===-98051&&!window.atlas.map.isMoving()')
    assert page.locator('#year-output').inner_text()=='100,000 BP'
    assert page.locator('.migration-marker').count()==0
    page.locator('#year-slider').focus();page.keyboard.press('ArrowRight')
    assert page.locator('#year-output').inner_text()=='99,000 BP'
    year(page,'55000 BP')
    assert page.locator('[data-migration="later-out-of-africa"]').count()==1
    assert page.locator('[data-migration="madjedbebe"]').count()==1
    assert page.locator('[data-migration="white-sands"]').count()==0
    page.wait_for_function('window.atlas.map.isSourceLoaded("migrations")')
    assert page.evaluate('window.atlas.map.querySourceFeatures("migrations").length')>0
    year(page,'45000 BP');assert page.locator('[data-migration="bacho-kiro"]').count()==1
    year(page,'22000 BP');assert page.locator('[data-migration="white-sands"]').count()==1
    page.locator('#migration-explorer>details>summary').click()
    page.locator('#migration-list button').filter(has_text='White Sands').click()
    page.wait_for_function('!window.atlas.map.isMoving()')
    assert 'route' in page.locator('#details').inner_text().lower()
    assert page.locator('#details a[href*="usgs.gov"]').count()==1
    page.screenshot(path=str(OUT/'migration-desktop.png'))
    page.reload(wait_until='networkidle');page.wait_for_function('window.atlas?.map.loaded()')
    assert page.locator('#migration-story').input_value()=='white-sands'
    assert page.locator('#year-output').inner_text()=='23,000 BP'
    page.set_viewport_size({'width':390,'height':844})
    page.locator('#migration-explorer>details>summary').click()
    page.locator('#migration-list button').filter(has_text='Madjedbebe').click()
    page.wait_for_function('!window.atlas.map.isMoving()')
    assert page.locator('#details h2').inner_text()=='Sahul · Madjedbebe occupation'
    assert 'OSL' in page.locator('#details').inner_text()
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.screenshot(path=str(OUT/'migration-mobile.png'))
    assert not errors,errors
    print('Expanded technology and migration desktop/mobile checks passed.')
    browser.close()
