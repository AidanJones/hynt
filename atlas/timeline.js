export const MIN_YEAR = -10000;
export const MAX_YEAR = 2026;
export const ordinal = year => year < 0 ? year + 1 : year;
export const civil = value => value <= 0 ? value - 1 : value;
export const sliderValue = year => ordinal(year) - ordinal(MIN_YEAR);
export const sliderYear = value => civil(Number(value) + ordinal(MIN_YEAR));
export const formatYear = year => `${Math.abs(year).toLocaleString('en-GB')} ${year < 0 ? 'BCE' : 'CE'}`;
export const stepYear = (year, delta) => civil(Math.max(ordinal(MIN_YEAR), Math.min(ordinal(MAX_YEAR), ordinal(year) + delta)));
export function parseYear(text) {
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
  for (const year of [-10000,-6000,-3400,1,2026]) {
    const tick = document.createElement('span'); tick.textContent = formatYear(year);
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
      onYear(stepYear(current, delta));
      if (current >= MAX_YEAR) stop();
    }
    if (running) requestAnimationFrame(frame);
  }
  slider.addEventListener('input', () => {stop(); onYear(sliderYear(slider.value));});
  input.addEventListener('change', () => {
    const year = parseYear(input.value);
    input.setCustomValidity(year === null ? 'Enter a year from 10000 BCE to 2026 CE. There is no year zero.' : '');
    if (year === null) input.reportValidity();
    else {stop(); onYear(year);}
  });
  input.addEventListener('input', () => input.setCustomValidity(''));
  input.addEventListener('keydown', event => {if (event.key === 'Enter') {input.dispatchEvent(new Event('change')); input.blur();}});
  document.querySelector('#previous').onclick = () => {stop(); onYear(stepYear(current, -1));};
  document.querySelector('#next').onclick = () => {stop(); onYear(stepYear(current, 1));};
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
      current = year; slider.value = sliderValue(year); input.value = formatYear(year);
      slider.setAttribute('aria-valuetext', formatYear(year));
      document.querySelector('#year-output').textContent = formatYear(year);
    },
  };
}
