import {element, link} from './panel.js';

// Evidence accumulates as a historical record; it is never an adoption/ownership map.
export function visibleAttestations(data, year, packageID = 'all', mode = 'cumulative') {
  return data.attestations.filter(a => (packageID === 'all' || a.package === packageID)
    && a.date_from <= year && (mode !== 'window' || year <= a.date_to));
}
export function visibleTransmissions(data, attestations, year) {
  const ids = new Set(attestations.map(a => a.id));
  const byID = new Map(data.attestations.map(a => [a.id, a]));
  return data.transmissions.filter(t => ids.has(t.origin) && ids.has(t.destination)
    && byID.get(t.destination).date_to <= year);
}
const drawings = {
  mathematics: '<path d="M5 5h14M5 19h14M7 5l7 7-7 7m10-9h4m-2-2v4"/>',
  farming: '<path d="M12 21V5m0 6C5 11 5 6 5 6s7 0 7 5Zm0 5c7 0 7-5 7-5s-7 0-7 5Zm0-10c5 0 5-4 5-4s-5 0-5 4Z"/>',
  iron: '<path d="m5 21 9-12m-4-5 4-2 7 6-4 4-7-6Z"/>',
  algebra: '<path d="m4 9 8 10m0-10L4 19m12-13c0-4 6-4 6 0 0 2-6 5-6 7h6"/>',
  printing: '<path d="M5 3h14v5H5Zm0 13h14v6H5ZM5 18H2V9h20v9h-3M6 12h1m2 7h6"/>',
  writing: '<path d="m4 18 1-5L16 2l5 5-11 11-6 1Zm2-5 4 4M3 22h18"/>',
  paper: '<path d="M5 2h10l5 5v15H5Zm10 0v6h5M8 12h9M8 16h9"/>',
};
export function icon(packageID) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 24 24'); svg.setAttribute('aria-hidden', 'true');
  svg.innerHTML = drawings[packageID] || drawings.printing;
  return svg;
}

