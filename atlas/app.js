import {bindTimeline, formatYear} from './timeline.js';
import {readState, writeState} from './state.js';
import {EraStore, loadJSON, makeLayers, updateFilters,representativeYear} from './layers.js';
import {element, showDetails} from './panel.js';
import {TechnologyLayer, visibleAttestations} from './technology.js';
import {BritainLayer} from './britain.js';
import {MigrationLayer} from './migrations.js';
import {bpToCivil} from './chronology.js';

const $ = selector => document.querySelector(selector);
let state = readState(), map, store, sources, entities = [], currentChunk = '', collection = null, ready = false, sequence = 0;
let selectedID = '', opacity = 0.58;
let technologies, selectedTechnology = null;
let britain, selectedBritish = null;
let migrations, selectedMigration = null;
let reviewNotes=[];
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const status = message => {$('#status').textContent = message;};
const timeline = bindTimeline(year => {state.year = year; update();});
timeline.update(state.year);
$('#polity-toggle').checked = state.polity;
$('#technology-toggle').checked = state.technology;
$('#britain-toggle').checked = state.britain;
$('#migration-toggle').checked=state.migration;

function applyPolityFilters() {
  const year=collection?.features.length?representativeYear(collection,state.year):state.year<store.manifest.minimum_year?store.manifest.minimum_year-1:state.year;
  updateFilters(map,state,opacity,year);
}

function syncMigrations() {
  $('#migration-toggle').checked=state.migration;$('#migration-story').value=state.migrationStory;
  if(migrations) {
    migrations.update(state);
    if(selectedMigration&&state.migration)migrations.showDetails(selectedMigration);
    else if(selectedMigration){selectedMigration=null;$('#details').hidden=true;}
  }
}
function selectMigration(record,jump=false) {
  timeline.stop();selectedID='';selectedBritish=null;selectedTechnology=null;selectedMigration=record;
  state.migration=true;state.focus='';$('#clear-focus').hidden=true;
  if(jump) {
    state.year=record.date_from;state.migrationStory=record.id;
    const bounds=record.coordinates.reduce((b,p)=>b.extend(p),new maplibregl.LngLatBounds());
    map.fitBounds(bounds,{maxZoom:3,padding:innerWidth>650?{left:320,right:340,top:130,bottom:250}:35,duration:reducedMotion?0:650});
  }
  update();migrations.showDetails(record);
}

function syncBritain() {
  $('#britain-toggle').checked = state.britain;
  $('#britain-kind').value = state.britainKind; $('#britain-mode').value = state.britainMode;
  if (britain) {
    britain.update(state);
    if (selectedBritish && state.britain) britain.showDetails(selectedBritish,state.year);
    else if (selectedBritish) {selectedBritish = null; $('#details').hidden = true;}
  }
}
function selectBritish(record,jump = false) {
  selectedMigration=null;
  timeline.stop(); selectedID = ''; selectedTechnology = null; selectedBritish = record;
  state.britain = true; state.focus = ''; $('#clear-focus').hidden = true;
  if (jump) {
    state.year = record.date_from; state.britainKind = 'all';
    map.flyTo({center:record.coordinates,zoom:5,duration:reducedMotion ? 0 : 650});
  }
  update(); britain.showDetails(record,state.year);
}

function syncTechnology() {
  $('#technology-toggle').checked = state.technology;
  $('#technology-package').value = state.technologyPackage;
  $('#technology-mode').value = state.technologyMode;
  if (technologies) {
    technologies.update(state);
    if (selectedTechnology && state.technology) technologies.showDetails(selectedTechnology, state.year);
    else if (selectedTechnology) {selectedTechnology = null; $('#details').hidden = true;}
  }
}
function selectTechnology(record, jump = false) {
  selectedMigration=null;
  selectedBritish = null;
  timeline.stop(); selectedID = ''; selectedTechnology = record;
  state.focus = ''; $('#clear-focus').hidden = true;
  state.technology = true;
  if (jump) {
    state.year = record.date_to; state.technologyPackage = record.package;
    map.flyTo({center:record.coordinates, zoom:record.place.includes('regional anchor') ? 2.8 : 4,
      duration:reducedMotion ? 0 : 650});
  }
  update();
  technologies.showDetails(record, state.year);
}

