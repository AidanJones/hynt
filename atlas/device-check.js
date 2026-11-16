const $=s=>document.querySelector(s);
let report,wasHidden=false,running=false;
document.addEventListener('visibilitychange',()=>{if(running&&document.hidden)wasHidden=true;});
async function waitFor(predicate,timeout=90000) {
  const start=performance.now();
  while(!predicate()) {
    if(wasHidden)throw Error('The tab became hidden. Run again with the tab visible.');
    if(performance.now()-start>timeout)throw Error('Timed out waiting for rendered map data.');
    await new Promise(resolve=>setTimeout(resolve,50));
  }
}
function ready(win,year) {
  return win?.atlas?.state.year===year&&win.atlas.features.length>0&&win.atlas.map.loaded()
    &&win.atlas.map.queryRenderedFeatures({layers:['polity-fill']}).length>0;
}
function renderer(win) {
  const gl=win.atlas.map.getCanvas().getContext('webgl2'),extension=gl.getExtension('WEBGL_debug_renderer_info');
  return extension?gl.getParameter(extension.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER);
}
async function scrub(win,span) {
  const slider=win.document.querySelector('#year-slider'),start=Number(slider.value),intervals=[],cpu=[];
  let previous;
  for(let i=0;i<120;i++) {
    await new Promise(win.requestAnimationFrame.bind(win));
    if(wasHidden)throw Error('The tab became hidden. Run again with the tab visible.');
    const now=performance.now();if(previous!==undefined)intervals.push(now-previous);previous=now;
    slider.value=start+i%span;
    const before=performance.now();slider.dispatchEvent(new win.Event('input',{bubbles:true}));cpu.push(performance.now()-before);
  }
  intervals.sort((a,b)=>a-b);
  const mean=intervals.reduce((a,b)=>a+b,0)/intervals.length;
  return {updates:120,frame_intervals:intervals.length,mean_frame_ms:mean,p95_frame_ms:intervals[Math.floor(intervals.length*.95)],
    observed_fps:1000/mean,mean_input_cpu_ms:cpu.reduce((a,b)=>a+b,0)/cpu.length};
}
async function loadCase(year,span) {
  $('#check-status').textContent=`Loading ${year} CE and measuring its timeline…`;
  const frame=$('#atlas-frame');frame.hidden=false;
  const start=performance.now();
  await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(Error('Atlas page navigation timed out.')),90000);
    frame.onload=()=>{clearTimeout(timer);resolve();};
    frame.onerror=()=>{clearTimeout(timer);reject(Error('Atlas frame failed to load.'));};
    // A different query forces a page load; changing only the fragment does not.
    frame.src=`./?device-check-case=${year}#y=${year}&l=polity&c=22,24,1.8`;
  });
  const win=frame.contentWindow;await waitFor(()=>ready(win,year));
  const first=performance.now()-start;
  const geometry=win.atlas.map.queryRenderedFeatures({layers:['polity-fill']}).length;
  const result={year,first_rendered_polity_ms:first,rendered_fragments:geometry,renderer:renderer(win),
    viewport:{width:win.innerWidth,height:win.innerHeight},scrub:await scrub(win,span)};
  return {result,win};
}
$('#run-check').onclick=async()=>{
  if(running)return;
  if($('#physical-device').checked&&!$('#device-label').value.trim()){$('#check-status').textContent='Enter the phone/tablet model and browser for a physical-device report.';$('#device-label').focus();return;}
  running=true;wasHidden=document.hidden;document.body.classList.add('running');$('#result').hidden=true;
  report={schema_version:1,recorded_at:new Date().toISOString(),complete:false,
    device:{label:$('#device-label').value.trim(),declared_physical_phone:$('#physical-device').checked,
      user_agent:navigator.userAgent,platform:navigator.platform,max_touch_points:navigator.maxTouchPoints,
      pixel_ratio:devicePixelRatio,screen:{width:screen.width,height:screen.height},hardware_concurrency:navigator.hardwareConcurrency,
      connection:$('#network').value},cases:[],cross_era:[],tab_remained_visible:false,
    limits:'Two short runs in a full-viewport same-origin iframe. HTTP/browser caches may warm after the first case; this is not a cold-network certification. Device identity and connection are self-reported. Frame timing is observed, not guaranteed across workloads.'};
  try {
    await waitFor(()=>!document.hidden);
    let win;
    for(const [year,span] of [[117,80],[1920,30]]) {
      const loaded=await loadCase(year,span);report.cases.push(loaded.result);win=loaded.win;
    }
    for(const year of [1550,1700,1920]) {
      $('#check-status').textContent=`Checking era change to ${year} CE…`;
      const start=performance.now(),input=win.document.querySelector('#year-input');input.value=String(year);
      input.dispatchEvent(new win.KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
      await waitFor(()=>ready(win,year));
      report.cross_era.push({year,rendered_polity_ms:performance.now()-start,rendered_fragments:win.atlas.map.queryRenderedFeatures({layers:['polity-fill']}).length});
    }
    report.tab_remained_visible=!wasHidden;report.complete=true;
    $('#check-status').textContent='Check complete. Copy the report to share the measured results.';
  }catch(error){report.error=error.message;$('#check-status').textContent=error.message;}
  finally {
    running=false;document.body.classList.remove('running');$('#result').hidden=false;
    $('#report').value=JSON.stringify(report,null,2);
  }
};
$('#copy-report').onclick=async()=>{
  try{await navigator.clipboard.writeText($('#report').value);$('#copy-report').textContent='Report copied';}
  catch{$('#report').focus();$('#report').select();$('#check-status').textContent='Select and copy the report text.';}
};
$('#download-report').onclick=()=>{
  const url=URL.createObjectURL(new Blob([$('#report').value],{type:'application/json'})),a=document.createElement('a');
  a.href=url;a.download='hynt-device-report.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};
