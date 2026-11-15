import {element,link} from './panel.js';
export function religionFeatures(collection,data,year,kind) {
  const records=data.records.filter(r=>r.kind===kind&&r.from<=year&&year<r.to);
  return {type:'FeatureCollection',features:(collection?.features||[]).filter(f=>f.properties.from<=year&&year<f.properties.to)
    .flatMap(f=>records.filter(r=>r.entity===f.properties.entity).map(r=>({...f,properties:{...f.properties,religion_id:r.id,religion:r.religion,colour:r.colour}})))};
}
function addReligionLayers(map,before) {
  map.addSource('religion',{type:'geojson',data:{type:'FeatureCollection',features:[]}});
  map.addLayer({id:'religion-fill',type:'fill',source:'religion',paint:{'fill-color':['get','colour'],'fill-opacity':0.72}},before);
  map.addLayer({id:'religion-line',type:'line',source:'religion',paint:{'line-color':['get','colour'],'line-width':1.5,'line-dasharray':[3,2]}},before);
}
export class ReligionLayer {
  constructor(map,data,onSelect) {
    this.map=map;this.data=data;this.onSelect=onSelect;this.selected=null;this.compare=null;
    addReligionLayers(map,'polity-line');
    this.bindClick(map);
  }
  bindClick(map) {map.on('click','religion-fill',event=>{
    const id=event.features[0]?.properties.religion_id;
    const record=this.data.records.find(r=>r.id===id);if(record)this.select(record);
  });}
  select(record) {this.onSelect();this.selected=record;this.showDetails(record);}
  clear() {this.selected=null;}
  async ensureComparison() {
    if(this.promise)return this.promise;
    const center=this.map.getCenter();
    this.compare=new maplibregl.Map({container:'comparison-map',center:[center.lng,center.lat],zoom:this.map.getZoom(),minZoom:0.5,maxZoom:7,
      renderWorldCopies:false,attributionControl:false,style:{version:8,sources:{land:{type:'geojson',data:'data/land.geojson'}},layers:[
        {id:'water',type:'background',paint:{'background-color':'#dce6e4'}},
        {id:'land',type:'fill',source:'land',paint:{'fill-color':'#eeeade'}},
        {id:'coast',type:'line',source:'land',paint:{'line-color':'#c3cbbf','line-width':0.6}}]}});
    this.promise=new Promise((resolve,reject)=>{this.compare.once('load',resolve);this.compare.once('error',e=>reject(e.error));}).then(()=>{
      addReligionLayers(this.compare);this.bindClick(this.compare);this.comparisonReady=true;
      let syncing=false;
      for(const [a,b] of [[this.map,this.compare],[this.compare,this.map]])a.on('move',()=>{
        if(syncing||!this.state?.compareReligion)return;syncing=true;
        const c=a.getCenter();b.jumpTo({center:[c.lng,c.lat],zoom:a.getZoom(),bearing:a.getBearing(),pitch:a.getPitch()});syncing=false;
      });
      const c=this.map.getCenter();this.compare.jumpTo({center:[c.lng,c.lat],zoom:this.map.getZoom(),bearing:this.map.getBearing(),pitch:this.map.getPitch()});
      this.update(this.state,this.collection);
    }).catch(()=>{
      this.compare?.remove();this.compare=null;this.promise=null;
      document.querySelector('#religion-count').textContent='Comparison map could not load. Toggle comparison to retry.';
    });
    return this.promise;
  }
  update(state,collection) {
    this.state=state;this.collection=collection;
    document.querySelector('#religion-explorer').hidden=!state.religion;
    document.body.classList.toggle('religion-compare',state.religion&&state.compareReligion);
    document.querySelector('#comparison-map').hidden=!(state.religion&&state.compareReligion);
    document.querySelector('#compare-labels').hidden=!(state.religion&&state.compareReligion);
    document.querySelector('#religion-mode-label').textContent=state.religionKind==='official'?'Official religion of ruler/state · selected evidence':'Population majority · dated national observation';
    if(state.religion&&state.compareReligion){this.ensureComparison();this.compare?.resize();}
    const result=state.religion?religionFeatures(collection,this.data,state.year,state.religionKind):{type:'FeatureCollection',features:[]};
    const key=JSON.stringify([state.religion,state.religionKind,state.compareReligion,result.features.map(f=>[f.properties.id,f.properties.religion_id])]);
    if(key!==this.key||this.lastComparisonReady!==this.comparisonReady) {
      this.key=key;this.lastComparisonReady=this.comparisonReady;
      this.map.getSource('religion').setData(state.compareReligion?{type:'FeatureCollection',features:[]}:result);
      if(this.comparisonReady)this.compare.getSource('religion').setData(result);
      const active=this.data.records.filter(r=>r.kind===state.religionKind&&r.from<=state.year&&state.year<r.to);
      document.querySelector('#religion-count').textContent=`${new Set(result.features.map(f=>f.properties.entity)).size} mapped polity proxies · ${active.length} active observations. Blank land means no record, not no religion.`;
      const list=document.querySelector('#religion-list');list.replaceChildren();
      for(const r of active){const button=element('button',r.name,'britain-stop');button.onclick=()=>this.select(r);list.append(button);}
    }
    if(this.selected&&(!state.religion||this.selected.kind!==state.religionKind||state.year<this.selected.from||state.year>=this.selected.to)){this.clear();document.querySelector('#details').hidden=true;}
  }
  showDetails(r) {
    const panel=document.querySelector('#details');panel.replaceChildren();panel.hidden=false;
    const close=element('button','×','close');close.setAttribute('aria-label','Close religion evidence');close.onclick=()=>{this.clear();panel.hidden=true;};
    panel.append(close,element('div',r.kind==='official'?'OFFICIAL RELIGION PROXY':'POPULATION MAJORITY OBSERVATION','eyebrow'),element('h2',r.name),element('p',r.summary),element('span','Confidence not assessed · source scope stated','badge'));
    if(r.share_percent)panel.append(element('p',`${r.share_percent}% in the cited observation`));
    for(const id of r.sources){const s=this.data.sources[id];panel.append(link(s.title,s.url),element('p',s.author),element('p',s.locator));}
    panel.append(element('p','Geometry: approximate dated Cliopatria polity boundaries, CC BY 4.0. A coloured area is a proxy attached to an entity, not a map of individual belief. No automatic 1945 change of meaning is used.'));
  }
}