function focusEntity(id) {
  state.focus = id; $('#clear-focus').hidden = !id;
  applyPolityFilters(); writeState(state);
}
function details(feature, candidates) {
  selectedMigration=null;
  selectedBritish = null;
  selectedTechnology = null;
  selectedID = feature.properties.id;
  showDetails(feature, sources, focusEntity, candidates, () => {selectedID = '';},reviewNotes);
}
function countActive() {
  const active = collection?.features.filter(f => f.properties.from <= state.year && state.year < f.properties.to) || [];
  const count = new Set(active.map(f => f.properties.entity)).size;
  $('#feature-count').textContent = state.polity ? `${count.toLocaleString()} polities recorded · ${formatYear(state.year)}` : 'Polity layer hidden';
  const focused = entities.find(e => e.id === state.focus);
  if (state.year < store.manifest.minimum_year) status('Before 3400 BCE: no polity data. Other enabled layers show separate evidence.');
  else if (state.year > store.manifest.coverage_to) status(`No polity data after ${store.manifest.coverage_to}. Borders have not been extrapolated.`);
  else if (!state.polity) status('Polity layer hidden · enable it in map layers.');
  else if (focused) status(`${focused.name} · ${active.some(f => f.properties.entity === focused.id) ? 'recorded in this year' : 'no shape recorded in this year'}`);
  else status(count ? `${count} polities recorded · select a shape to see its sources` : 'No polity records for this year.');
  if (selectedID) {
    const current = active.find(f => f.properties.id === selectedID);
    if (!current) {$('#details').hidden = true; selectedID = '';}
  }
}
async function update() {
  timeline.update(state.year); writeState(state);
  if (!ready) return;
  syncTechnology();
  syncBritain();
  syncMigrations();
  applyPolityFilters();
  const chunk = store.chunk(state.year), request = ++sequence;
  if (!chunk) {
    if(!collection||collection.features.length){collection={type:'FeatureCollection',features:[]};map.getSource('polities').setData(collection);}
    currentChunk = '';selectedID = '';
    if (!selectedTechnology && !selectedBritish && !selectedMigration) $('#details').hidden = true;
    $('#retry').hidden = true; countActive(); return;
  }
  if (chunk.url === currentChunk && collection) {
    countActive();
    if (chunk.to - state.year < 20) store.prefetch(state.year);
    return;
  }
  // Never leave a previous era's polygons visible while another era loads.
  map.getSource('polities').setData({type:'FeatureCollection', features:[]});
  collection = null; currentChunk = ''; selectedID = '';
  if (!selectedTechnology && !selectedBritish && !selectedMigration) $('#details').hidden = true;
  status(`Loading records for ${formatYear(state.year)}…`); $('#retry').hidden = true;
  try {
    const result = await store.load(chunk);
    if (request !== sequence) return;
    collection = result; currentChunk = chunk.url;
    map.getSource('polities').setData(collection);
    applyPolityFilters(); countActive();
    if (chunk.to - state.year < 20) store.prefetch(state.year);
  } catch (error) {
    if (request !== sequence) return;
    status('Historical data could not load. Check the connection and retry.'); $('#retry').hidden = false;
    console.error(error);
  }
}
function fitEntity(id) {
  const entity = entities.find(e => e.id === id);
  if (!entity) return;
  timeline.stop();
  if (!(entity.from <= state.year && state.year < entity.to)) state.year = entity.from;
  focusEntity(id);
  update().then(() => {
    const feature = collection?.features.find(f => f.properties.entity === id && f.properties.from <= state.year && state.year < f.properties.to);
    if (!feature) return;
    const points = feature.geometry.coordinates.flat(feature.geometry.type === 'MultiPolygon' ? 2 : 1);
    const bounds = points.reduce((b, point) => b.extend(point), new maplibregl.LngLatBounds());
    map.fitBounds(bounds, {padding: innerWidth > 650 ? {left:320, right:340, top:120, bottom:240} : 45, maxZoom:5, duration: reducedMotion ? 0 : 700});
    details(feature);
  });
}

