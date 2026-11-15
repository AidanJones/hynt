"""Check that date decisions and historical interpretation notes reach the viewer."""
import sys,re
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8001'
with sync_playwright() as p:
    browser=p.chromium.launch(args=['--enable-unsafe-swiftshader']);page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(URL,wait_until='networkidle');page.wait_for_function('window.atlas?.map.loaded()',timeout=60000)
    for year,name,expected in [('-1','Roman Empire','upstream inclusive endpoint'),('1280','Mongol Empire','separate khanates'),('1920','British Empire','double-count')]:
        page.locator('#year-input').fill(year);page.locator('#year-input').press('Enter')
        page.wait_for_function('!document.querySelector("#status").textContent.startsWith("Loading")')
        page.locator('#search').fill(name)
        page.locator('#search-results button').filter(has_text=re.compile(r'^\(?'+re.escape(name)+r'\)? ·')).first.click()
        page.wait_for_function('!document.querySelector("#details").hidden')
        assert expected in page.locator('#details').inner_text(),page.locator('#details').inner_text()
        if year=='-1':assert '0 CE' not in page.locator('#details').inner_text()
        page.locator('#details .close').click()
    assert not errors,errors
    print('Date-boundary explanation and Mongol/British interpretation notes passed.')
    browser.close()
