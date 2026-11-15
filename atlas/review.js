import {element,link} from './panel.js';
import {formatYear} from './timeline.js';
let audit,entities,limit=30;
function render() {
  const kind=document.querySelector('#review-kind').value,query=document.querySelector('#review-search').value.toLocaleLowerCase();
  const names=new Map(entities.map(e=>[e.id,e]));
  const rows=kind==='aliases'?audit.aliases:kind==='temporal'?audit.same_entity_interval_overlaps:audit.samples.flatMap(s=>s.largest_overlaps.map(r=>({...r,year:s.year})));
  const selected=rows.filter(r=>JSON.stringify(r).toLocaleLowerCase().includes(query));
  const host=document.querySelector('#review-results');host.replaceChildren();
  document.querySelector('#review-count').textContent=`${selected.length} matching flags · ${audit.features.toLocaleString()} shapes, ${audit.entities.toLocaleString()} entities audited. Spatial rows are the largest pairs retained at ten sampled years, not all annual intersections.`;
  for(const r of selected.slice(0,limit)) {
    const article=element('article'),entity=names.get(r.entity),year=r.year??r.from??entity?.from??117;
    article.append(element('h2',r.names?r.names.join(' / '):r.a_name?`${r.a_name} / ${r.b_name}`:`${entity?.name||r.entity} · concurrent records`));
    article.append(element('p',r.names?`Entity ${r.entity}. A shared ID may represent an alias, composite polity or identity error; it is not automatically a safe merge.`:r.overlap_km2?`${formatYear(year)} · ${r.overlap_km2.toLocaleString()} km² of sampled planar intersection. ${r.same_entity?'Same entity.':'Distinct entities; aggregate/component overlap is possible.'}`:`${formatYear(r.from)} to before ${formatYear(r.to)}. Temporal concurrency alone does not establish duplicate geography.`));
    if(r.a)article.append(element('p',`${r.a} / ${r.b}`));
    const go=element('a','Inspect this year in the atlas ↗');go.href=`./#${new URLSearchParams({y:year,l:'polity',...(r.entity?{f:r.entity}:{})})}`;article.append(go);
    article.append(element('p','Review source interval precision, aggregate/component status, claimed versus effective control, and regional scholarship before editing. Preserve the original record IDs and write a cited crosswalk or interpretation note.'));
    host.append(article);
  }
  const more=document.querySelector('#review-more');more.hidden=selected.length<=limit;more.textContent=`Show more (${Math.min(limit,selected.length)} of ${selected.length})`;
}
Promise.all(['audit','entities'].map(f=>fetch(`data/${f}.json`).then(r=>{if(!r.ok)throw Error('Could not load audit data');return r.json();}))).then(([a,e])=>{
  audit=a;entities=e;render();
  for(const id of ['review-kind','review-search'])document.querySelector(`#${id}`).addEventListener('input',()=>{limit=30;render();});
  document.querySelector('#review-more').onclick=()=>{limit+=30;render();};
}).catch(e=>{document.querySelector('#error').textContent=e.message;});
