import test from 'node:test';
import assert from 'node:assert/strict';
import {migrationProgress,routePrefix} from '../atlas/migrations.js';
import {readState,serializeState} from '../atlas/state.js';
test('route progress clamps before and after its window and crosses BCE/CE without zero',()=>{
  const record={date_from:-1,date_to:2};
  assert.equal(migrationProgress(record,-2),0);
  assert.equal(migrationProgress(record,1),0.5);
  assert.equal(migrationProgress(record,3),1);
  assert.deepEqual(routePrefix([[0,0],[10,0],[10,10]],0.75),[[0,0],[10,0],[10,5]]);
  assert.deepEqual(routePrefix([[0,0],[1,1]],0),[]);
});
test('migration-only deep views round-trip URL state',()=>{
  const state={...readState(''),year:-58051,migration:true,migrationStory:'later-out-of-africa'};
  assert.deepEqual(readState(serializeState(state)),state);
});
