import {ordinal,civil,bpToCivil,civilToBP} from './chronology.js';
export {ordinal,civil};
export const MIN_YEAR = bpToCivil(300000);
export const MAX_YEAR = 2026;
export const YEARS = [];
for (let bp=300000;bp>=12000;bp-=1000) YEARS.push(bpToCivil(bp));
for (let year=YEARS.at(-1)+50;year<-3400;year+=50) YEARS.push(year);
for (let year=-3400;year<=MAX_YEAR;year++) if (year!==0) YEARS.push(year);
export function sliderValue(year) {
  let low=0,high=YEARS.length-1;
  while(low<high) {const mid=Math.ceil((low+high)/2); if(YEARS[mid]<=year) low=mid; else high=mid-1;}
  if (low===YEARS.length-1 || YEARS[low]===year) return low;
  return low+(ordinal(year)-ordinal(YEARS[low]))/(ordinal(YEARS[low+1])-ordinal(YEARS[low]));
}
export function sliderYear(value) {
  const position=Math.max(0,Math.min(YEARS.length-1,Number(value))), index=Math.floor(position);
  if (index===YEARS.length-1) return MAX_YEAR;
  return civil(Math.round(ordinal(YEARS[index])+(position-index)*(ordinal(YEARS[index+1])-ordinal(YEARS[index]))));
}
export const formatYear = year => year<=-10000 ? `${civilToBP(year).toLocaleString('en-GB')} BP` : `${Math.abs(year).toLocaleString('en-GB')} ${year < 0 ? 'BCE' : 'CE'}`;
export const stepYear = (year, delta) => civil(Math.max(ordinal(MIN_YEAR), Math.min(ordinal(MAX_YEAR), ordinal(year) + delta)));
export const stepTimeline = (year,direction) => YEARS[Math.max(0,Math.min(YEARS.length-1,direction>0 ? Math.floor(sliderValue(year))+direction : Math.ceil(sliderValue(year))+direction))];
export function parseYear(text) {
  const age=String(text).trim().replaceAll(',','').match(/^(\d+)\s*(?:cal\s*)?(BP|ya)$/i);
  if (age) {
    const bp=Number(age[1]), year=age[2].toLowerCase()==='ya' ? civil(2026-bp) : bpToCivil(bp);
    return Number.isSafeInteger(bp)&&year>=MIN_YEAR&&year<=MAX_YEAR ? year : null;
  }
  const match = String(text).trim().replaceAll(',', '').match(/^(-?\d+)\s*(BCE|BC|CE|AD)?$/i);
  if (!match) return null;
  let year = Number(match[1]);
  if (/^BC/i.test(match[2] || '')) year = -Math.abs(year);
  if (!Number.isSafeInteger(year) || year === 0 || year < MIN_YEAR || year > MAX_YEAR) return null;
  return year;
}

export function bindTimeline(onYear) {
  const slider = document.querySelector('#year-slider');
  const input = document.querySelector('#year-input');
  const play = document.querySelector('#play');
  const speed = document.querySelector('#speed');
  let current = 117, running = false, last = 0, accumulated = 0;
  slider.max = sliderValue(MAX_YEAR);
  const ticks = document.querySelector('.ticks'); ticks.replaceChildren();
  for (const year of [MIN_YEAR,-3400,1,2026]) {
    const tick = document.createElement('span'); tick.textContent = year===MIN_YEAR ? '300k BP' : formatYear(year);
    tick.style.left = `${100 * sliderValue(year) / sliderValue(MAX_YEAR)}%`;
    ticks.append(tick);
  }
  function stop() {
    running = false; play.textContent = '▶'; play.setAttribute('aria-label', 'Play timeline');
  }
  function frame(now) {
    if (!running) return;
    accumulated += Math.min(now - last, 250) * Number(speed.value) / 1000;
    last = now;
    if (accumulated >= 1) {
      const delta = Math.floor(accumulated); accumulated -= delta;
      onYear(current<-3400 ? stepTimeline(current,delta) : stepYear(current, delta));
      if (current >= MAX_YEAR) stop();
    }
    if (running) requestAnimationFrame(frame);
  }
  slider.addEventListener('input', () => {stop(); onYear(sliderYear(slider.value));});
  input.addEventListener('change', () => {
    const year = parseYear(input.value);
    input.setCustomValidity(year === null ? 'Enter BCE/CE, BP (before 1950 CE), or ya (before 2026 CE), within 300,000 BP–2026 CE. No year zero.' : '');
    if (year === null) input.reportValidity();
    else {stop(); onYear(year);}
  });
  input.addEventListener('input', () => input.setCustomValidity(''));
  input.addEventListener('keydown', event => {if (event.key === 'Enter') {input.dispatchEvent(new Event('change')); input.blur();}});
  document.querySelector('#previous').onclick = () => {stop(); onYear(stepTimeline(current, -1));};
  document.querySelector('#next').onclick = () => {stop(); onYear(stepTimeline(current, 1));};
  document.querySelectorAll('[data-year]').forEach(button => button.onclick = () => {stop(); onYear(Number(button.dataset.year));});
  play.onclick = () => {
    if (running) {stop(); return;}
    if (current === MAX_YEAR) onYear(MIN_YEAR);
    running = true; last = performance.now(); accumulated = 0;
    play.textContent = 'Ⅱ'; play.setAttribute('aria-label', 'Pause timeline'); requestAnimationFrame(frame);
  };
  document.addEventListener('visibilitychange', () => {if (document.hidden) stop();});
  return {
    stop,
    update(year) {
      for(const option of speed.options)option.textContent=`${option.value} ${year<-3400?'steps':'years'} / sec`;
      current = year; slider.value = sliderValue(year); input.value = formatYear(year);
      slider.setAttribute('aria-valuetext', formatYear(year));
      document.querySelector('#year-output').textContent = formatYear(year);
    },
  };
}
