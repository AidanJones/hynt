import {element, link} from './panel.js';

export function visibleBritishRecords(data, year, kind = 'all', mode = 'cumulative') {
  return data.records.filter(r => (kind === 'all' || r.kind === kind)
    && r.date_from <= year && (mode !== 'window' || year <= r.date_to));
}
const SIGNS = {site:'⌂', artefact:'◇', ruler:'♛', community:'◉'};

export class BritainLayer {
  constructor(map, data, onSelect, onClose) {
    this.map = map; this.data = data; this.onSelect = onSelect; this.onClose = onClose; this.markers = [];
  }
  update(state) {
    const records = state.britain ? visibleBritishRecords(this.data,state.year,state.britainKind,state.britainMode) : [];
    const key = JSON.stringify([state.britain,state.britainKind,state.britainMode,records.map(r=>r.id),this.data.records.filter(r=>r.date_from>state.year).map(r=>r.id)]);
    if (key === this.renderKey) return;
    this.renderKey = key;
    this.markers.forEach(m => m.remove()); this.markers = [];
    for (const r of records) {
      const button = element('button',SIGNS[r.kind],`britain-marker britain-${r.kind}`);
      button.title = `${r.name} · ${r.date_label}`; button.setAttribute('aria-label',button.title);
      button.dataset.britainRecord = r.id;
      button.onclick = event => {event.stopPropagation(); this.onSelect(r);};
      this.markers.push(new maplibregl.Marker({element:button}).setLngLat(r.coordinates).addTo(this.map));
    }
    document.querySelector('#britain-explorer').hidden = !state.britain;
    document.querySelector('#britain-count').textContent = `${records.length} records ${state.britainMode === 'window' ? 'whose dating overlaps this year' : 'recorded by this year'}`;
    const list = document.querySelector('#britain-list'); list.replaceChildren();
    const all = this.data.records.filter(r => state.britainKind === 'all' || r.kind === state.britainKind).sort((a,b) => a.date_from - b.date_from);
    for (const record of all) {
      const button = element('button',undefined,'britain-stop');
      button.classList.toggle('future-stop',record.date_from > state.year);
      button.append(element('span',`${SIGNS[record.kind]} ${record.name}`),element('small',`${record.kind} · ${record.date_label}`));
      button.onclick = () => this.onSelect(record,true); list.append(button);
    }
  }
  showDetails(record, year) {
    const panel = document.querySelector('#details'); panel.replaceChildren(); panel.hidden = false;
    const close = element('button','×','close'); close.setAttribute('aria-label','Close British evidence details');
    close.onclick = () => {panel.hidden = true; this.onClose();};
    panel.append(close,element('div','BRITAIN & WALES · EVIDENCE','eyebrow'),element('h2',record.name));
    panel.append(element('p',`${record.kind} · ${record.place}`),element('span',record.date_label,'badge'));
    if (!(record.date_from <= year && year <= record.date_to)) panel.append(element('p','This is an earlier evidence record; its dating does not overlap the selected year.'));
    panel.append(element('p',record.summary),element('h3','What the dates mean'),element('p',record.date_basis));
    panel.append(element('h3','What the location means'),element('p',record.location_note));
    panel.append(element('p','Points are evidence anchors, not state borders. A recorded name or object does not establish an ethnically uniform territory or uninterrupted occupation. No marker means no entry in this small selection.'));
    if (record.related.length) {
      panel.append(element('h3','Related evidence'));
      for (const id of record.related) {
        const other = this.data.records.find(r => r.id === id), button = element('button',`${other.name} ↗`,'candidate');
        button.onclick = () => this.onSelect(other,true); panel.append(button);
      }
    }
    panel.append(element('h3','Sources & evidence'));
    for (const id of record.sources) {
      const source = this.data.sources[id]; panel.append(link(source.title,source.url),element('p',source.author),element('p',source.locator));
    }
  }
}
