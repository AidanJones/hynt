"""Run against a local server: python tests/browser_smoke.py [URL]."""
import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8000'
OUT = Path(__file__).resolve().parents[1] / 'test-results'
OUT.mkdir(exist_ok=True)


def go_year(page, year):
    page.locator('#year-input').fill(str(year))
    page.locator('#year-input').press('Enter')
    page.wait_for_function('y => window.atlas?.state.year === y && !document.querySelector("#status").textContent.startsWith("Loading")', arg=year)
    page.wait_for_function('window.atlas.map.isSourceLoaded("polities")')
    page.wait_for_function('window.atlas.map.loaded()')


with sync_playwright() as p:
    browser = p.chromium.launch(args=['--enable-unsafe-swiftshader'])
    page = browser.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    started = time.monotonic()
    page.goto(URL, wait_until='networkidle')
    page.wait_for_function('window.atlas?.map.loaded()', timeout=60000)
    first_view_seconds = time.monotonic() - started
    results = []
    for year in [-3400, 117, 1280, 1920, 2026]:
        go_year(page, year)
        count = page.evaluate('window.atlas.map.queryRenderedFeatures({layers:["polity-fill"]}).length')
        assert (count > 0) if year < 2026 else count == 0, (year, count)
        results.append({'year': year, 'rendered_fragments': count})
    assert 'not been extrapolated' in page.locator('#status').inner_text()
    go_year(page, -1)
    page.locator('#next').click()
    assert page.locator('#year-output').inner_text() == '1 CE'
    page.locator('#previous').click()
    assert page.locator('#year-output').inner_text() == '1 BCE'
    go_year(page, 117)
    page.locator('#technology-toggle').uncheck()
    page.locator('#britain-toggle').uncheck()
    page.locator('#search').fill('Roman Empire')
    page.locator('#search-results button').filter(has_text='Roman Empire ·').first.click()
    page.wait_for_function('window.atlas.map.loaded() && !window.atlas.map.isMoving()')
    assert page.locator('#details').is_visible()
    assert page.locator('#details a').filter(has_text='Cliopatria').count() == 1
    assert page.locator('#details a').filter(has_text='Wikipedia').count() == 1
    page.locator('#details .close').click()
    # Click a real rendered polygon away from the control panels.
    point = page.evaluate('''() => {
      const m = window.atlas.map;
      for (let y=160; y<650; y+=15) for (let x=340; x<1080; x+=15)
        if(m.queryRenderedFeatures([x,y],{layers:['polity-fill']}).some(f=>f.properties.name==='Roman Empire')) return {x,y};
      return null;
    }''')
    assert point, 'Rome should have a visible clickable polygon'
    page.mouse.click(point['x'], point['y'])
    assert page.locator('#details h2').inner_text() == 'Roman Empire'
    page.screenshot(path=str(OUT / 'desktop.png'))
    page.locator('#details .close').click()
    page.locator('#polity-toggle').uncheck()
    assert page.evaluate('window.atlas.map.getLayoutProperty("polity-fill","visibility")') == 'none'
    page.reload(wait_until='networkidle')
    page.wait_for_function('window.atlas?.map.loaded()')
    assert not page.locator('#polity-toggle').is_checked(), 'Hash must preserve hidden layer'
    page.locator('#polity-toggle').check()
    page.locator('#play').click()
    page.wait_for_function('window.atlas.state.year > 117')
    page.locator('#play').click()
    page.locator('#about-button').click()
    assert page.locator('#about').is_visible()
    page.keyboard.press('Escape')
    page.set_viewport_size({'width':390, 'height':844})
    go_year(page, 117)
    page.wait_for_function('window.atlas.map.loaded()')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    assert page.locator('#year-slider').is_visible()
    page.screenshot(path=str(OUT / 'mobile.png'))
    assert not errors, errors
    # Technology evidence is independent of polity coverage and has its own dates.
    page.set_viewport_size({'width':1440, 'height':1000})
    page.locator('#technology-toggle').check()
    page.locator('#technology-package').select_option('algebra')
    go_year(page, 825)
    assert page.locator('.technology-marker').count() == 1
    assert page.locator('.technology-marker.uncertain').count() == 1
    go_year(page, 1145)
    assert page.locator('.technology-marker').count() == 2
    page.locator('#technology-fit').click()
    page.wait_for_function('!window.atlas.map.isMoving()')
    page.wait_for_function('window.atlas.map.isSourceLoaded("technology-links")')
    assert page.evaluate('window.atlas.map.querySourceFeatures("technology-links").length') > 0
    page.locator('.technology-journey summary').click()
    page.locator('.technology-stop').filter(has_text='Robert of Chester').click()
    assert page.locator('#details h2').inner_text() == 'Robert of Chester’s Latin translation'
    assert page.locator('#details a').filter(has_text='Euclid').count() == 1
    page.wait_for_function('!window.atlas.map.isMoving()')
    page.screenshot(path=str(OUT / 'technology-desktop.png'))
    page.locator('#details .close').click()
    page.reload(wait_until='networkidle')
    page.wait_for_function('window.atlas?.map.loaded()')
    assert page.locator('#technology-package').input_value() == 'algebra'
    assert page.locator('#technology-toggle').is_checked()
    page.locator('#technology-mode').select_option('window')
    go_year(page, 2026)
    assert page.locator('.technology-marker').count() == 0
    page.locator('#technology-package').select_option('farming')
    page.locator('#technology-mode').select_option('cumulative')
    go_year(page, -9000)
    assert page.locator('.technology-marker').count() == 1
    assert page.evaluate('window.atlas.map.queryRenderedFeatures({layers:["polity-fill"]}).length') == 0
    assert 'Before 3400 BCE' in page.locator('#status').inner_text()
    page.set_viewport_size({'width':390, 'height':844})
    page.locator('.technology-journey summary').click()
    page.locator('.technology-stop').filter(has_text='Cereal cultivation').click()
    page.wait_for_function('!window.atlas.map.isMoving()')
    page.screenshot(path=str(OUT / 'technology-mobile.png'))
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.locator('#details .close').click()
    assert not errors, errors
    # Britain/Wales has its own chronology and point evidence, not invented borders.
    page.set_viewport_size({'width':1440,'height':1000})
    page.locator('#britain-toggle').check()
    page.locator('#britain-tour').click()
    page.wait_for_function('window.atlas.state.year === -700 && !window.atlas.map.isMoving()')
    assert page.locator('[data-britain-record="llyn-fawr"]').count() == 1
    assert page.locator('[data-britain-record="caratacus"]').count() == 0
    page.locator('#search').fill('Caratacus')
    page.locator('#search-results button').filter(has_text='Caratacus').click()
    page.wait_for_function('window.atlas.state.year === 51 && !window.atlas.map.isMoving()')
    assert page.locator('#details h2').inner_text() == 'Caratacus / Caradog'
    assert 'disputed' in page.locator('#details').inner_text()
    assert page.locator('#details a[href="https://coflein.gov.uk/en/sites/403831"]').count() == 1
    page.screenshot(path=str(OUT/'britain-desktop.png'))
    page.locator('#details .close').click()
    page.locator('#britain-kind').select_option('ruler')
    page.locator('#britain-mode').select_option('window')
    assert page.locator('.britain-marker').count() == 1
    page.reload(wait_until='networkidle')
    page.wait_for_function('window.atlas?.map.loaded()')
    assert page.locator('#britain-kind').input_value() == 'ruler'
    assert page.locator('#britain-mode').input_value() == 'window'
    go_year(page,52)
    assert page.locator('.britain-marker').count() == 0
    page.locator('#britain-tour').click()
    page.wait_for_function('!window.atlas.map.isMoving()')
    page.set_viewport_size({'width':390,'height':844})
    page.locator('#britain-explorer>details>summary').click()
    page.locator('.britain-stop').filter(has_text='Llyn Fawr').click()
    page.wait_for_function('!window.atlas.map.isMoving()')
    assert page.locator('#details h2').inner_text() == 'Llyn Fawr · bronze and iron deposits'
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path=str(OUT/'britain-mobile.png'))
    page.locator('#details .close').click()
    assert not errors, errors
    # Failed chunk must show a recoverable error rather than stale polygons.
    page.route('**/data/polities/*', lambda route: route.fulfill(status=503, body='Unavailable'))
    go_year(page, -2500)
    assert page.locator('#retry').is_visible()
    assert page.evaluate('window.atlas.map.queryRenderedFeatures({layers:["polity-fill"]}).length') == 0
    page.unroute('**/data/polities/*')
    page.locator('#retry').click()
    page.wait_for_function('document.querySelector("#retry").hidden && window.atlas.features.length > 0')
    report = {'first_view_local_seconds': round(first_view_seconds, 2), 'years':results,
              'page_errors':errors, 'desktop':[1440,1000], 'mobile':[390,844]}
    (OUT / 'browser-results.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    browser.close()
