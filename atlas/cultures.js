import {element,link} from './panel.js';
import {formatYear} from './timeline.js';
export function activeCultures(data,year,entity='all') {
  return data.features.filter(f=>f.properties.from<=year&&year<f.properties.to&&(entity==='all'||f.properties.entity===entity));
}
export class CultureLayer {
  constructor(map,data,onSelect) {
    this.map=map;this.data=data;this.onSelect=onSelect;this.selected=null;
    map.addSource('cultures',{type:'geojson',data,attribution:'<a href="https://github.com/aourednik/historical-basemaps">historical-basemaps</a> · GPL-3.0'});
    map.addLayer({id:'culture-fill',type:'fill',source:'cultures',paint:{'fill-color':['get','colour'],'fill-opacity':0.22}},'polity-fill');
    map.addLayer({id:'culture-line',type:'line',source:'cultures',paint:{'line-color':['get','colour'],'line-width':1.5,'line-dasharray':[2,2]}},'polity-fill');
    for(const [id,name] of new Map(data.features.map(f=>[f.properties.entity,f.properties.name.split(' · ')[0]]))) {
      const option=element('option',name);option.value=id;document.querySelector('#culture-kind').append(option);
    }
    map.on('click','culture-fill',event=>{
      const f=data.features.find(f=>f.properties.id===event.features[0]?.properties.id);if(f)this.select(f);
    });
  }
  clear(){this.selected=null;}
  select(feature,jump=false){this.onSelect(feature,jump);this.selected=feature;this.showDetails(feature);}
  update(state) {
    this.state=state;
    const filter=['all',['<=',['get','from'],state.year],['>',['get','to'],state.year]];
    if(state.cultureKind!=='all')filter.push(['==',['get','entity'],state.cultureKind]);
    const key=state.cultures?JSON.stringify([state.cultureKind,state.year]):'off';if(key===this.key)return;this.key=key;
    for(const id of ['culture-fill','culture-line']){this.map.setFilter(id,filter);this.map.setLayoutProperty(id,'visibility',state.cultures?'visible':'none');}
    const active=state.cultures?activeCultures(this.data,state.year,state.cultureKind):[];
    document.querySelector('#culture-count').textContent=`${active.length} selected reconstruction${active.length===1?'':'s'} · coverage 10,000–3400 BCE. Blank land is a data gap.`;
    const list=document.querySelector('#culture-list');list.replaceChildren();
    for(const f of this.data.features.filter(f=>state.cultureKind==='all'||f.properties.entity===state.cultureKind)) {
      const button=element('button',`${f.properties.name} · snapshot ${formatYear(f.properties.snapshot_year)}`,'britain-stop');
      button.onclick=()=>this.select(f,true);list.append(button);
    }
    if(this.selected&&(!state.cultures||!active.some(f=>f.id===this.selected.id))){this.clear();document.querySelector('#details').hidden=true;}
  }
  showDetails(feature) {
    const p=feature.properties,panel=document.querySelector('#details');panel.replaceChildren();panel.hidden=false;
    const close=element('button','×','close');close.setAttribute('aria-label','Close culture details');close.onclick=()=>{this.clear();panel.hidden=true;};
    panel.append(close,element('div','ARCHAEOLOGICAL CULTURE · RECONSTRUCTION','eyebrow'),element('h2',p.name),element('span','Boundary confidence not assessed','badge'));
    panel.append(element('p',`Source snapshot: ${formatYear(p.snapshot_year)}. Carried forward to before ${formatYear(p.to)} as a display assumption, not an observed unchanged border.`),element('p',p.summary));
    panel.append(element('p','These are selected material-culture interpretations. They do not define a uniform people, language, ancestry or state. Present-day coastlines provide orientation. Import coverage ending at 3400 BCE does not mean a culture ended then.'));
    panel.append(element('h3','Independent archaeological context'));
    for(const id of p.references){const s=this.data.references[id];panel.append(link(s.title,s.url),element('p',s.author),element('p',s.locator));}
    panel.append(element('h3','Polygon provenance & reuse'));
    panel.append(link('André Ourednik and contributors · historical-basemaps',`https://github.com/aourednik/historical-basemaps/tree/${this.data.revision}`),element('p',`Original feature index ${p.source_index}. Repaired/simplified at 0.01°. Upstream BORDERPRECISION=${p.source_properties.BORDERPRECISION}; this number is not converted into a confidence rating.`));
    for(const [text,url] of [['GPL-3.0 licence','data/cultures/LICENSE.txt'],['Corresponding source records','data/cultures/source.json'],['Selection and transformation recipe','https://github.com/AidanJones/hynt/blob/main/pipeline/cultures.py']]) {
      const a=element('a',text);a.href=url;panel.append(a,element('br'));
    }
  }
}
