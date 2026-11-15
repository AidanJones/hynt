import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {dayOfYear,campaignPrefix,activeEvents} from '../atlas/events.js';
import {readState,serializeState} from '../atlas/state.js';
const data=JSON.parse(readFileSync(new URL('../atlas/data/events.json',import.meta.url)));
test('campaign progress respects each independent waypoint date',()=>{
  const c=data.campaigns[0],first=c.waypoints[0],last=c.waypoints.at(-1);
  assert.deepEqual(campaignPrefix(c,dayOfYear(first.date)-1),[]);
  assert.deepEqual(campaignPrefix(c,dayOfYear(first.date)),[first.coordinates]);
  assert.deepEqual(campaignPrefix(c,dayOfYear(c.waypoints[1].date)).at(-1),c.waypoints[1].coordinates);
  assert.deepEqual(campaignPrefix(c,dayOfYear(last.date)),c.waypoints.map(w=>w.coordinates));
});
test('1066 events obey category and intra-year date without leaking to adjacent years',()=>{
  const s={events:true,year:1066,eventCategory:'battle',campaignDay:dayOfYear('1066-09-25')};
  assert.deepEqual(activeEvents(data,s).map(e=>e.id),['fulford','stamford-bridge']);
  assert.equal(activeEvents(data,{...s,year:1067}).length,0);
  const round=readState(serializeState({...readState('#y=1066'),...s}));
  assert.equal(round.campaignDay,s.campaignDay);assert.equal(round.events,true);
});
