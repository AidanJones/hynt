import {element, link} from './panel.js';
import {formatYear} from './timeline.js';

// Chunk membership is an index of evidence/model provenance, never a literacy rate.
export function coverageRows(data, technologies, year, packageID, mode='evidence') {
  const records=new Map(technologies.attestations.filter(a=>a.package===packageID).map(a=>[a.id,a]));
  const direct=new Map(), inferred=new Map();
  for(const item of data.direct) {
    const a=records.get(item.attestation);
    if(a&&a.date_from<=year) {
      if(!direct.has(item.cell))direct.set(item.cell,[]);
      direct.get(item.cell).push(a);
    }
  }
  if(mode==='polity')for(const item of data.inferred) {
    if(!records.has(item.attestation)||item.year>year)continue;
    for(const id of item.cells) {
      if(!inferred.has(id))inferred.set(id,[]);
      inferred.get(id).push(item);
    }
  }
  return data.cells.features.map(cell=>{
    const evidence=(direct.get(cell.id)||[]).sort((a,b)=>a.date_from-b.date_from||a.date_to-b.date_to||a.id.localeCompare(b.id));
    const assumptions=(inferred.get(cell.id)||[]).sort((a,b)=>a.year-b.year||a.attestation.localeCompare(b.attestation)||a.polity.id.localeCompare(b.polity.id));
    const first=evidence[0], model=assumptions[0];
    return {cell,evidence,assumptions,first,model,
      status:first?(year<first.date_to?'window':'direct'):model?'inferred':'unknown'};
  });
}