$('#search').addEventListener('input', () => {
  const query = $('#search').value.trim().toLocaleLowerCase();
  const results = $('#search-results'); results.replaceChildren(); results.hidden = !query;
  $('#search').setAttribute('aria-expanded', String(!!query));
  if (!query) return;
  const exactName = name => name.toLocaleLowerCase().replace(/^\(|\)$/g,'').trim() === query;
  const matches = entities.filter(e => e.name.toLocaleLowerCase().includes(query))
    .sort((a,b)=>Number(exactName(b.name))-Number(exactName(a.name))||a.name.localeCompare(b.name)).slice(0, 15);
  const evidenceMatches = britain?.data.records.filter(r => `${r.name} ${r.place}`.toLocaleLowerCase().includes(query)) || [];
  for (const record of evidenceMatches.slice(0,8)) {
    const button = element('button',`${record.name} · ${record.date_label} · ${record.kind}`);
    button.onclick = () => {results.hidden = true; $('#search').setAttribute('aria-expanded','false'); $('#search').value = record.name; selectBritish(record,true);};
    results.append(button);
  }
  for (const entity of matches) {
    const button = element('button', `${entity.name} · ${formatYear(entity.from)}`);
    button.onclick = () => {results.hidden = true; $('#search').setAttribute('aria-expanded', 'false'); $('#search').value = entity.name; fitEntity(entity.id);};
    results.append(button);
  }
  if (!matches.length && !evidenceMatches.length) results.append(element('p', 'No matching polity or British evidence in this dataset.'));
});
$('#search').addEventListener('keydown', event => {
  if (event.key === 'ArrowDown') {event.preventDefault(); $('#search-results button')?.focus();}
  if (event.key === 'Escape') {$('#search-results').hidden = true; $('#search').setAttribute('aria-expanded', 'false');}
});
$('#clear-focus').onclick = () => {focusEntity(''); countActive();};
$('#polity-toggle').onchange = event => {state.polity = event.target.checked; update();};
$('#migration-toggle').onchange=event=>{state.migration=event.target.checked;$('#migration-explorer').open=state.migration;update();};
$('#migration-story').onchange=event=>{state.migrationStory=event.target.value;selectedMigration=null;$('#details').hidden=true;update();};
$('#migration-tour').onclick=()=>{
  if(!ready)return;timeline.stop();selectedMigration=null;selectedBritish=null;selectedTechnology=null;selectedID='';$('#details').hidden=true;
  state.year=bpToCivil(100000);state.migration=true;state.migrationStory='all';state.focus='';$('#clear-focus').hidden=true;
  map.flyTo({center:[40,15],zoom:1.5,duration:reducedMotion?0:650});update();
};
$('#technology-toggle').onchange = event => {state.technology = event.target.checked; $('#technology-explorer').open = state.technology; update();};
$('#britain-toggle').onchange = event => {state.britain = event.target.checked; $('#britain-explorer').open = state.britain; update();};
$('#britain-kind').onchange = event => {state.britainKind = event.target.value; selectedBritish = null; $('#details').hidden = true; update();};
$('#britain-mode').onchange = event => {state.britainMode = event.target.value; update();};
$('#britain-tour').onclick = () => {
  if (!ready) return;
  timeline.stop(); selectedBritish = null; selectedTechnology = null; selectedMigration=null; selectedID = ''; $('#details').hidden = true;
  state.year = -700; state.britain = true; state.britainKind = 'all'; state.britainMode = 'cumulative'; state.focus = '';
  $('#clear-focus').hidden = true; $('#britain-explorer').open = true;
  map.fitBounds([[-5.5,51.3],[-2.5,53.6]],{padding:innerWidth > 650 ? {left:320,right:100,top:130,bottom:250} : {left:30,right:30,top:200,bottom:260},duration:reducedMotion ? 0 : 650});
  update();
};
$('#technology-package').onchange = event => {
  state.technologyPackage = event.target.value; selectedTechnology = null; state.focus = ''; $('#clear-focus').hidden = true; $('#details').hidden = true; update();
};
$('#technology-fit').onclick = () => {
  if (!technologies) return;
  const points = visibleAttestations(technologies.data,state.year,state.technologyPackage,state.technologyMode);
  if (!points.length) return;
  const bounds = points.reduce((b,a) => b.extend(a.coordinates),new maplibregl.LngLatBounds());
  map.fitBounds(bounds,{maxZoom:4, padding:innerWidth > 650 ? {left:330,right:$('#details').hidden ? 80 : 350,top:145,bottom:260} : {left:35,right:35,top:150,bottom:280}, duration:reducedMotion ? 0 : 650});
};
$('#technology-mode').onchange = event => {state.technologyMode = event.target.value; update();};
$('#opacity').oninput = event => {opacity = Number(event.target.value) / 100; if (ready) applyPolityFilters();};
$('#retry').onclick = () => ready ? update() : location.reload();
$('#region').onchange = event => {
  const regions = {world:[[-170,-55],[179,75]], mediterranean:[[-12,25],[48,50]], britain:[[-12,49],[3,61]], asia:[[95,5],[145,55]], southasia:[[60,0],[100,38]], africa:[[-20,-35],[53,20]], americas:[[-165,-55],[-30,70]]};
  if (map) map.fitBounds(regions[event.target.value], {padding:innerWidth > 650 ? {left:320, right:70, top:120, bottom:250} : 35, duration:reducedMotion ? 0 : 700});
};
$('#share').onclick = async () => {
  writeState(state);
  try {await navigator.clipboard.writeText(location.href); $('#share').textContent = 'View link copied ✓';}
  catch {$('#share').textContent = 'Copy the URL from the address bar';}
  setTimeout(() => {$('#share').textContent = 'Copy view link ↗';}, 3000);
};
$('#about-button').onclick = () => $('#about').showModal();
$('#close-about').onclick = () => $('#about').close();
window.addEventListener('hashchange', () => {
  timeline.stop(); state = readState(); $('#polity-toggle').checked = state.polity;
  if (technologies && state.technologyPackage !== 'all' && !technologies.packages.has(state.technologyPackage)) state.technologyPackage = 'all';
  if(migrations&&state.migrationStory!=='all'&&!migrations.data.records.some(r=>r.id===state.migrationStory))state.migrationStory='all';
  $('#clear-focus').hidden = !state.focus;
  if (map) map.jumpTo({center:state.camera.slice(0,2), zoom:state.camera[2]});
  update();
});

