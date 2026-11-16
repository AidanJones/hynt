import {element,link} from './panel.js';
import {formatYear} from './timeline.js';
let audit,entities,evidence,limit=30;
function render() {
  const kind=document.querySelector('#review-kind').value,query=document.querySelector('#review-search').value.toLocaleLowerCase(),filter=document.querySelector('#review-filter').value;
  const names=new Map(entities.map(e=>[e.id,e]));
  const rows=kind==='references'?evidence.identities:kind==='aliases'?audit.aliases:kind==='temporal'?evidence.temporal:audit.samples.flatMap(s=>s.largest_overlaps.map(r=>({...r,year:s.year})));
  const selected=rows.filter(r=>JSON.stringify(r).toLocaleLowerCase().includes(query)&&(filter==='all'||[r.geometry_relation,r.status,r.decision].includes(filter)));
  const host=document.querySelector('#review-results');host.replaceChildren();
  document.querySelector('#review-count').textContent=`${selected.length} matching flags · ${audit.features.toLocaleString()} shapes, ${audit.entities.toLocaleString()} entities audited. Spatial rows are the largest pairs retained at ten sampled years, not all annual intersections.`;
  for(const r of selected.slice(0,limit)) {
    const article=element('article'),entity=names.get(r.current_entities?.[0]||r.entity),year=r.year??r.from??entity?.from??117;
    article.append(element('h2',r.article?`${r.name} · ${r.decision}`:r.names?r.names.join(' / '):r.a_name?`${r.a_name} / ${r.b_name}`:`${entity?.name||r.entity} · concurrent records`));
    if(r.article) {
      article.append(element('p',`Source ID ${r.entity}; cited article: ${r.article}. Article reference ID: ${r.qid||'unresolved'}. Current grouping: ${r.current_entities.join(', ')||'not found'}.`),element('p',r.reason));
      if(r.reference)article.append(link('Pinned article revision',r.reference));
      if(r.qid)article.append(element('br'),link('Canonical structured reference',`https://www.wikidata.org/wiki/${r.qid}`));
      if(r.review_reference)article.append(element('br'),link('Historical review reference',r.review_reference));
    }
    if(r.geometry_relation)article.append(element('p',`${r.geometry_relation} · ${r.civil_years} civil year${r.civil_years===1?'':'s'} of interval concurrency. Mechanical classification; historical control remains unadjudicated.`));
    if(!r.article)article.append(element('p',r.names?`Entity ${r.entity}. A shared ID may represent an alias, composite polity or identity error; it is not automatically a safe merge.`:r.overlap_km2?`${formatYear(year)} · ${r.overlap_km2.toLocaleString()} km² of sampled planar intersection. ${r.same_entity?'Same entity.':'Distinct entities; aggregate/component overlap is possible.'}`:`${formatYear(r.from)} to before ${formatYear(r.to)}. Temporal concurrency alone does not establish duplicate geography.`));
    if(r.a)article.append(element('p',`${r.a} / ${r.b}`));
    const go=element('a','Inspect this year in the atlas ↗');go.href=`./#${new URLSearchParams({y:year,l:'polity',...(entity?{f:entity.id}:{})})}`;article.append(go);
    article.append(element('p','Review source interval precision, aggregate/component status, claimed versus effective control, and regional scholarship before editing. Preserve the original record IDs and write a cited crosswalk or interpretation note.'));
    host.append(article);
  }
  const more=document.querySelector('#review-more');more.hidden=selected.length<=limit;more.textContent=`Show more (${Math.min(limit,selected.length)} of ${selected.length})`;
}
Promise.all(['audit','entities','review-evidence'].map(f=>fetch(`data/${f}.json`).then(r=>{if(!r.ok)throw Error('Could not load audit data');return r.json();}))).then(([a,e,r])=>{
  audit=a;entities=e;evidence=r;render();
  const requested=new URLSearchParams(location.search).get('entity');
  if(requested){document.querySelector('#review-search').value=requested;render();}
  for(const id of ['review-kind','review-search','review-filter'])document.querySelector(`#${id}`).addEventListener('input',()=>{limit=30;render();});
  document.querySelector('#review-more').onclick=()=>{limit+=30;render();};
}).catch(e=>{document.querySelector('#error').textContent=e.message;});
