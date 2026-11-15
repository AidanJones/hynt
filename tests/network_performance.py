"""Record throttled desktop observations; this does not certify a physical phone."""
import json,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8001'
records=[]
with sync_playwright() as p:
    browser=p.chromium.launch(args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist'] if sys.platform=='win32' else ['--enable-unsafe-swiftshader'])
    for label,bits,latency,viewport in [('broadband-desktop',10_000_000,40,{'width':1440,'height':1000}),('slower-phone-viewport',1_600_000,150,{'width':390,'height':844})]:
        context=browser.new_context(viewport=viewport);page=context.new_page()
        cdp=context.new_cdp_session(page);cdp.send('Network.enable')
        cdp.send('Network.emulateNetworkConditions',{'offline':False,'latency':latency,'downloadThroughput':bits/8,'uploadThroughput':bits/8})
        start=time.perf_counter();page.goto(URL,wait_until='domcontentloaded')
        page.wait_for_function('window.atlas?.features.length>0&&window.atlas.map.queryRenderedFeatures({layers:["polity-fill"]}).length>0',timeout=120000)
        first=time.perf_counter()-start
        page.wait_for_load_state('networkidle')
        renderer=page.evaluate('''()=>{const gl=window.atlas.map.getCanvas().getContext('webgl2'),e=gl.getExtension('WEBGL_debug_renderer_info');return e?gl.getParameter(e.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER)}''')
        bodies=page.evaluate('performance.getEntriesByType("resource").reduce((n,r)=>n+r.encodedBodySize,0)')
        records.append({'case':label,'bits_per_second':bits,'latency_ms':latency,'viewport':viewport,'first_rendered_polity_seconds':round(first,3),'resource_body_bytes':bodies,'renderer':renderer,'browser':browser.version,'physical_phone':False})
        context.close()
    browser.close()
result={'observations':records,'limits':'CDP network throttling on this desktop, cold browser contexts. Small viewport is not a physical phone; local HTTP server and configured latency are not a field network. First render requires visible polity geometry.'}
(ROOT/'test-results').mkdir(exist_ok=True)
(ROOT/'test-results/network-performance.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
