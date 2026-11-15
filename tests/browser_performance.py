"""Local byte and scrub benchmark; results are observations, not device certification."""
import json
import platform
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8001'
LABEL=sys.argv[2] if len(sys.argv)>2 else 'current'
HARDWARE='--hardware' in sys.argv
TARGET_YEAR=int(next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--year=')),'117'))
MOBILE='--mobile' in sys.argv
manifest=json.loads((ROOT/'atlas/data/manifest.json').read_text())
chunk=next(c for c in manifest['chunks'] if c['from']<=TARGET_YEAR<c['to'])
SPAN=min(80,chunk['to']-TARGET_YEAR)
with sync_playwright() as p:
    browser=p.chromium.launch(args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist'] if HARDWARE else ['--enable-unsafe-swiftshader'])
    viewport={'width':390,'height':844} if MOBILE else {'width':1440,'height':1000}
    page=browser.new_page(viewport=viewport)
    page.goto(URL+f'#y={TARGET_YEAR}',wait_until='networkidle')
    page.wait_for_function('window.atlas?.map.loaded()',timeout=60000)
    assert page.evaluate('window.atlas.features.length>0'),page.locator('#status').inner_text()
    assert page.evaluate('window.atlas.map.queryRenderedFeatures({layers:["polity-fill"]}).length>0'),'Benchmark must render actual polity polygons'
    renderer=page.evaluate('''()=>{const gl=window.atlas.map.getCanvas().getContext('webgl2');const info=gl.getExtension('WEBGL_debug_renderer_info');return info?gl.getParameter(info.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER);}''')
    resources=page.evaluate('performance.getEntriesByType("resource").map(r=>({name:r.name,bytes:r.encodedBodySize,duration:r.duration}))')
    assert not any('http' in r['name'] and not r['name'].startswith(URL) for r in resources), 'Viewer should not need external resources'
    benchmark=page.evaluate('''async(span)=>{
      const slider=document.querySelector('#year-slider'), start=Number(slider.value), times=[];
      const marker=document.querySelector('.technology-marker'),cpu=[],operations={setFilter:0,setLayoutProperty:0,setPaintProperty:0};
      for(const name of Object.keys(operations)){const original=window.atlas.map[name].bind(window.atlas.map);window.atlas.map[name]=(...args)=>{operations[name]++;return original(...args);};}
      let previous=performance.now();
      for(let i=0;i<120;i++) {
        await new Promise(requestAnimationFrame);
        const now=performance.now(); times.push(now-previous); previous=now;
        slider.value=start+i%span;
        const before=performance.now();slider.dispatchEvent(new Event('input',{bubbles:true}));cpu.push(performance.now()-before);
      }
      times.shift(); times.sort((a,b)=>a-b);
      const mean=times.reduce((a,b)=>a+b,0)/times.length;
      return {frames:times.length,mean_frame_ms:mean,p95_frame_ms:times[Math.floor(times.length*.95)],
        observed_fps:1000/mean,mean_input_cpu_ms:cpu.reduce((a,b)=>a+b,0)/cpu.length,operations,stable_technology_marker:marker===document.querySelector('.technology-marker')};
    }''',SPAN)
    assert benchmark['stable_technology_marker'], 'Scrubbing unchanged evidence should reuse its DOM markers'
    report={'label':LABEL,'year':TARGET_YEAR,'span_years':SPAN,'environment':{'os':platform.platform(),'browser':browser.version,'renderer':renderer,'requested_hardware':HARDWARE,'viewport':list(viewport.values()),'mobile_viewport_only':MOBILE},
            'initial_resource_bytes':sum(r['bytes'] for r in resources),'scrub':benchmark,
            'limits':'Loopback benchmark within one loaded era, 120 UI updates with rendered polygons. Renderer is reported explicitly; does not certify networks, cross-era loads, phones or universal 60fps.'}
    (ROOT/'test-results').mkdir(exist_ok=True)
    (ROOT/'test-results/performance.json').write_text(json.dumps(report,indent=2))
    (ROOT/f'test-results/performance-{LABEL}.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2)); browser.close()
