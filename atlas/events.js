import {element,link} from './panel.js';
export function dayOfYear(iso) {
  const year=Number(iso.slice(0,4));
  return (Date.parse(iso+'T00:00:00Z')-Date.parse(`${year}-01-01T00:00:00Z`))/86400000+1;
}
export function campaignPrefix(campaign,day) {
  const points=campaign.waypoints;
  if(day<dayOfYear(points[0].date))return [];
  const result=[points[0].coordinates];
  for(let i=1;i<points.length;i++) {
    const a=points[i-1],b=points[i],start=dayOfYear(a.date),end=dayOfYear(b.date);
    if(day>=end){result.push(b.coordinates);continue;}
    const t=(day-start)/(end-start);
    if(t>0)result.push(a.coordinates.map((v,j)=>v+(b.coordinates[j]-v)*t));
    break;
  }
  return result;
}
export function activeEvents(data,state) {
  return state.events?data.events.filter(e=>e.year===state.year&&(state.eventCategory==='all'||e.category===state.eventCategory)
    &&(!e.date||dayOfYear(e.date)<=state.campaignDay)):[];
}
export class EventsLayer {
  constructor(map,data,onSelect) {
    this.map=map;this.data=data;this.onSelect=onSelect;this.markers=[];this.selected=null;
    map.addSource('campaigns',{type:'geojson',data:{type:'FeatureCollection',features:[]}});
    map.addLayer({id:'campaign-lines',type:'line',source:'campaigns',paint:{'line-color':['get','colour'],'line-width':3,'line-dasharray':[3,2]}});
    map.on('click','campaign-lines',e=>{const r=[...data.campaigns,...data.relations].find(c=>c.id===e.features[0]?.properties.id);if(r)this.select(r);});
  }
  select(r,jump=false) {this.onSelect(r,jump);this.selected=r;this.showDetails(r);}
  clear() {this.selected=null;}
  update(state) {
    this.state=state;
    document.querySelector('#event-explorer').hidden=!state.events;
    document.querySelector('#campaign-date-controls').hidden=!state.events||!this.data.campaigns.some(c=>c.year===state.year);
    if(!state.events) {
      if(this.key!=='off'){this.markers.forEach(m=>m.remove());this.markers=[];this.map.getSource('campaigns').setData({type:'FeatureCollection',features:[]});this.key='off';}
      if(this.selected){this.clear();document.querySelector('#details').hidden=true;}
      return;
    }
    const key=JSON.stringify([state.events,state.year,state.eventCategory,state.campaignDay]);
    if(key===this.key)return;this.key=key;
    this.markers.forEach(m=>m.remove());this.markers=[];
    const events=activeEvents(this.data,state),features=[];
    const addMarker=(r,coordinates,text,rotation=0)=>{
      const button=element('button',text,'migration-marker');button.style.background=r.colour||'#9d523a';button.dataset.event=r.id;
      button.title=r.name||`${r.origin} → ${r.destination}`;button.setAttribute('aria-label',button.title);button.onclick=e=>{e.stopPropagation();this.select(r);};
      this.markers.push(new maplibregl.Marker({element:button,rotation,rotationAlignment:'map'}).setLngLat(coordinates).addTo(map));
    };
    const map=this.map;
    for(const e of events)addMarker(e,e.coordinates,e.category==='battle'?'⚔':'◆');
    if(state.events)for(const c of this.data.campaigns.filter(c=>c.year===state.year&&(state.eventCategory==='all'||state.eventCategory==='battle'))) {
      const prefix=campaignPrefix(c,state.campaignDay);if(!prefix.length)continue;
      if(prefix.length>1)features.push({type:'Feature',properties:{id:c.id,colour:c.colour},geometry:{type:'LineString',coordinates:prefix}});
      const a=prefix.at(-2)||prefix[0],b=prefix.at(-1);
      const rotation=prefix.length>1?-Math.atan2(b[1]-a[1],(b[0]-a[0])*Math.cos(a[1]*Math.PI/180))*180/Math.PI:0;
      addMarker(c,b,'➤',rotation);
    }
    if(state.eventCategory==='all'||state.eventCategory==='political')for(const r of this.data.relations.filter(r=>r.year===state.year)) {
      features.push({type:'Feature',properties:{id:r.id,colour:'#526d65'},geometry:{type:'LineString',coordinates:r.coordinates}});
    }
    map.getSource('campaigns').setData({type:'FeatureCollection',features});
    const date=new Date(Date.UTC(state.year,0,state.campaignDay));
    document.querySelector('#campaign-date').textContent=`${date.toLocaleDateString('en-GB',{day:'numeric',month:'short',timeZone:'UTC'})} ${state.year}`;
    document.querySelector('#campaign-day').value=state.campaignDay;
    const list=document.querySelector('#event-list');list.replaceChildren();
    document.querySelector('#event-count').textContent=`${events.length} events in this year and category · selected coverage`;
    for(const e of [...this.data.events,...this.data.campaigns,...this.data.relations]) {
      if(state.eventCategory!=='all'&&e.category&&e.category!==state.eventCategory)continue;
      const button=element('button',`${e.name||`${e.origin} → ${e.destination}`} · ${e.date||e.year}`,'britain-stop');
      button.onclick=()=>this.select(e,true);list.append(button);
    }
    if(this.selected&&!state.events){this.clear();document.querySelector('#details').hidden=true;}
    else if(this.selected)this.showDetails(this.selected);
  }
  showDetails(r) {
    const panel=document.querySelector('#details');panel.replaceChildren();panel.hidden=false;
    const close=element('button','×','close');close.setAttribute('aria-label','Close event details');close.onclick=()=>{this.clear();panel.hidden=true;};
    panel.append(close,element('div',r.waypoints?'DATED CAMPAIGN':r.origin?'CITED RELATION':'HISTORICAL EVENT','eyebrow'),element('h2',r.name||`${r.origin} → ${r.destination}`),element('p',r.date||`${r.year} CE`),element('p',r.summary));
    if(r.waypoints) {
      panel.append(element('p',`${r.attacker} · against ${r.defender}`),element('p',r.outcome),element('h3','Dated anchors'));
      for(const w of r.waypoints)panel.append(element('p',`${w.date} · ${w.name}`));
      panel.append(element('p','Dashed arrows interpolate between dated anchors for illustration. Intermediate paths and travel speeds are not observed. Use the day slider to explore the sequence.'));
    }
    if(r.kind)panel.append(element('span',r.kind,'badge'));
    panel.append(element('span','Location approximate · confidence not assessed','badge'),element('h3','Sources'));
    for(const id of r.sources){const s=this.data.sources[id];panel.append(link(s.title,s.url),element('p',s.author),element('p',s.locator));}
  }
}
