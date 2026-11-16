import {parseYear} from './timeline.js';
import {validBounds} from './spatial.js';
const DEFAULT_CAMERA = [22, 24, 1.8];
export function readState(hash = location.hash) {
  const params = new URLSearchParams(hash.replace(/^#/, ''));
  const camera = (params.get('c') || '').split(',').map(Number);
  const boundParts=(params.get('box')||'').split(',');
  const bounds=boundParts.every(v=>v.trim()!=='')?boundParts.map(Number):[];
  const validCamera = camera.length === 3 && camera.every(Number.isFinite) && Math.abs(camera[0]) <= 180 && Math.abs(camera[1]) <= 80 && camera[2] >= 0.5 && camera[2] <= 7;
  return {year: parseYear(params.get('y')) ?? 117,
    polity: !params.has('l') || params.get('l').split(',').includes('polity'),
    technology: !params.has('l') || params.get('l').split(',').includes('technology'),
    technologyPackage: /^[a-z-]{1,30}$/.test(params.get('t') || '') ? params.get('t') : 'all',
    technologyMode: params.get('tm') === 'window' ? 'window' : 'cumulative',
    technologyCoverage: ['off','polity'].includes(params.get('tc')) ? params.get('tc') : 'evidence',
    events: params.has('l') && params.get('l').split(',').includes('events'),
    religion: params.has('l') && params.get('l').split(',').includes('religion'),
    religionKind: params.get('rk')==='majority'?'majority':'official',
    compareReligion: params.get('compare')==='religion',
    ranking: params.get('rank')==='1',
    bounds: validBounds(bounds)?bounds:null,
    confidence: params.get('confidence')==='unknown'?'unknown':'all',
    eventCategory: ['battle','landing','political','founding','religious','technology','catastrophe'].includes(params.get('ec')) ? params.get('ec') : 'all',
    campaignDay: /^\d{1,3}$/.test(params.get('day')||'') && Number(params.get('day'))>=1 && Number(params.get('day'))<=365 ? Number(params.get('day')) : 365,
    britain: !params.has('l') || params.get('l').split(',').includes('britain'),
    britainKind: ['ruler','site','community','artefact'].includes(params.get('bk')) ? params.get('bk') : 'all',
    britainMode: params.get('bm') === 'window' ? 'window' : 'cumulative',
    migration: params.has('l') && params.get('l').split(',').includes('migration'),
    cultures: params.has('l') && params.get('l').split(',').includes('cultures'),
    cultureKind: ['culture:jomon','culture:ubaid','culture:narva'].includes(params.get('culture'))?params.get('culture'):'all',
    migrationStory: /^[a-z-]{1,60}$/.test(params.get('m') || '') ? params.get('m') : 'all',
    focus: (params.get('f') || '').slice(0, 120),
    camera: validCamera ? camera : [...DEFAULT_CAMERA]};
}
export function serializeState(state) {
  const params = new URLSearchParams({y: state.year, l: [state.polity && 'polity',state.technology && 'technology',state.britain && 'britain',state.migration && 'migration',state.events && 'events',state.religion && 'religion',state.cultures&&'cultures'].filter(Boolean).join(',')});
  if(state.cultureKind&&state.cultureKind!=='all')params.set('culture',state.cultureKind);
  if(state.religionKind==='majority')params.set('rk','majority');
  if(state.compareReligion)params.set('compare','religion');
  if(state.ranking)params.set('rank','1');
  if(state.bounds)params.set('box',state.bounds.join(','));
  if(state.confidence==='unknown')params.set('confidence','unknown');
  if(state.eventCategory&&state.eventCategory!=='all')params.set('ec',state.eventCategory);
  if(state.campaignDay&&state.campaignDay!==365)params.set('day',state.campaignDay);
  if(state.migrationStory && state.migrationStory!=='all')params.set('m',state.migrationStory);
  if (state.britainKind && state.britainKind !== 'all') params.set('bk',state.britainKind);
  if (state.britainMode === 'window') params.set('bm','window');
  if (state.technologyPackage && state.technologyPackage !== 'all') params.set('t',state.technologyPackage);
  if (state.technologyMode === 'window') params.set('tm','window');
  if (state.technologyCoverage && state.technologyCoverage !== 'evidence') params.set('tc',state.technologyCoverage);
  if (state.focus) params.set('f', state.focus);
  params.set('c', state.camera.map(x => Number(x.toFixed(3))).join(','));
  return '#' + params.toString();
}
export function writeState(state) {
  history.replaceState(null, '', serializeState(state));
}
