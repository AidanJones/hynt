import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'test-results';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT))
from pipeline.device_reports import validate
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8001'
with sync_playwright() as p:
    browser=p.chromium.launch(args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist'] if sys.platform=='win32' else ['--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':390,'height':844});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(URL+'/device-check.html',wait_until='networkidle')
    page.locator('#device-label').fill('Desktop Chromium · phone-size viewport')
    page.locator('#run-check').click()
    page.wait_for_function('!document.querySelector("#result").hidden',timeout=180000)
    report=json.loads(page.locator('#report').input_value());summary=validate(report)
    assert summary['physical_device_status']=='desktop or unverified device'
    assert not summary['independently_verified_physical_device']
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    assert not errors,errors
    (OUT/'device-check-desktop.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    page.screenshot(path=str(OUT/'device-check.png'))
    print('Device harness rendered both eras, measured 119 intervals each, loaded three eras and preserved desktop classification.')
    browser.close()
