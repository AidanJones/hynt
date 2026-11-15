import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {visibleAttestations, visibleTransmissions} from '../atlas/technology.js';
import {readState, serializeState} from '../atlas/state.js';
const data = JSON.parse(readFileSync(new URL('../atlas/data/technologies.json', import.meta.url)));
test('evidence accumulates without leaking future attestations', () => {
  assert.equal(visibleAttestations(data, -10000).length, 0);
  assert.equal(visibleAttestations(data, -9000, 'farming').length, 1);
  assert.equal(visibleAttestations(data, 819, 'algebra').length, 0);
  assert.equal(visibleAttestations(data, 825, 'algebra').length, 1);
  assert.equal(visibleAttestations(data, 1145, 'algebra').length, 2);
  assert.equal(visibleAttestations(data, 2026, 'algebra', 'window').length, 0);
  assert.equal(visibleAttestations(data, 825, 'algebra', 'window').length, 1);
});
test('connections appear only when both endpoints and destination date are attested', () => {
  const before = visibleAttestations(data, 1144, 'algebra');
  assert.equal(visibleTransmissions(data,before,1144).length,0);
  assert.equal(visibleTransmissions(data,visibleAttestations(data,1145,'algebra'),1145).length,1);
  assert.equal(visibleTransmissions(data,visibleAttestations(data,1475,'printing'),1475).length,0);
  assert.equal(visibleTransmissions(data,visibleAttestations(data,1476,'printing'),1476).length,1);
  assert.ok(!data.transmissions.some(t => t.origin === 'printing-cheongju'));
});
test('technology view and deep date survive a share link; old links stay valid', () => {
  const state = {...readState(''), year:-9000, technology:true, technologyPackage:'farming'};
  assert.deepEqual(readState(serializeState(state)),state);
  const old = readState('#y=117&l=polity');
  assert.equal(old.year,117); assert.equal(old.technology,false);
});