async function init() {
  if (!window.maplibregl?.Map) throw new Error('MapLibre could not load. Check the local viewer assets.');
  const probe = document.createElement('canvas');
  const context = probe.getContext('webgl2');
  if (!context) throw new Error('WebGL 2 is not available in this browser.');
  context.getExtension('WEBGL_lose_context')?.loseContext();
  const [manifest, sourceData, entityData, technologyData, britainData, migrationData, notes] = await Promise.all(['manifest', 'sources', 'entities', 'technologies', 'britain', 'migrations', 'review-notes'].map(file => loadJSON(`data/${file}.json`)));
  reviewNotes=notes;
  sources = sourceData; entities = entityData; store = new EraStore(manifest);
  if (!entities.some(e => e.id === state.focus)) state.focus = '';
  $('#clear-focus').hidden = !state.focus;
  map = new maplibregl.Map({container:'map', center:state.camera.slice(0,2), zoom:state.camera[2], minZoom:0.5, maxZoom:7,
    renderWorldCopies:false, attributionControl:false,
    style:{version:8, sources:{land:{type:'geojson', data:'data/land.geojson'}}, layers:[
      {id:'water', type:'background', paint:{'background-color':'#dce6e4'}},
      {id:'land', type:'fill', source:'land', paint:{'fill-color':'#eeeade'}},
      {id:'coast', type:'line', source:'land', paint:{'line-color':'#c3cbbf','line-width':0.6}},
    ]}});
  map.addControl(new maplibregl.NavigationControl({showCompass:false}), 'top-right');
  map.addControl(new maplibregl.AttributionControl({compact:true, customAttribution:'Cliopatria / Seshat · CC BY 4.0 | Natural Earth · public domain'}));
  await new Promise((resolve, reject) => {
    map.once('load', resolve);
    map.once('error', event => reject(event.error));
  });
  makeLayers(map);
  technologies = new TechnologyLayer(map, technologyData, selectTechnology, () => {selectedTechnology = null;});
  britain = new BritainLayer(map,britainData,selectBritish,() => {selectedBritish = null;});
  migrations=new MigrationLayer(map,migrationData,selectMigration,()=>{selectedMigration=null;});
  if(state.migrationStory!=='all'&&!migrationData.records.some(r=>r.id===state.migrationStory))state.migrationStory='all';
  $('#migration-explorer').open=state.migration;
  $('#technology-explorer').open = state.technology && state.technologyPackage !== 'all';
  $('#britain-explorer').open = state.britain && state.britainKind !== 'all';
  $('#about').append(element('h3','Britain & Wales evidence'),element('p','A small cited selection of monuments, objects, named rulers and community attestations. Dates may refer to construction, object dating or one historical episode; each record explains which. Regional anchors are illustrative, not borders. The compilation is CC0; linked sources retain their own rights.'));
  const note = element('p','Technology markers are a small curated selection of dated evidence for farming, ironworking, algebra, printing, writing and paper. Regional and city anchors are approximate. Past evidence persists in the cumulative display; it does not imply continued or universal adoption. Dashed connections have their own citations. The original factual compilation is CC0; linked publications retain their own rights.');
  $('#about').append(element('h3','Technology & knowledge'),note);
  if (state.technologyPackage !== 'all' && !technologies.packages.has(state.technologyPackage)) state.technologyPackage = 'all';
  ready = true;
  map.on('moveend', () => {const c = map.getCenter(); state.camera = [c.lng, c.lat, map.getZoom()]; writeState(state);});
  map.on('click', 'polity-fill', event => {
    const ids = [...new Set(event.features.map(f => f.properties.id))];
    const candidates = ids.map(id => collection?.features.find(f => f.properties.id === id)).filter(Boolean);
    if (candidates.length) details(candidates[0], candidates);
  });
  map.on('mouseenter','polity-fill',() => {map.getCanvas().style.cursor = 'pointer';});
  map.on('mouseleave','polity-fill',() => {map.getCanvas().style.cursor = '';});
  map.on('click','migration-routes',event=>{const r=migrationData.records.find(r=>r.id===event.features[0]?.properties.id);if(r)selectMigration(r);});
  map.on('click','technology-links',event => {
    const edge = technologyData.transmissions.find(t => t.id === event.features[0]?.properties.id);
    if (edge) selectTechnology(technologyData.attestations.find(a => a.id === edge.destination));
  });
  map.on('error', () => {status('A map resource failed to load. Reload or retry if the map is incomplete.'); $('#retry').hidden = false;});
  await update();
  // Read-only diagnostics for smoke tests and performance measurements.
  window.atlas = {map, get state() {return {...state};}, get features() {return collection?.features || [];}};
}
init().catch(error => {status(error.message.includes('WebGL') ? error.message : 'The atlas could not start. Check local data files and retry.'); $('#retry').hidden = false; console.error(error);});
