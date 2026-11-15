"""Local byte and scrub benchmark; results are observations, not device certification."""
import json
import platform
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8001'
with sync_playwright() as p:
    browser=p.chromium.launch(args=['--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1440,'height':1000})
    page.goto(URL,wait_until='networkidle')
    page.wait_for_function('window.atlas?.map.loaded()',timeout=60000)
    resources=page.evaluate('performance.getEntriesByType("resource").map(r=>({name:r.name,bytes:r.encodedBodySize,duration:r.duration}))')
    assert not any('http' in r['name'] and not r['name'].startswith(URL) for r in resources), 'Viewer should not need external resources'
    benchmark=page.evaluate('''async()=>{
      const slider=document.querySelector('#year-slider'), start=Number(slider.value), times=[];
      const marker=document.querySelector('.technology-marker');
      let previous=performance.now();
      for(let i=0;i<120;i++) {
        await new Promise(requestAnimationFrame);
        const now=performance.now(); times.push(now-previous); previous=now;
        slider.value=start+i%80;
        slider.dispatchEvent(new Event('input',{bubbles:true}));
      }
      times.shift(); times.sort((a,b)=>a-b);
      const mean=times.reduce((a,b)=>a+b,0)/times.length;
      return {frames:times.length,mean_frame_ms:mean,p95_frame_ms:times[Math.floor(times.length*.95)],
        observed_fps:1000/mean,stable_technology_marker:marker===document.querySelector('.technology-marker')};
    }''')
    assert benchmark['stable_technology_marker'], 'Scrubbing unchanged evidence should reuse its DOM markers'
    report={'environment':{'os':platform.platform(),'browser':browser.version,'renderer':'headless Chromium, SwiftShader software WebGL','viewport':[1440,1000]},
            'initial_resource_bytes':sum(r['bytes'] for r in resources),'scrub':benchmark,
            'limits':'Loopback benchmark within one loaded era, 120 UI updates. Does not certify network, physical GPU, cross-era loads, mobile or 60fps on user devices.'}
    (ROOT/'test-results').mkdir(exist_ok=True)
    (ROOT/'test-results/performance.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2)); browser.close()