export class TechnologyRegions {
  constructor(map,data,technologies,onEvidence,onSelect) {
    this.map=map;this.data=data;this.technologies=technologies;this.onEvidence=onEvidence;this.onSelect=onSelect;
    this.limit=24;this.selected=null;
    map.addSource('technology-regions',{type:'geojson',data:{type:'FeatureCollection',features:[]}});
    const hatch=new Uint8Array(8*8*4);
    for(let y=0;y<8;y++)for(let x=0;x<8;x++)if((x+y)%8<2)hatch.set([96,66,30,150],(y*8+x)*4);
    map.addImage('technology-inference-hatch',{width:8,height:8,data:hatch});
    map.addLayer({id:'technology-region-fill',type:'fill',source:'technology-regions',paint:{
      'fill-color':['match',['get','status'],'direct','#427b68','window','#79a99b','inferred','#bf9147','#a2aba4'],
      'fill-opacity':['match',['get','status'],'unknown',0.14,0.58]}},'polity-line');
    map.addLayer({id:'technology-region-inference',type:'fill',source:'technology-regions',filter:['==',['get','status'],'inferred'],paint:{'fill-pattern':'technology-inference-hatch','fill-opacity':0.6}},'polity-line');
    map.addLayer({id:'technology-region-line',type:'line',source:'technology-regions',paint:{
      'line-color':['match',['get','status'],'inferred','#885d27','unknown','#79877d','#315e4f'],
      'line-width':0.8,'line-dasharray':[2,2]}},'polity-line');
    map.on('click','technology-region-fill',event=>{
      const row=this.rows?.find(r=>r.cell.id===event.features[0]?.properties.id);
      if(row){this.onSelect();this.showDetails(row.cell.id);}
    });
    for(const id of ['technology-area','technology-research'])document.querySelector(`#${id}`).addEventListener('input',()=>{this.limit=24;this.renderList();});
    document.querySelector('#technology-more').onclick=()=>{this.limit+=24;this.renderList();};
  }
  update(state) {
    this.state=state;
    const enabled=state.technology&&state.technologyCoverage!=='off'&&state.technologyPackage!=='all';
    document.querySelector('#technology-regional-controls').hidden=!enabled;
    document.querySelector('#technology-regional-hint').hidden=!state.technology||state.technologyCoverage==='off'||state.technologyPackage!=='all';
    if(!enabled) {
      if(this.key!==null){this.map.getSource('technology-regions').setData({type:'FeatureCollection',features:[]});this.key=null;}
      if(this.selected)document.querySelector('#details').hidden=true;
      this.selected=null;return;
    }
    this.rows=coverageRows(this.data,this.technologies,state.year,state.technologyPackage,state.technologyCoverage);
    const key=JSON.stringify([state.technologyPackage,state.technologyCoverage,this.rows.map(r=>[r.status,r.first?.id,r.model?.attestation,r.evidence.length,r.assumptions.length])]);
    if(key!==this.key) {
      this.key=key;
      this.map.getSource('technology-regions').setData({type:'FeatureCollection',features:this.rows.map(r=>({...r.cell,properties:{...r.cell.properties,status:r.status}}))});
      this.renderList();
    }
    if(this.selected)this.showDetails(this.selected);
  }
  renderList() {
    if(!this.rows)return;
    const query=document.querySelector('#technology-area').value.toLocaleLowerCase().trim();
    const filter=document.querySelector('#technology-research').value;
    const rows=this.rows.filter(r=>(!query||r.cell.properties.name.toLocaleLowerCase().includes(query))
      &&(filter==='all'||(filter==='direct'?['direct','window'].includes(r.status):r.status===filter)))
      .sort((a,b)=>({direct:0,window:0,inferred:1,unknown:2}[a.status]-{direct:0,window:0,inferred:1,unknown:2}[b.status])
        ||(a.first?.date_from??a.model?.year??Infinity)-(b.first?.date_from??b.model?.year??Infinity)
        ||a.cell.properties.name.localeCompare(b.cell.properties.name));
    const list=document.querySelector('#technology-region-list');list.replaceChildren();
    const counts={direct:0,window:0,inferred:0,unknown:0};this.rows.forEach(r=>counts[r.status]++);
    document.querySelector('#technology-region-count').textContent=`${counts.direct+counts.window} evidence chunks · ${counts.inferred} inferred only · ${counts.unknown} without coverage in this selection`;
    for(const row of rows.slice(0,this.limit)) {
      const button=element('button',undefined,'technology-region-stop');button.dataset.cell=row.cell.id;
      const label=row.first?`Earliest selected evidence: ${row.first.date_label}`:row.model?`Modelled from ${formatYear(row.model.year)}`:'No evidence entered by this year';
      button.append(element('span',row.cell.properties.name),element('small',label));
      button.onclick=()=>{
        this.onSelect();this.showDetails(row.cell.id);
        const [w,s,e,n]=row.cell.properties.bounds;
        this.map.fitBounds([[w,s],[e,n]],{padding:innerWidth>650?{left:330,right:350,top:120,bottom:250}:45,maxZoom:5,duration:0});
      };
      list.append(button);
    }
    if(!rows.length)list.append(element('p','No chunks match this filter.'));
    const more=document.querySelector('#technology-more');more.hidden=rows.length<=this.limit;
    more.textContent=`Show more chunks (${Math.min(this.limit,rows.length)} of ${rows.length})`;
  }
  clear() {this.selected=null;}
  showDetails(id) {
    const row=this.rows.find(r=>r.cell.id===id);if(!row)return;
    this.selected=id;
    const panel=document.querySelector('#details');panel.replaceChildren();panel.hidden=false;
    const close=element('button','×','close');close.setAttribute('aria-label','Close regional technology details');
    close.onclick=()=>{this.selected=null;panel.hidden=true;};
    const p=this.technologies.packages.find(p=>p.id===this.state.technologyPackage);
    panel.append(close,element('div','REGIONAL TECHNOLOGY COVERAGE','eyebrow'),element('h2',row.cell.properties.name),element('p',p.name));
    panel.append(element('p','Five-degree geographic reporting chunk, clipped to present-day land. It is not a historical region or a claim of uniform use. Earliest means earliest in this researched selection; new finds or sources can move the date earlier.'));
    if(row.first) {
      panel.append(element('h3','Earliest selected evidence in this chunk'),element('p',row.first.date_label));
      if(this.state.year<row.first.date_to)panel.append(element('p','The selected year is inside this evidence date window. Polity inference waits until its latest endpoint.'));
      for(const a of row.evidence) {
        const button=element('button',`${a.name} · ${a.date_label} ↗`);
        button.onclick=()=>{this.clear();this.onEvidence(a);};panel.append(button);
        for(const sid of a.sources){const source=this.technologies.sources[sid];panel.append(link(source.title,source.url));}
      }
    } else panel.append(element('h3','No direct evidence entered by this year'),element('p','This is a gap in our selection, not evidence that people lacked this technology.'));
    if(row.assumptions.length) {
      panel.append(element('h3','Optional polity assumption'),element('p','The model assigns all land chunks overlapping a polity that contains an evidence anchor at the latest endpoint of its date window. Any overlap can mark a whole chunk, including land outside that polity. Coverage is retained going forward as a hypothesis; it does not prove continued use. Later conquests and inferred chunks do not seed further spread. Overlapping polity candidates are retained, not silently resolved.'));
      for(const model of row.assumptions) {
        const a=this.technologies.attestations.find(a=>a.id===model.attestation);
        panel.append(element('h4',`${model.polity.name} · ${formatYear(model.year)}`),element('p',`Seed: ${a.name} · ${a.date_label}. Polity record: ${model.polity.id}.`));
        const button=element('button','Read the seed evidence & sources ↗');button.onclick=()=>{this.clear();this.onEvidence(a);};panel.append(button);
      }
      panel.append(link('Polity geometry · Cliopatria / Seshat · CC BY 4.0',`https://github.com/Seshat-Global-History-Databank/cliopatria/tree/${this.data.polity_revision}`));
    }
    panel.append(element('h3','Research this chunk'),element('p','Search results are research leads. Check dates, object provenance and whether the claim concerns use, manufacture or invention before adding evidence. A modelled chunk can still benefit from direct research.'));
    const terms=`${p.name} earliest evidence ${row.cell.properties.region}`;
    panel.append(link('Search Wikipedia',`https://en.wikipedia.org/w/index.php?search=${encodeURIComponent(terms)}`),link('Search the web',`https://www.google.com/search?q=${encodeURIComponent(terms)}`));
  }
}
