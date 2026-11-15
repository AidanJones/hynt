const matches=new WeakMap();
export function validBounds(bounds) {
  return Array.isArray(bounds)&&bounds.length===4&&bounds.every(Number.isFinite)&&bounds[0]>=-180&&bounds[2]<=180&&bounds[1]>=-90&&bounds[3]<=90&&bounds[0]<bounds[2]&&bounds[1]<bounds[3];
}
function segmentTouches(a,b,[w,s,e,n]) {
  let lo=0,hi=1;const dx=b[0]-a[0],dy=b[1]-a[1];
  for(const [p,q] of [[-dx,a[0]-w],[dx,e-a[0]],[-dy,a[1]-s],[dy,n-a[1]]]) {
    if(p===0){if(q<0)return false;continue;}
    const t=q/p;if(p<0)lo=Math.max(lo,t);else hi=Math.min(hi,t);if(lo>hi)return false;
  }
  return true;
}
function inRing([x,y],ring) {
  let inside=false;
  for(let i=0,j=ring.length-1;i<ring.length;j=i++) {
    const a=ring[i],b=ring[j];
    if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])inside=!inside;
  }
  return inside;
}
export function geometryIntersectsBounds(geometry,bounds) {
  const polygons=geometry.type==='MultiPolygon'?geometry.coordinates:[geometry.coordinates];
  const [w,s,e,n]=bounds;
  for(const rings of polygons) {
    if(!rings[0]?.length)continue;
    for(const ring of rings)for(let i=1;i<ring.length;i++)if(segmentTouches(ring[i-1],ring[i],bounds))return true;
    if([[w,s],[w,n],[e,s],[e,n]].some(p=>inRing(p,rings[0])&&!rings.slice(1).some(h=>inRing(p,h))))return true;
  }
  return false;
}
export function spatialIDs(collection,bounds) {
  if(!bounds||!collection)return null;
  const key=bounds.join(','),previous=matches.get(collection);
  if(previous?.key===key)return previous.ids;
  const ids=collection.features.filter(f=>geometryIntersectsBounds(f.geometry,bounds)).map(f=>f.properties.id);
  matches.set(collection,{key,ids});return ids;
}
export class BoxFilter {
  constructor(map,onChange) {
    this.map=map;this.onChange=onChange;this.start=null;this.armed=false;
    map.addSource('filter-box',{type:'geojson',data:{type:'FeatureCollection',features:[]}});
    map.addLayer({id:'filter-box-line',type:'line',source:'filter-box',paint:{'line-color':'#263b36','line-width':2,'line-dasharray':[2,2]}});
    const button=document.querySelector('#draw-box');
    button.onclick=()=>{this.armed=!this.armed;this.start=null;button.setAttribute('aria-pressed',String(this.armed));button.textContent=this.armed?'Drag a box on the map · cancel':'Draw a geographic box';
      if(this.armed){map.dragPan.disable();map.boxZoom.disable();}else{map.dragPan.enable();map.boxZoom.enable();this.show(this.bounds);}
    };
    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&this.armed){this.start=null;button.click();}});
    map.on('mousedown',e=>{if(!this.armed)return;this.start=[e.lngLat.lng,e.lngLat.lat];});
    map.on('mousemove',e=>{if(this.start)this.show(this.between(this.start,[e.lngLat.lng,e.lngLat.lat]));});
    map.on('mouseup',e=>{
      if(!this.start)return;
      const bounds=this.between(this.start,[e.lngLat.lng,e.lngLat.lat]);this.start=null;this.armed=false;
      map.dragPan.enable();map.boxZoom.enable();button.setAttribute('aria-pressed','false');button.textContent='Draw a geographic box';
      if(validBounds(bounds))this.onChange(bounds);else this.show(this.bounds);
    });
    for(const id of ['west','south','east','north'])document.querySelector(`#box-${id}`).addEventListener('keydown',e=>{if(e.key==='Enter')document.querySelector('#apply-box').click();});
    document.querySelector('#apply-box').onclick=()=>{
      const values=['west','south','east','north'].map(id=>document.querySelector(`#box-${id}`).value.trim());
      const bounds=values.map(Number);
      if(values.every(Boolean)&&validBounds(bounds)){document.querySelector('#box-error').textContent='';this.onChange(bounds);}
      else document.querySelector('#box-error').textContent='Enter west < east (−180 to 180) and south < north (−90 to 90). Use separate windows across the date line.';
    };
    document.querySelector('#clear-box').onclick=()=>this.onChange(null);
  }
  between(a,b){return [Math.min(a[0],b[0]),Math.min(a[1],b[1]),Math.max(a[0],b[0]),Math.max(a[1],b[1])];}
  show(bounds) {
    const features=bounds?[{type:'Feature',properties:{},geometry:{type:'Polygon',coordinates:[[[bounds[0],bounds[1]],[bounds[2],bounds[1]],[bounds[2],bounds[3]],[bounds[0],bounds[3]],[bounds[0],bounds[1]]]]}}]:[];
    this.map.getSource('filter-box').setData({type:'FeatureCollection',features});
  }
  update(bounds) {
    if(JSON.stringify(bounds)===JSON.stringify(this.bounds))return;this.bounds=bounds;
    this.show(bounds);
    ['west','south','east','north'].forEach((id,i)=>{document.querySelector(`#box-${id}`).value=bounds?.[i]??'';});
    document.querySelector('#box-error').textContent='';
  }
}
