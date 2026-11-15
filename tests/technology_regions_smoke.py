"""Verify regional evidence, explicit assumptions, research links and URL state."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'test-results';OUT.mkdir(exist_ok=True)
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8001'

with sync_playwright() as p:
    browser=p.chromium.launch(args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist'] if sys.platform=='win32' else ['--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(URL+'/#y=117&t=writing&tc=polity&l=technology',wait_until='networkidle')
    page.wait_for_function('window.atlas?.map.loaded()',timeout=60000)
    assert 'inferred only' in page.locator('#technology-region-count').inner_text()
    page.locator('#technology-regional-controls details>summary').click()
    page.locator('#technology-area').fill('Europe')
    page.locator('#technology-research').select_option('inferred')
    page.locator('#technology-region-list button').first.click()
    assert 'optional polity assumption' in page.locator('#details').inner_text().lower()
    assert 'Seed:' in page.locator('#details').inner_text()
    assert page.locator('#details a[href*="wikipedia.org/w/index.php"]').count()==1
    assert page.locator('#details a[href*="cliopatria/tree"]').count()==1
    page.screenshot(path=str(OUT/'technology-regions-desktop.png'))
    page.reload(wait_until='networkidle');page.wait_for_function('window.atlas?.map.loaded()')
    assert page.locator('#technology-coverage').input_value()=='polity'
    page.locator('#technology-coverage').select_option('evidence')
    assert '0 inferred only' in page.locator('#technology-region-count').inner_text()
    page.locator('#technology-package').select_option('mathematics')
    page.locator('#year-input').fill('1700 BCE');page.locator('#year-input').press('Enter')
    assert page.locator('[data-attestation="math-ybc7289"]').count()==1
    page.locator('#technology-regional-controls details>summary').click()
    page.locator('#technology-area').fill('Africa');page.locator('#technology-research').select_option('direct')
    page.locator('#technology-region-list button').first.click()
    assert 'Moscow Mathematical Papyrus' in page.locator('#details').inner_text()
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.screenshot(path=str(OUT/'technology-regions-mobile.png'))
    page.locator('#details .close').click()
    page.locator('#technology-coverage').select_option('off')
    assert page.locator('#technology-regional-controls').is_hidden()
    assert not errors,errors
    print('Regional technology desktop/mobile, chronology, assumptions, citations and reload passed.')
    browser.close()
