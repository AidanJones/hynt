import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activeCultures} from '../atlas/cultures.js';
import {readState,serializeState} from '../atlas/state.js';
const data=JSON.parse(readFileSync(new URL('../atlas/data/cultures.json',import.meta.url)));
test('culture snapshots change at half-open boundaries and end at import coverage',()=>{
  assert.equal(activeCultures(data,-10001).length,0);
  assert.equal(activeCultures(data,-8000)[0].id,'jomon-8000');
  assert.equal(activeCultures(data,-5000).length,3);
  assert.equal(activeCultures(data,-4000).length,1);
  assert.equal(activeCultures(data,-3400).length,0);
  assert.equal(activeCultures(data,-5000,'culture:narva').length,1);
});
test('culture state round-trips and invalid traditions are ignored',()=>{
  const state={...readState('#y=-5000'),cultures:true,cultureKind:'culture:ubaid'};
  assert.deepEqual(readState(serializeState(state)),state);
  assert.equal(readState('#culture=unsupported').cultureKind,'all');
});
