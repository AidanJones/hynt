import test from 'node:test';
import assert from 'node:assert/strict';
import {parseYear, sliderValue, sliderYear, stepYear, stepTimeline, YEARS, MIN_YEAR, MAX_YEAR} from '../atlas/timeline.js';
import {bpToCivil} from '../atlas/chronology.js';
import {readState, serializeState} from '../atlas/state.js';

test('every civil year round-trips through a contiguous slider with no zero', () => {
  for (let year = MIN_YEAR; year <= MAX_YEAR; year++) {
    if (year === 0) continue;
    assert.equal(sliderYear(sliderValue(year)), year);
  }
  assert.equal(sliderYear(sliderValue(-1) + 1), 1);
  assert.equal(stepYear(-1, 1), 1);
  assert.equal(stepYear(1, -1), -1);
  assert.equal(stepYear(MAX_YEAR, 100), MAX_YEAR);
});
test('year parsing accepts eras and rejects invalid input', () => {
  for (const [text, expected] of [['300 BCE', -300], ['1066',1066], ['1 BC',-1], ['2,026 CE',2026], ['-31',-31]]) assert.equal(parseYear(text), expected);
  assert.equal(parseYear('55000 BP'),bpToCivil(55000));
  assert.equal(parseYear('55000 ya'),-52975);
  for (const text of ['0','0 BCE','2027','-300001','300001 BP','hello','1.5']) assert.equal(parseYear(text), null);
});
test('share state round-trips layers, focus, camera and civil year', () => {
  const state = {year:-1, polity:false, technology:true, technologyPackage:'algebra', technologyMode:'window',technologyCoverage:'polity', britain:true, britainKind:'ruler',britainMode:'window',migration:false,migrationStory:'all', focus:'Q12544', camera:[12.5,41.9,4]};
  assert.deepEqual(readState(serializeState(state)), {...readState('#'),...state});
  const invalid = readState('#y=0&c=NaN,91,90&l=nonsense');
  assert.equal(invalid.year,117); assert.deepEqual(invalid.camera,[22,24,1.8]); assert.equal(invalid.polity,false);
});
test('piecewise steps are continuous at joins and annual in recorded history',()=>{
  assert.equal(MIN_YEAR,bpToCivil(300000));
  assert.equal(stepTimeline(bpToCivil(100000),1),bpToCivil(99000));
  assert.equal(stepTimeline(-3400,1),-3399);
  assert.equal(stepTimeline(-1,1),1);
  assert.ok(YEARS.every((year,index)=>year!==0&&(index===0||year>YEARS[index-1])));
  assert.equal(sliderYear(sliderValue(bpToCivil(12000))),bpToCivil(12000));
});
