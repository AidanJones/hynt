import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {coverageRows} from '../atlas/technology-regions.js';
import {readState,serializeState} from '../atlas/state.js';
const data=JSON.parse(readFileSync(new URL('../atlas/data/technology-regions.json',import.meta.url)));
const tech=JSON.parse(readFileSync(new URL('../atlas/data/technologies.json',import.meta.url)));

test('regional writing retains pre-Roman evidence and date uncertainty',()=>{
  const id=data.direct.find(a=>a.attestation==='writing-commius').cell;
  const row=year=>coverageRows(data,tech,year,'writing').find(r=>r.cell.id===id);
  assert.equal(row(-41).status,'unknown');
  assert.equal(row(-30).status,'window');
  assert.equal(row(-25).status,'direct');
  assert.equal(row(2026).first.id,'writing-commius');
});
test('polity assumption is optional, starts at latest date and persists without new conquests',()=>{
  const model=data.inferred.find(m=>m.attestation==='writing-bloomberg'&&m.cells.some(id=>!data.direct.some(d=>d.cell===id&&tech.attestations.find(a=>a.id===d.attestation)?.package==='writing')));
  assert.ok(model);
  const id=model.cells.find(id=>!data.direct.some(d=>d.cell===id&&tech.attestations.find(a=>a.id===d.attestation)?.package==='writing'));
  const row=(year,mode)=>coverageRows(data,tech,year,'writing',mode).find(r=>r.cell.id===id);
  assert.equal(row(2026,'evidence').status,'unknown');
  assert.ok(!row(model.year-1,'polity').assumptions.some(m=>m.attestation==='writing-bloomberg'));
  assert.ok(row(model.year,'polity').assumptions.some(m=>m.attestation==='writing-bloomberg'));
  assert.equal(row(2026,'polity').status,'inferred');
});
test('all coverage modes and old links round-trip safely',()=>{
  for(const mode of ['off','evidence','polity']) {
    const state={...readState('#y=117'),technologyCoverage:mode};
    assert.equal(readState(serializeState(state)).technologyCoverage,mode);
  }
  assert.equal(readState('#y=117&tc=bad').technologyCoverage,'evidence');
});
