import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {visibleBritishRecords} from '../atlas/britain.js';
import {readState,serializeState} from '../atlas/state.js';
const data = JSON.parse(readFileSync(new URL('../atlas/data/britain.json',import.meta.url)));
test('British evidence stays distinct from a continuous reign or occupation',() => {
  assert.equal(visibleBritishRecords(data,-5000).length,0);
  assert.ok(visibleBritishRecords(data,-700,'all','window').some(r=>r.id==='llyn-fawr'));
  assert.ok(!visibleBritishRecords(data,-500,'all','window').some(r=>r.id==='llyn-fawr'));
  assert.equal(visibleBritishRecords(data,-500,'ruler').length,0);
  assert.ok(visibleBritishRecords(data,-10,'ruler','window').some(r=>r.id==='tasciovanus'));
  assert.ok(!visibleBritishRecords(data,50,'ruler').some(r=>r.id==='caratacus'));
  assert.ok(visibleBritishRecords(data,51,'ruler','window').some(r=>r.id==='caratacus'));
  assert.equal(visibleBritishRecords(data,2026,'all','window').length,0);
});
test('British layer and filters round-trip while old URLs remain valid',()=>{
  const state = {...readState(''),year:51,britain:true,britainKind:'ruler',britainMode:'window'};
  assert.deepEqual(readState(serializeState(state)),state);
  assert.equal(readState('#y=51&l=polity').britain,false);
  assert.equal(readState('#bk=made-up&bm=made-up').britainKind,'all');
});
