import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validBounds,geometryIntersectsBounds} from '../atlas/spatial.js';
import {rankingAt} from '../atlas/ranking.js';
import {readState,serializeState} from '../atlas/state.js';
test('spatial windows handle enclosing polygons, contained shapes, crossings and holes',()=>{
  const outer=[[0,0],[10,0],[10,10],[0,10],[0,0]],hole=[[3,3],[7,3],[7,7],[3,7],[3,3]];
  const p={type:'Polygon',coordinates:[outer,hole]};
  assert.equal(geometryIntersectsBounds(p,[4,4,6,6]),false);
  assert.equal(geometryIntersectsBounds(p,[1,1,2,2]),true);
  assert.equal(geometryIntersectsBounds(p,[-1,-1,11,11]),true);
  assert.equal(geometryIntersectsBounds(p,[9,4,12,6]),true);
  assert.equal(geometryIntersectsBounds(p,[11,11,12,12]),false);
  assert.equal(validBounds([170,0,-170,10]),false);
});
test('ranking excludes unsupported years and maps source identities at change points',()=>{
  const d=JSON.parse(readFileSync(new URL('../atlas/data/influence.json',import.meta.url)));
  assert.equal(rankingAt(d,2026),null);
  const row=rankingAt(d,117);assert.ok(row[0]<=117&&117<row[1]);
  assert.ok(row[2].some(([i])=>d.entities[i].name.includes('Roman')));
  assert.ok(row[2].every((r,i)=>i===0||row[2][i-1][1]>=r[1]));
});
test('spatial window, confidence and rankings round-trip and invalid bounds are ignored',()=>{
  const s={...readState('#y=117'),bounds:[-5,50,2,56],confidence:'unknown',ranking:true};
  assert.deepEqual(readState(serializeState(s)),s);
  assert.equal(readState('#box=5,0,-5,10').bounds,null);
});
