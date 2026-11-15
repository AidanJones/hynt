import {formatYear} from './timeline.js';
export function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
export function link(text, url) {
  const a = element('a', text);
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== 'https:') return element('span', text);
    a.href = parsed.href; a.target = '_blank'; a.rel = 'noopener noreferrer';
  } catch {return element('span', text);}
  return a;
}
export function showDetails(feature, sources, onFocus, candidates = [], onClose = () => {}, reviewNotes = []) {
  const panel = document.querySelector('#details');
  panel.replaceChildren(); panel.hidden = false;
  const p = feature.properties;
  const close = element('button', '×', 'close'); close.setAttribute('aria-label', 'Close polity details');
  close.onclick = () => {panel.hidden = true; onClose();}; panel.append(close);
  panel.append(element('div', 'THE HISTORICAL RECORD', 'eyebrow'), element('h2', p.name));
  panel.append(element('p', `${formatYear(p.from)} – ${formatYear(p.display_to ?? p.source_to)} · ${p.kind}`));
  if(p.date_note)panel.append(element('p',p.date_note));
  if(p.identity_note)panel.append(element('h3','Reviewed identity correction'),element('p',p.identity_note),link('Identity reference',p.identity_source));
  for(const note of reviewNotes.filter(n=>n.entity===p.entity&&n.from<p.to&&p.from<n.to)) {
    panel.append(element('h3','Interpretation note'),element('p',note.text));
    for(const source of note.sources)panel.append(link(source.title,source.url));
  }
  panel.append(element('span', 'Confidence · not assessed', 'badge'));
  panel.append(element('p', 'Approximate claimed or controlled territory. The source supplies no per-feature confidence rating; the dashed outline does not indicate a measured level of uncertainty.'));
  panel.append(element('p', `${Math.round(p.area_km2).toLocaleString('en-GB')} km² · source-reported area for this shape`));
  const focus = element('button', 'Follow this polity through time ↗'); focus.onclick = () => onFocus(p.entity); panel.append(focus);
  panel.append(element('h3', 'Sources & evidence'));
  for (const id of p.sources) {
    const source = sources[id];
    if (!source) continue;
    panel.append(link(source.title, source.url), element('p', source.citation));
    panel.append(link(source.licence, source.licence_url), element('p', source.changes));
  }
  panel.append(element('h3', 'Further reading'));
  if (p.wikipedia) panel.append(link('Read on Wikipedia ↗', 'https://en.wikipedia.org/wiki/' + encodeURIComponent(p.wikipedia.replaceAll(' ', '_'))));
  if (p.wikidata) {panel.append(element('br')); panel.append(link('View structured evidence on Wikidata ↗', 'https://www.wikidata.org/wiki/' + encodeURIComponent(p.wikidata)));}
  if (candidates.length > 1) {
    panel.append(element('h3', 'Also recorded at this location'));
    for (const candidate of candidates.filter(c => c.properties.id !== p.id)) {
      const button = element('button', candidate.properties.name, 'candidate');
      button.onclick = () => showDetails(candidate, sources, onFocus, candidates, onClose, reviewNotes); panel.append(button);
    }
    panel.append(element('p', 'Overlaps are preserved from the source. They may represent competing claims or dataset inconsistencies.'));
  }
}
