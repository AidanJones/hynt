import {parseYear} from './timeline.js';
const DEFAULT_CAMERA = [22, 24, 1.8];
export function readState(hash = location.hash) {
  const params = new URLSearchParams(hash.replace(/^#/, ''));
  const camera = (params.get('c') || '').split(',').map(Number);
  const validCamera = camera.length === 3 && camera.every(Number.isFinite) && Math.abs(camera[0]) <= 180 && Math.abs(camera[1]) <= 80 && camera[2] >= 0.5 && camera[2] <= 7;
  return {year: parseYear(params.get('y')) ?? 117,
    polity: !params.has('l') || params.get('l').split(',').includes('polity'),
    technology: !params.has('l') || params.get('l').split(',').includes('technology'),
    technologyPackage: /^[a-z-]{1,30}$/.test(params.get('t') || '') ? params.get('t') : 'all',
    technologyMode: params.get('tm') === 'window' ? 'window' : 'cumulative',
    britain: !params.has('l') || params.get('l').split(',').includes('britain'),
    britainKind: ['ruler','site','community','artefact'].includes(params.get('bk')) ? params.get('bk') : 'all',
    britainMode: params.get('bm') === 'window' ? 'window' : 'cumulative',
    migration: params.has('l') && params.get('l').split(',').includes('migration'),
    migrationStory: /^[a-z-]{1,60}$/.test(params.get('m') || '') ? params.get('m') : 'all',
    focus: (params.get('f') || '').slice(0, 120),
    camera: validCamera ? camera : [...DEFAULT_CAMERA]};
}
export function serializeState(state) {
  const params = new URLSearchParams({y: state.year, l: [state.polity && 'polity',state.technology && 'technology',state.britain && 'britain',state.migration && 'migration'].filter(Boolean).join(',')});
  if(state.migrationStory && state.migrationStory!=='all')params.set('m',state.migrationStory);
  if (state.britainKind && state.britainKind !== 'all') params.set('bk',state.britainKind);
  if (state.britainMode === 'window') params.set('bm','window');
  if (state.technologyPackage && state.technologyPackage !== 'all') params.set('t',state.technologyPackage);
  if (state.technologyMode === 'window') params.set('tm','window');
  if (state.focus) params.set('f', state.focus);
  params.set('c', state.camera.map(x => Number(x.toFixed(3))).join(','));
  return '#' + params.toString();
}
export function writeState(state) {
  history.replaceState(null, '', serializeState(state));
}
