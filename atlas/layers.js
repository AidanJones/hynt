import {PolityLoader} from './polity-loader.js';
const filterState=new WeakMap(),changePoints=new WeakMap();

export function representativeYear(collection,year) {
  if(!collection?.features.length)return year;
  if(!changePoints.has(collection))changePoints.set(collection,[...new Set(collection.features.flatMap(f=>[f.properties.from,f.properties.to]))].sort((a,b)=>a-b));
  const points=changePoints.get(collection);let low=0,high=points.length-1;
  if(year<points[0])return year;
  while(low<high){const mid=Math.ceil((low+high)/2);if(points[mid]<=year)low=mid;else high=mid-1;}
  return points[low];
}
export const PALETTE = ['#b08b48','#688e83','#bc7861','#7b83a0','#9c995c','#b38d99','#7b9b60','#b88c64','#6293a0','#9a7d56','#b5a059','#8d83a3'];
export function colour(entity) {
  let hash = 0;
  for (const character of entity) hash = ((hash << 5) - hash + character.charCodeAt(0)) | 0;
  return PALETTE[Math.abs(hash) % PALETTE.length];
}
export async function loadJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Could not load ${url} (${response.status})`);
  return response.json();
}
export function makeLayers(map) {
  map.addSource('polities', {type: 'geojson', data: {type: 'FeatureCollection', features: []}});
  map.addLayer({id: 'polity-fill', type: 'fill', source: 'polities', paint: {'fill-color': ['get', 'colour'], 'fill-opacity': 0.58}});
  map.addLayer({id: 'polity-line', type: 'line', source: 'polities', paint: {'line-color': ['get', 'colour'], 'line-width': 1, 'line-opacity': 0.9, 'line-dasharray': [3, 2]}});
  map.addLayer({id: 'polity-focus', type: 'line', source: 'polities', filter: ['==', ['get', 'entity'], ''], paint: {'line-color': '#364a37', 'line-width': 2.5}});
}
export function updateFilters(map, state, opacity, year=state.year, ids=null) {
  const boundsKey=state.bounds?.join(',')||'',confidence=state.confidence||'all';
  const previous=filterState.get(map)||{},temporalChanged=previous.year!==year||previous.focus!==state.focus||previous.boundsKey!==boundsKey||previous.confidence!==confidence||previous.ids!==ids;
  const visibilityChanged=previous.polity!==state.polity,paintChanged=previous.opacity!==opacity||previous.focus!==state.focus;
  const temporal = ['all', ['<=', ['get', 'from'], year], ['>', ['get', 'to'], year]];
  if(ids)temporal.push(['in',['get','id'],['literal',ids]]);
  if(confidence!=='all')temporal.push(['==',['get','confidence'],confidence]);
  for (const layer of ['polity-fill', 'polity-line', 'polity-focus']) {
    if (!map.getLayer(layer)) continue;
    if(temporalChanged)map.setFilter(layer, layer === 'polity-focus' ? ['all', temporal, ['==', ['get', 'entity'], state.focus]] : temporal);
    if(visibilityChanged)map.setLayoutProperty(layer, 'visibility', state.polity ? 'visible' : 'none');
  }
  if (paintChanged&&map.getLayer('polity-fill')) {
    map.setPaintProperty('polity-fill', 'fill-opacity', state.focus ? ['case', ['==', ['get', 'entity'], state.focus], opacity, 0.1] : opacity);
  }
  filterState.set(map,{year,focus:state.focus,polity:state.polity,opacity,boundsKey,confidence,ids});
}
export class EraStore {
  constructor(manifest,{loader=new PolityLoader()}={}) {this.manifest = manifest; this.cache = new Map();this.loader=loader;}
  chunk(year) {return this.manifest.chunks.find(c => c.from <= year && year < c.to);}
  load(chunk) {
    if (!chunk) return Promise.reject(new Error('No data package for this year'));
    if (!this.cache.has(chunk.url)) {
      const url = 'data/' + chunk.url + (chunk.sha256 ? `?v=${chunk.sha256.slice(0,12)}` : '');
      const promise = this.loader.load(url).then(collection => {
        for (const feature of collection.features) feature.properties.colour = colour(feature.properties.entity);
        return collection;
      }).catch(error => {if(this.cache.get(chunk.url)===promise)this.cache.delete(chunk.url); throw error;});
      this.cache.set(chunk.url, promise);
      // Keep recent eras; playback prefetch must not retain the entire atlas.
      if (this.cache.size > 4) this.cache.delete(this.cache.keys().next().value);
    }
    return this.cache.get(chunk.url);
  }
  prefetch(year) {
    const index = this.manifest.chunks.indexOf(this.chunk(year));
    const next = this.manifest.chunks[index + 1];
    if (next) this.load(next).catch(() => {});
  }
}
