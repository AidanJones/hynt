import {element,link} from './panel.js';
import {ordinal} from './chronology.js';

export function migrationProgress(record,year) {
  if(year<record.date_from) return 0;
  if(year>=record.date_to) return 1;
  return (ordinal(year)-ordinal(record.date_from))/(ordinal(record.date_to)-ordinal(record.date_from));
}
export function routePrefix(coordinates,progress) {
  if(progress<=0) return [];
  if(progress>=1) return coordinates;
  const position=(coordinates.length-1)*progress,index=Math.floor(position),fraction=position-index;
  const from=coordinates[index],to=coordinates[index+1];
  return [...coordinates.slice(0,index+1),[from[0]+(to[0]-from[0])*fraction,from[1]+(to[1]-from[1])*fraction]];
}
export class MigrationLayer {
  constructor(map,data,onSelect,onClose) {
    this.map=map;this.data=data;this.onSelect=onSelect;this.onClose=onClose;this.markers=[];
    map.addSource('migrations',{type:'geojson',data:{type:'FeatureCollection',features:[]}});
    map.addLayer({id:'migration-routes',type:'line',source:'migrations',paint:{'line-color':['get','colour'],'line-width':3,'line-dasharray':[2,2],'line-opacity':0.85}});
    for(const record of data.records) {
      const option=element('option',record.name); option.value=record.id;document.querySelector('#migration-story').append(option);
    }
  }
  update(state) {
    const active=state.migration ? this.data.records.filter(r=>(state.migrationStory==='all'||state.migrationStory===r.id)&&state.year>=r.date_from) : [];
    const key=JSON.stringify([state.migration,state.migrationStory,active.map(r=>[r.id,r.kind==='route'?migrationProgress(r,state.year):state.year<r.date_to])]);
    if(key===this.key)return;this.key=key;
    this.markers.forEach(m=>m.remove());this.markers=[];
    const features=[];
    for(const r of active) {
      const progress=migrationProgress(r,state.year);
      const prefix=r.kind==='route'?(progress===0?[r.coordinates[0]]:routePrefix(r.coordinates,progress)):r.coordinates;
      if(r.kind==='route'&&prefix.length>=2) features.push({type:'Feature',properties:{id:r.id,colour:r.colour},geometry:{type:'LineString',coordinates:prefix}});
      if(!prefix.length)continue;
      const button=element('button',r.kind==='route'?'➤':'◎','migration-marker');
      button.dataset.migration=r.id;button.title=`${r.name} · ${r.date_label}`;button.setAttribute('aria-label',button.title);button.style.background=r.colour;
      button.onclick=event=>{event.stopPropagation();this.onSelect(r);};
      let rotation=0;
      if(r.kind==='route'){
        const from=prefix.length>1?prefix.at(-2):r.coordinates[0],to=prefix.length>1?prefix.at(-1):r.coordinates[1];
        rotation=Math.atan2(to[1]-from[1],(to[0]-from[0])*Math.cos(from[1]*Math.PI/180))*-180/Math.PI;
      }
      this.markers.push(new maplibregl.Marker({element:button,rotation,rotationAlignment:'map'}).setLngLat(prefix.at(-1)).addTo(this.map));
    }
    this.map.getSource('migrations').setData({type:'FeatureCollection',features});
    document.querySelector('#migration-explorer').hidden=!state.migration;
    document.querySelector('#migration-count').textContent=active.length?`${active.length} stories reached this date · past evidence retained`:'No curated migration/site record for this year';
    const list=document.querySelector('#migration-list');list.replaceChildren();
    for(const r of this.data.records) {
      const button=element('button',`${r.name} · ${r.date_label}`,'britain-stop');button.onclick=()=>this.onSelect(r,true);list.append(button);
    }
  }
  showDetails(r) {
    const panel=document.querySelector('#details');panel.replaceChildren();panel.hidden=false;
    const close=element('button','×','close');close.setAttribute('aria-label','Close migration details');close.onclick=()=>{panel.hidden=true;this.onClose();};
    panel.append(close,element('div','MIGRATIONS & DATED PRESENCE','eyebrow'),element('h2',r.name),element('span',r.date_label,'badge'));
    panel.append(element('p',r.summary),element('h3','Interpretation & uncertainty'),element('p',r.caveat));
    panel.append(element('p','Present-day coastlines provide orientation only. Ice-age land, sea levels and shorelines differed. A route arrow is a schematic model; a circle is evidence at a site. Neither marks a uniform people or fixed territory.'));
    panel.append(element('h3','Sources & evidence'));
    for(const id of r.sources){const source=this.data.sources[id];panel.append(link(source.title,source.url),element('p',source.author),element('p',source.locator));}
  }
}
