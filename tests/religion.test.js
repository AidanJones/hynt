import test from 'node:test';
import assert from 'node:assert/strict';
import {religionFeatures} from '../atlas/religion.js';
import {readState,serializeState} from '../atlas/state.js';
test('religion proxy respects entity, time and evidence type',()=>{
  const c={features:[{properties:{id:'one',entity:'Q1',from:700,to:800},geometry:{type:'Polygon',coordinates:[]}}]};
  const d={records:[{id:'official',entity:'Q1',from:700,to:751,kind:'official',religion:'A',colour:'#111111'},
    {id:'majority',entity:'Q1',from:750,to:751,kind:'majority',religion:'B',colour:'#222222'}]};
  assert.equal(religionFeatures(c,d,750,'official').features[0].properties.religion,'A');
  assert.equal(religionFeatures(c,d,750,'majority').features[0].properties.religion,'B');
  assert.equal(religionFeatures(c,d,751,'majority').features.length,0);
  const s={...readState('#y=750'),religion:true,religionKind:'majority',compareReligion:true};
  assert.deepEqual(readState(serializeState(s)),s);
});