export class TechnologyLayer {
  constructor(map, data, onSelect, onHide) {
    this.map = map; this.data = data; this.onSelect = onSelect; this.onHide = onHide; this.markers = [];
    this.packages = new Map(data.packages.map(p => [p.id, p]));
    map.addSource('technology-links', {type:'geojson', data:{type:'FeatureCollection', features:[]}});
    map.addLayer({id:'technology-links', type:'line', source:'technology-links', paint:{'line-color':['get','colour'], 'line-width':2.5, 'line-dasharray':[3,2], 'line-opacity':0.85}});
    for (const p of data.packages) {
      const option = element('option', p.name); option.value = p.id;
      document.querySelector('#technology-package').append(option);
    }
  }
  update(state) {
    this.state = state;
    const active = state.technology ? visibleAttestations(this.data, state.year, state.technologyPackage, state.technologyMode) : [];
    const key = JSON.stringify([state.technology,state.technologyPackage,state.technologyMode,
      active.map(a=>[a.id,state.year<a.date_to]),this.data.attestations.filter(a=>a.date_from>state.year).map(a=>a.id)]);
    if (key === this.renderKey) return;
    this.renderKey = key;
    this.markers.forEach(m => m.remove()); this.markers = [];
    for (const a of active) {
      const p = this.packages.get(a.package), button = element('button', undefined, 'technology-marker');
      button.style.setProperty('--tech-colour', p.colour);
      button.dataset.attestation = a.id;
      button.classList.toggle('uncertain', state.year < a.date_to);
      const title = `${p.name}: ${a.name} · ${a.date_label}${state.year < a.date_to ? ' · within date window' : ''}`;
      button.title = title; button.setAttribute('aria-label', title); button.append(icon(a.package));
      button.onclick = event => {event.stopPropagation(); this.onSelect(a);};
      const marker = new maplibregl.Marker({element:button}).setLngLat(a.coordinates).addTo(this.map);
      this.markers.push(marker);
    }
    const records = new Map(this.data.attestations.map(a => [a.id,a]));
    const edges = visibleTransmissions(this.data, active, state.year);
    this.map.getSource('technology-links').setData({type:'FeatureCollection', features:edges.map(t => ({
      type:'Feature', properties:{id:t.id, colour:this.packages.get(t.package).colour},
      geometry:{type:'LineString', coordinates:[records.get(t.origin).coordinates, records.get(t.destination).coordinates]},
    }))});
    this.renderTrail(active, state);
  }
  renderTrail(active, state) {
    const list = document.querySelector('#technology-trail'); list.replaceChildren();
    document.querySelector('#technology-explorer').hidden = !state.technology;
    const p = this.packages.get(state.technologyPackage);
    document.querySelector('#technology-summary').textContent = p ? p.description : 'Choose a package to follow its evidence through time. Icons mark selected attestations; lines show cited connections.';
    const components = document.querySelector('#technology-components'); components.replaceChildren();
    if (p) for (const component of p.components) components.append(element('span', component));
    const count = document.querySelector('#technology-count');
    count.textContent = `${active.length} records ${state.technologyMode === 'window' ? 'dated to this year' : 'recorded by this year'}`;
    const all = this.data.attestations.filter(a => state.technologyPackage === 'all' || a.package === state.technologyPackage).sort((a,b) => a.date_from - b.date_from);
    for (const a of all) {
      const button = element('button', undefined, 'technology-stop');
      button.classList.toggle('future-stop', a.date_from > state.year);
      button.classList.toggle('current-stop', active.some(record => record.id === a.id));
      button.append(icon(a.package), element('span', a.name), element('small', a.date_label));
      button.onclick = () => this.onSelect(a, true);
      list.append(button);
    }
  }
  showDetails(a, year) {
    const panel = document.querySelector('#details'), p = this.packages.get(a.package);
    panel.replaceChildren(); panel.hidden = false;
    const close = element('button','×','close'); close.setAttribute('aria-label','Close technology details');
    close.onclick = () => {panel.hidden = true; this.onHide();};
    panel.append(close, element('div','TECHNOLOGY & KNOWLEDGE','eyebrow'), element('h2',a.name));
    const badge = element('div',p.name,'technology-heading'); badge.prepend(icon(a.package)); panel.append(badge);
    panel.append(element('p',`${a.place} · ${a.date_label}`));
    panel.append(element('span', year < a.date_from ? 'Not yet within this evidence date' : year < a.date_to ? 'Within the cited date window' : a.approximate ? 'Evidence at an approximate date' : 'Dated attestation', 'badge'));
    panel.append(element('p',a.summary), element('h3','What is evidenced here'));
    const components = element('div',undefined,'technology-components');
    for (const component of a.components) components.append(element('span',component));
    panel.append(components,element('p',a.evidence),element('h3','Reading this marker'),element('p',a.location_note));
    panel.append(element('p','Markers persist as a record of past evidence. They do not establish continuous use, general literacy, or adoption by everyone nearby. No marker means no entry in this small selection.'));
    for (const t of this.data.transmissions.filter(t => t.origin === a.id || t.destination === a.id)) {
      const other = this.data.attestations.find(record => record.id === (t.origin === a.id ? t.destination : t.origin));
      panel.append(element('h3', t.kind), element('p',t.summary));
      const jump = element('button',`Explore ${other.place} · ${other.date_label} ↗`);
      jump.onclick = () => this.onSelect(other, true); panel.append(jump);
    }
    panel.append(element('h3','Sources & evidence'));
    const sourceIDs = new Set([...a.sources, ...this.data.transmissions.filter(t => t.origin === a.id || t.destination === a.id).flatMap(t => t.sources)]);
    for (const id of sourceIDs) {
      const source = this.data.sources[id];
      panel.append(link(source.title,source.url),element('p',source.author),element('p',source.locator));
    }
  }
}
