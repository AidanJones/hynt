import {element} from './panel.js';
import {formatYear} from './timeline.js';
import {ordinal} from './chronology.js';
export function rankingAt(data,year) {
  let lo=0,hi=data.snapshots.length-1;
  while(lo<=hi){const mid=(lo+hi)>>1,row=data.snapshots[mid];if(year<row[0])hi=mid-1;else if(year>=row[1])lo=mid+1;else return row;}
  return null;
}
export class Ranking {
  constructor(data,onFocus,onYear) {this.data=data;this.onFocus=onFocus;this.onYear=onYear;}
  update(state) {
    document.querySelector('#ranking-explorer').hidden=!state.ranking;
    const row=rankingAt(this.data,state.year),key=JSON.stringify([state.ranking,row?.[0],state.focus]);
    if(key!==this.key){this.key=key;const list=document.querySelector('#ranking-list');list.replaceChildren();
      if(state.ranking)for(const [index,area] of row?.[2]||[]) {
        const entity=this.data.entities[index],button=element('button',undefined,'ranking-stop');
        button.classList.toggle('rank-focused',state.focus===entity.id);
        button.append(element('span',entity.name),element('strong',`${area.toLocaleString()} km²`));
        const bar=element('span',undefined,'ranking-bar');bar.style.width=`${100*area/row[2][0][1]}%`;button.append(bar);
        button.onclick=()=>this.onFocus(entity.id);list.append(button);
      }
      if(state.ranking&&!row?.[2].length)list.append(element('p','No ranked polity geometry for this year.'));
    }
    this.lifespan(state.focus,state.year);
  }
  lifespan(id,year) {
    const host=document.querySelector('#entity-lifespan');
    if(this.historyKey===`${id}:${year}`)return;this.historyKey=`${id}:${year}`;
    host.replaceChildren();host.hidden=!id;if(!id)return;
    const index=this.data.entities.findIndex(e=>e.id===id),rows=this.data.history[index]||[];
    if(!rows.length){host.append(element('p','No extent history for this entity.'));return;}
    const start=rows[0][0],end=rows.at(-1)[1],maximum=Math.max(...rows.map(r=>r[2]));
    host.append(element('h3',this.data.entities[index].name),element('p',`${formatYear(start)} to before ${formatYear(end)} · recorded geometry intervals`));
    const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 240 80');svg.setAttribute('role','img');svg.setAttribute('aria-label','Territorial extent history; gaps are missing observations');
    const x=y=>5+230*(ordinal(y)-ordinal(start))/(ordinal(end)-ordinal(start)),v=a=>75-65*a/maximum;
    for(const [from,to,area] of rows){const line=document.createElementNS(ns,'path');line.setAttribute('d',`M${x(from)} ${v(area)}H${x(to)}`);line.setAttribute('stroke','#5a786a');line.setAttribute('stroke-width','2');svg.append(line);}
    if(start<=year&&year<end){const line=document.createElementNS(ns,'path');line.setAttribute('d',`M${x(year)} 5V78`);line.setAttribute('stroke','#b25737');svg.append(line);}
    host.append(svg,element('p',`Peak mapped extent ${maximum.toLocaleString()} km². Gaps remain gaps; aliases and composite empires follow source identity.`));
    const jump=element('button','Jump to first recorded year ↗');jump.onclick=()=>this.onYear(start);host.append(jump);
  }
}
